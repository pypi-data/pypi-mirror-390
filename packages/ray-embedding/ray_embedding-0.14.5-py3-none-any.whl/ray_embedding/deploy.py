import os
from typing import Any, Dict

import torch
from ray.serve import Application

from ray_embedding.dto import AppConfig, ModelDeploymentConfig, DeployedModel, NodeReaperConfig
from ray_embedding.embedding_model import EmbeddingModel
from ray_embedding.model_router import ModelRouter
from ray_embedding.node_reaper import NodeReaper, NODE_REAPER_DEPLOYMENT_NAME


def build_model(model_config: ModelDeploymentConfig, node_reaper):
    deployment_name = model_config.deployment
    model = model_config.model
    served_model_name = model_config.served_model_name or os.path.basename(model)
    device = model_config.device
    backend = model_config.backend or "torch"
    matryoshka_dim = model_config.matryoshka_dim
    trust_remote_code = model_config.trust_remote_code or False
    model_kwargs = model_config.model_kwargs or {}
    cuda_memory_flush_threshold = model_config.cuda_memory_flush_threshold or 0.8

    if "torch_dtype" in model_kwargs:
        torch_dtype = model_kwargs["torch_dtype"].strip()
        if torch_dtype == "float16":
            model_kwargs["torch_dtype"] = torch.float16
        elif torch_dtype == "bfloat16":
            model_kwargs["torch_dtype"] = torch.bfloat16
        elif torch_dtype == "float32":
            model_kwargs["torch_dtype"] = torch.float32
        else:
            raise ValueError(f"Invalid torch_dtype: '{torch_dtype}'")

    deployment = EmbeddingModel.options(name=deployment_name).bind(model=model,
                                                                   served_model_name=served_model_name,
                                                                   device=device,
                                                                   backend=backend,
                                                                   matryoshka_dim=matryoshka_dim,
                                                                   trust_remote_code=trust_remote_code,
                                                                   model_kwargs=model_kwargs,
                                                                   cuda_memory_flush_threshold=cuda_memory_flush_threshold,
                                                                   node_reaper=node_reaper,
                                                                   )
    return DeployedModel(model=served_model_name,
                         deployment_handle=deployment,
                         batch_size=model_config.batch_size,
                         num_retries=model_config.num_retries
                         )


def build_app(args: AppConfig) -> Application:
    model_router, models = args.model_router, args.models
    assert model_router and models
    assert model_router.path_prefix

    node_reaper_config = args.node_reaper or NodeReaperConfig()

    node_reaper_kwargs: Dict[str, Any] = {
        "ssh_user": node_reaper_config.ssh_user,
        "ssh_private_key": node_reaper_config.ssh_private_key,
    }
    if node_reaper_config.retention_seconds is not None:
        node_reaper_kwargs["retention_seconds"] = node_reaper_config.retention_seconds
    if node_reaper_config.reap_interval_seconds is not None:
        node_reaper_kwargs["reap_interval_seconds"] = node_reaper_config.reap_interval_seconds

    node_reaper = NodeReaper.options( 
        name=NODE_REAPER_DEPLOYMENT_NAME,
        ray_actor_options={"num_cpus": 0.25, "resources": {"head_node": 1}},
        autoscaling_config={"initial_replicas": 1, "min_replicas": 1, "max_replicas": 1}
    ).bind(**node_reaper_kwargs)

    deployed_models = {model_config.served_model_name: build_model(model_config, node_reaper) for model_config in models}
    model_router_kwargs = {
        "deployed_models": deployed_models,
        "path_prefix": model_router.path_prefix,
        "max_concurrency": model_router.max_concurrency,
        "node_reaper": node_reaper
    }
    router = ModelRouter.options(
        name=model_router.deployment,
        ray_actor_options={"num_cpus": 0.25, "resources": {"worker_node": 1}}
    ).bind(**model_router_kwargs)
    
    return router
