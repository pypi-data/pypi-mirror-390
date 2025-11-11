from __future__ import annotations

from typing import Any

from pruna_pro.algorithms.global_utils.resampling.pipeline_helper.flux import FluxHelper
from pruna_pro.algorithms.global_utils.resampling.pipeline_helper.flux_kontext import FluxKontextHelper
from pruna_pro.algorithms.global_utils.resampling.pipeline_helper.hidream import HiDreamHelper
from pruna_pro.algorithms.global_utils.resampling.pipeline_helper.hunyuan import HunyuanHelper
from pruna_pro.algorithms.global_utils.resampling.pipeline_helper.pipeline_helper import PipelineHelper
from pruna_pro.algorithms.global_utils.resampling.pipeline_helper.qwen import QwenHelper
from pruna_pro.algorithms.global_utils.resampling.pipeline_helper.wan import WanHelper
from pruna_pro.algorithms.global_utils.resampling.pipeline_helper.wan_i2v import WanI2VHelper

IMAGE_PIPELINES = {
    "FluxKontextPipeline": FluxKontextHelper,
    "FluxPipeline": FluxHelper,
    "HiDreamImagePipeline": HiDreamHelper,
    "QwenImagePipeline": QwenHelper,
}
VIDEO_PIPELINES = {
    "WanImageToVideoPipeline": WanI2VHelper,
    "WanPipeline": WanHelper,
    "HunyuanVideoPipeline": HunyuanHelper,
}
SUPPORTED_PIPELINES = {**IMAGE_PIPELINES, **VIDEO_PIPELINES}


def get_pipeline_helper(pipe: Any, sampling_mode: str) -> PipelineHelper:
    """
    Get the pipeline helper for a given pipeline.

    Parameters
    ----------
    pipe : Any
        The pipeline to get the helper for.
    sampling_mode : str
        The sampling mode.

    Returns
    -------
    PipelineHelper
        The pipeline helper for the given pipeline.
    """
    pipe_class = getattr(pipe, "__class__", None)
    pipe_name = getattr(pipe_class, "__name__", None) if pipe_class is not None else None
    if pipe_name not in SUPPORTED_PIPELINES:
        raise ValueError(f"{pipe_name} is not supported by prores.")
    if sampling_mode == "default":
        sampling_mode = "bilinear" if pipe_name in IMAGE_PIPELINES else "trilinear"
    valid_sampling_modes_image = ["bilinear", "bicubic", "nearest"]
    valid_sampling_modes_video = ["trilinear", "area"]
    valid_sampling_modes = valid_sampling_modes_image if pipe_name in IMAGE_PIPELINES else valid_sampling_modes_video
    return SUPPORTED_PIPELINES[pipe_name](pipe, sampling_mode, valid_sampling_modes)  # type: ignore[abstract]
