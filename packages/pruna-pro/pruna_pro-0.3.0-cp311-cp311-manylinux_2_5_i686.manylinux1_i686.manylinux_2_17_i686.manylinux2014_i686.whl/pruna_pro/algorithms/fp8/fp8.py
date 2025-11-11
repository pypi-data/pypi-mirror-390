from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Dict

import torch
from ConfigSpace import Constant
from pruna import SmashConfig
from pruna.algorithms.base.pruna_base import PrunaAlgorithmBase
from pruna.algorithms.base.tags import AlgorithmTag
from pruna.config.smash_config import SmashConfigPrefixWrapper
from pruna.config.target_modules import TARGET_MODULES_TYPE, TargetModules, map_targeted_nn_roots
from pruna.engine.model_checks import (
    is_transformer_pipeline,
    is_unet_pipeline,
)
from pruna.engine.save import SAVE_FUNCTIONS
from pruna.engine.utils import safe_memory_cleanup

from pruna_pro.algorithms.fp8.utils import quantize_linear_layer_fp8
from pruna_pro.algorithms.global_utils.quantization.utils.swap_linear import swap_linear
from pruna_pro.engine.pruna_pro_model import PrunaProModel


class Fp8(PrunaAlgorithmBase):
    """
    Implement fp8 quantization, using torch._scaled_mm to accelerate the inference.

    Based on the torch.float8_e4m3fn and torch.float8_e5m2 formats, this quantizer compresses the weights,
    but also the activations, to reduce the memory usage and the inference time.
    """

    algorithm_name = "fp8"
    group_tags: list[AlgorithmTag] = [AlgorithmTag.QUANTIZER]
    references: dict[str, str] = {
        "Github": "https://github.com/aredden/flux-fp8-api",
    }
    save_fn = SAVE_FUNCTIONS.save_before_apply
    tokenizer_required = False
    processor_required = False
    runs_on: list[str] = ["cpu", "cuda", "accelerate"]
    dataset_required = False
    compatible_before: Iterable[str | AlgorithmTag] = ["qkv_diffusers", "padding_pruning"]
    compatible_after: Iterable[str | AlgorithmTag] = [
        AlgorithmTag.CACHER,
        AlgorithmTag.RESAMPLER,  # type: ignore[attr-defined]
        AlgorithmTag.ENHANCER,  # type: ignore[attr-defined]
        "ring_attn",
    ]

    def get_hyperparameters(self) -> list:
        """
        Configure all algorithm-specific hyperparameters with ConfigSpace.

        Returns
        -------
        list
            The hyperparameters.
        """
        return [
            Constant(
                "float8_dtype",
                value="torch.float8_e4m3fn",
                meta=dict(desc="The float8 dtype to use for weight quantization."),
            ),
            Constant(
                "input_float8_dtype",
                value="torch.float8_e5m2",
                meta=dict(desc="The float8 dtype to use for input quantization."),
            ),
            TargetModules(
                "target_modules",
                default_value=None,
                meta=dict(
                    desc="Precise choices of which modules to quantize, "
                    "e.g. {include: ['transformer.*']} to quantize only the transformer in a diffusion pipeline. "
                    f"See the {TargetModules.documentation_name_with_link} documentation for more details."
                ),
            ),
        ]

    def model_check_fn(self, model: Any) -> bool:
        """
        Check if the model is directly made of a nn.Module, or if it is a pipeline with a unet/transformer denoiser.

        Parameters
        ----------
        model : Any
            The model to check.

        Returns
        -------
        bool
            True if the model is a nn.Module, or a pipeline with a unet/transformer denoiser, False otherwise.
        """
        if isinstance(model, torch.nn.Module):
            return True
        return is_unet_pipeline(model) or is_transformer_pipeline(model)

    def get_model_dependent_hyperparameter_defaults(
        self, model: Any, smash_config: SmashConfig | SmashConfigPrefixWrapper
    ) -> TARGET_MODULES_TYPE:
        """
        Get default values for the target_modules based on the model and configuration.

        Parameters
        ----------
        model : Any
            The model to get the default hyperparameters from.
        smash_config : SmashConfig
            The SmashConfig object.

        Returns
        -------
        TARGET_MODULES_TYPE
            The default target_modules for the algorithm.
        """
        include: list[str]
        exclude: list[str]
        if is_unet_pipeline(model):
            include = ["unet.*"]
            proj_out_pattern = "unet.proj_out"
        elif is_transformer_pipeline(model):
            include = ["transformer.*"]
            proj_out_pattern = "transformer.proj_out"
        else:
            include = ["*"]
            proj_out_pattern = "proj_out"
        exclude = [
            "*embed*",
            "*norm*",
            proj_out_pattern,  # proj_out module at the root of the model/pipeline
            "*lm_head",  # "lm_head" modules, for transformers
        ]
        return {"include": include, "exclude": exclude}

    def _apply(self, model: Any, smash_config: SmashConfigPrefixWrapper) -> Any:
        """
        Quantize the model.

        Parameters
        ----------
        model : Any
            The model to quantize.
        smash_config : SmashConfigPrefixWrapper
            The configuration for the quantization.

        Returns
        -------
        Any
            The quantized model.
        """
        PrunaProModel.verify_token(token=None)

        float8_dtype = (
            torch.float8_e4m3fn if smash_config["float8_dtype"] == "torch.float8_e4m3fn" else torch.float8_e5m2
        )
        input_float8_dtype = (
            torch.float8_e4m3fn if smash_config["input_float8_dtype"] == "torch.float8_e4m3fn" else torch.float8_e5m2
        )

        target_modules: None | TARGET_MODULES_TYPE = smash_config["target_modules"]
        if target_modules is None:
            target_modules = self.get_model_dependent_hyperparameter_defaults(model, smash_config)

        def quantize_nn_module(attr_name: str | None, module: torch.nn.Module, subpaths: list[str]) -> Any:
            """
            Apply fp8 quantization to a nn.Module.

            Parameters
            ----------
            attr_name : str | None
                The name of the attribute in the model pointing to the nn.Module to quantize.
            module : torch.nn.Module
                The nn.Module to quantize.
            subpaths : list[str]
                The subpaths of the module to quantize.
            """
            for subpath in subpaths:
                swap_linear(
                    module,
                    quantize_linear_layer_fn=quantize_linear_layer_fp8,
                    path=subpath,
                    kwargs={"float8_dtype": float8_dtype, "input_float8_dtype": input_float8_dtype},
                )
            return module

        model = map_targeted_nn_roots(quantize_nn_module, model, target_modules)

        safe_memory_cleanup()
        return model

    def import_algorithm_packages(self) -> Dict[str, Any]:
        """
        Provide a algorithm packages for the algorithm.

        Returns
        -------
        Dict[str, Any]
            The algorithm packages.
        """
        return dict()
