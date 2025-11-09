from typing import Optional, Tuple

from ray import serve
from ray.serve.handle import DeploymentHandle
from ray.util import get_node_ip_address, state

from ray_embedding.node_reaper import NODE_REAPER_DEPLOYMENT_NAME


def get_head_node_id() -> Tuple[str, str]:
    try:
        nodes = state.list_nodes(filters=[("is_head_node", "=", True)])
        if not nodes:
            raise RuntimeError("Unable to locate head node for NodeReaper deployment.")
        head_node = nodes[0]
        return head_node["node_id"], head_node["node_ip"]
    except Exception as exc:
        raise RuntimeError("Unable to locate the head node ID for NodeReaper deployment.") from exc


def get_node_reaper_handle() -> DeploymentHandle:
    try:
        return serve.context.get_deployment_handle(NODE_REAPER_DEPLOYMENT_NAME)
    except Exception:
        return serve.get_deployment(NODE_REAPER_DEPLOYMENT_NAME).get_handle(sync=False)


def get_current_replica_tag() -> Optional[str]:
    try:
        context = serve.context.get_current_replica_context()
    except Exception:
        context = None
    if context is None:
        return None
    return getattr(context, "replica_tag", None)


def get_current_node_ip() -> Optional[str]:
    try:
        return get_node_ip_address()
    except Exception:
        return None


def report_unhealthy_replica(error: Optional[str] = None,
                             node_reaper: Optional[DeploymentHandle] = None) -> None:
    replica_id = get_current_replica_tag()
    node_ip = get_current_node_ip()
    if not (replica_id and node_ip):
        return
    handle = node_reaper
    if handle is None:
        try:
            handle = get_node_reaper_handle()
        except Exception:
            return
    handle.report_failure.remote(replica_id, node_ip, error)
