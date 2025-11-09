import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

from ray import serve


NODE_REAPER_DEPLOYMENT_NAME = "NodeReaper"


@serve.deployment
class NodeReaper:
    def __init__(
        self,
        ssh_user: str,
        ssh_private_key: str,
        retention_seconds: int = 900,
        reap_interval_seconds: int = 60,
    ):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ssh_user = ssh_user
        key_path = Path(ssh_private_key).expanduser()
        if not key_path.exists():
            raise FileNotFoundError(f"SSH private key not found: {key_path}")
        self.ssh_private_key = key_path.as_posix()
        self.retention_seconds = retention_seconds
        self.reap_interval_seconds = max(30, reap_interval_seconds)

        self._unhealthy_replicas: Dict[str, Dict[str, Any]] = {}
        self._nodes_marked_for_reap: Dict[str, float] = {}
        self._nodes_inflight: Set[str] = set()

        loop = asyncio.get_event_loop()
        self._reaper_task = loop.create_task(self._reap_loop())
        self.logger.info("NodeReaper initialized; monitoring unhealthy nodes for recycling")

    def __del__(self):
        if hasattr(self, "_reaper_task") and self._reaper_task and not self._reaper_task.done():
            self._reaper_task.cancel()
    
    def report_failure(self, replica_id: str, node_ip: str, error: Optional[str] = None):
        self._unhealthy_replicas[replica_id] = {
            "node_ip": node_ip,
            "error": error,
            "timestamp": time.time(),
        }
        self._nodes_marked_for_reap[node_ip] = self._nodes_marked_for_reap.get(node_ip, time.time())
        self.logger.warning(f"Replica {replica_id} on {node_ip} marked for reaping: {error}")
        self._purge_stale()

    def get_unhealthy_node_ips(self) -> List[str]:
        self._purge_stale()
        return list(self._nodes_marked_for_reap.keys())
    
    async def _reap_loop(self):
        while True:
            try:
                await asyncio.sleep(self.reap_interval_seconds)
                await self._reap_pending_nodes()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.warning(f"Unexpected error in reap loop: {exc}")

    async def _reap_pending_nodes(self):
        nodes = self.get_unhealthy_node_ips()
        for node_ip in nodes:
            if node_ip in self._nodes_inflight:
                continue
            self._nodes_inflight.add(node_ip)
            try:
                await self._reap_node(node_ip)
                self._clear_node(node_ip)
                self.logger.info(f"Successfully reaped node {node_ip}")
            except Exception as exc:
                self.logger.error(f"Failed to reap node {node_ip}: {exc}")
            finally:
                self._nodes_inflight.discard(node_ip)

    async def _reap_node(self, node_ip: str):
        ssh_command = [
            "ssh",
            "-i",
            self.ssh_private_key,
            "-o",
            "StrictHostKeyChecking=no",
            f"{self.ssh_user}@{node_ip}",
            "docker stop ray_container",
        ]

        self.logger.info(f"Reaping node {node_ip} via SSH")
        process = await asyncio.create_subprocess_exec(
            *ssh_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            stdout_text = stdout.decode().strip()
            stderr_text = stderr.decode().strip()
            raise RuntimeError(
                f"SSH command failed with code {process.returncode}. stdout={stdout_text} stderr={stderr_text}"
            )

    def _clear_node(self, node_ip: str):
        to_delete = [replica for replica, data in self._unhealthy_replicas.items() if data.get("node_ip") == node_ip]
        for replica in to_delete:
            self._unhealthy_replicas.pop(replica, None)
        self._nodes_marked_for_reap.pop(node_ip, None)

    def _purge_stale(self):
        if not self.retention_seconds:
            return
        cutoff = time.time() - self.retention_seconds
        replica_ids = [replica_id for replica_id, data in self._unhealthy_replicas.items()
                       if data.get("timestamp", 0) < cutoff]
        for replica_id in replica_ids:
            node_ip = self._unhealthy_replicas[replica_id]["node_ip"]
            self._unhealthy_replicas.pop(replica_id, None)
            if node_ip in self._nodes_marked_for_reap and self._nodes_marked_for_reap[node_ip] < cutoff:
                self._nodes_marked_for_reap.pop(node_ip, None)
