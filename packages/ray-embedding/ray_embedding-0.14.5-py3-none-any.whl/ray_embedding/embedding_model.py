import logging
import os.path
import time
from typing import Optional, Dict, Any, List, Union

import torch
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo
from ray import serve
from ray.serve.handle import DeploymentHandle
from sentence_transformers import SentenceTransformer

from ray_embedding.utils import report_unhealthy_replica


@serve.deployment
class EmbeddingModel:
    def __init__(self, model: str, served_model_name: Optional[str] = None,
                 device: Optional[str] = None, backend: Optional[str] = "torch",
                 matryoshka_dim: Optional[int] = None, trust_remote_code: Optional[bool] = False,
                 model_kwargs: Dict[str, Any] = None, cuda_memory_flush_threshold: Optional[float] = 0.8,
                 node_reaper: Optional[DeploymentHandle] = None):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.served_model_name = served_model_name or os.path.basename(self.model)
        self.init_device = device
        self.cuda_memory_flush_threshold = cuda_memory_flush_threshold
        self.node_reaper = node_reaper
        self.torch_device = torch.device(self.init_device)
        self.backend = backend or "torch"
        self.matryoshka_dim = matryoshka_dim
        self.trust_remote_code = trust_remote_code or False
        self.model_kwargs = model_kwargs or {}

        if self.init_device is None or self.init_device == "auto":
            self.init_device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.init_device == "cuda":
            self.wait_for_cuda()

        self.logger.info(f"Initializing embedding model: {self.model}")
        self.embedding_model = SentenceTransformer(self.model, device=self.init_device, backend=self.backend,
                                                   trust_remote_code=self.trust_remote_code,
                                                   model_kwargs=self.model_kwargs)

        self.logger.info(f"Successfully initialized model {self.model} using device {self.torch_device}")

    async def __call__(self, text: Union[str, List[str]], dimensions: Optional[int] = None) -> List[List[float]]:
        """Compute embeddings for the input text using the current model."""
        if not text or (isinstance(text, list) and not all(text)):
            raise ValueError("Input text is empty or invalid")

        text = [text] if isinstance(text, str) else text
        truncate_dim = dimensions or self.matryoshka_dim

        # Compute embeddings in PyTorch format
        embeddings = self.embedding_model.encode(
            text, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=False,
        ).to(self.torch_device)

        if truncate_dim is not None:
            # Truncate and re-normalize the embeddings
            embeddings = embeddings[:, :truncate_dim]
            embeddings = embeddings / torch.norm(embeddings, dim=1, keepdim=True)

        # Move all embeddings to CPU at once before conversion
        embeddings_list = embeddings.cpu().tolist()

        # don't wait for GC
        del embeddings

        return embeddings_list

    def wait_for_cuda(self, wait: int = 10):
        if self.init_device == "cuda" and not torch.cuda.is_available():
            time.sleep(wait)
        self.check_health()

    def check_health(self):
        if self.init_device != "cuda":
            return

        try:
            # Even though CUDA was available at init time,
            # CUDA can become unavailable - this is a known problem in AWS EC2+Docker
            # https://github.com/ray-project/ray/issues/49594
            nvmlInit()
            count = nvmlDeviceGetCount()
            assert count >= 1, "No CUDA devices found"

            # replicas only have access to GPU 0
            handle = nvmlDeviceGetHandleByIndex(0)
            mem_info = nvmlDeviceGetMemoryInfo(handle)
        except Exception as e:
            error_message = f"CUDA health check failed: {e}"
            report_unhealthy_replica(error=error_message, node_reaper=self.node_reaper)
            raise RuntimeError(error_message)

        reserved = torch.cuda.memory_reserved()  # bytes currently reserved by CUDA cache
        threshold_bytes = self.cuda_memory_flush_threshold * mem_info.total

        if reserved > threshold_bytes:
            # flush only when cache exceeds the percentage threshold
            torch.cuda.empty_cache()

    def __del__(self):
        # Clean up and free any remaining GPU memory
        try:
            if hasattr(self, 'embedding_model'):
                del self.embedding_model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
