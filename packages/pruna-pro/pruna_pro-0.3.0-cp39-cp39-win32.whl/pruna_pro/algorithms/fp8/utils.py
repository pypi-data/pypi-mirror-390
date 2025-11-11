from __future__ import annotations

from typing import Optional

import torch


class F8Linear(torch.nn.Module):
    """
    A custom linear layer that uses 8-bit floating point quantization for weights/activations.

    This is a modified version of the F8Linear class from the flux-fp8-api.
    The original class is available at https://github.com/aredden/flux-fp8-api/blob/main/float8_quantize.py

    Parameters
    ----------
    in_features : int
        The number of input features.
    out_features : int
        The number of output features.
    bias : bool, optional
        Whether to use bias.
    device : torch.device, optional
        The device to use.
    dtype : torch.dtype, optional
        The dtype to use.
    float8_dtype : torch.dtype, optional
        The float8 dtype to use for weight quantization.
    float_weight : torch.Tensor, optional
        The float weight to use.
    float_bias : torch.Tensor, optional
        The float bias to use.
    num_scale_trials : int, optional
        The number of scale trials to use.
    input_float8_dtype : torch.dtype, optional
        The float8 dtype to use for input quantization.
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=torch.float16,
        float8_dtype=torch.float8_e4m3fn,
        float_weight: Optional[torch.Tensor] = None,
        float_bias: Optional[torch.Tensor] = None,
        num_scale_trials: int = 12,
        input_float8_dtype=torch.float8_e5m2,
    ) -> None:
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.float8_dtype = float8_dtype
        self.input_float8_dtype = input_float8_dtype
        self.input_scale_initialized = False
        self.weight_initialized = False
        self.max_value = torch.finfo(self.float8_dtype).max
        self.input_max_value = torch.finfo(self.input_float8_dtype).max
        factory_kwargs = {"dtype": dtype, "device": device}
        if float_weight is None:
            self.weight = torch.nn.Parameter(torch.empty((out_features, in_features), **factory_kwargs))
        else:
            self.weight = torch.nn.Parameter(float_weight, requires_grad=float_weight.requires_grad)
        if float_bias is None:
            if bias:
                self.bias = torch.nn.Parameter(
                    torch.empty(out_features, **factory_kwargs),
                )
            else:
                self.register_parameter("bias", None)
        else:
            self.bias = torch.nn.Parameter(float_bias, requires_grad=float_bias.requires_grad)
        self.num_scale_trials = num_scale_trials
        self.input_amax_trials = torch.zeros(num_scale_trials, requires_grad=False, device=device, dtype=torch.float32)
        self.trial_index = 0
        self.register_buffer("scale", None)
        self.register_buffer(
            "input_scale",
            None,
        )
        self.register_buffer(
            "float8_data",
            None,
        )
        self.register_buffer("scale_reciprocal", None)
        self.register_buffer("input_scale_reciprocal", None)

    def quantize_weight(self) -> None:
        """Quantize the weight of the linear layer."""
        if self.weight_initialized:
            return
        amax = torch.max(torch.abs(self.weight.data)).float()
        self.scale = self.amax_to_scale(amax, self.max_value)
        self.float8_data = self.to_fp8_saturated(self.weight.data, self.scale, self.max_value).to(self.float8_dtype)
        self.scale_reciprocal = self.scale.reciprocal()
        self.weight.data = torch.zeros(1, dtype=self.weight.dtype, device=self.weight.device, requires_grad=False)
        self.weight_initialized = True

    def amax_to_scale(self, amax: torch.Tensor, max_val: float) -> torch.Tensor:
        """
        Convert the amax to a scale.

        Parameters
        ----------
        amax : torch.Tensor
            The absolute max value of tensor to quantize.
        max_val : float
            The maximum possible value of the scale.

        Returns
        -------
        torch.Tensor
            The scale to use for quantization.
        """
        return (max_val / torch.clamp(amax, min=1e-12)).clamp(max=max_val)

    def to_fp8_saturated(self, x: torch.Tensor, scale: torch.Tensor, max_val: float) -> torch.Tensor:
        """
        Scale the input to maximally fill the range of fp8 values.

        Parameters
        ----------
        x : torch.Tensor
            The input to quantize.
        scale : torch.Tensor
            The scale to use for quantization.
        max_val : float
            The maximum possible value of the scale.

        Returns
        -------
        torch.Tensor
            The scaled input.
        """
        return (x * scale).clamp(-max_val, max_val)

    def quantize_input(self, x: torch.Tensor) -> torch.Tensor:
        """
        Quantize the input to the float8 data type.

        Parameters
        ----------
        x : torch.Tensor
            The input to quantize.

        Returns
        -------
        torch.Tensor
            The quantized input.
        """
        if self.input_scale_initialized:
            return self.to_fp8_saturated(x, self.input_scale, self.input_max_value).to(  # type: ignore
                self.input_float8_dtype
            )
        elif self.trial_index < self.num_scale_trials:
            amax = torch.max(torch.abs(x)).float()

            self.input_amax_trials[self.trial_index] = amax
            self.trial_index += 1
            self.input_scale = self.amax_to_scale(self.input_amax_trials[: self.trial_index].max(), self.input_max_value)
            self.input_scale_reciprocal = self.input_scale.reciprocal()
            return self.to_fp8_saturated(x, self.input_scale, self.input_max_value).to(self.input_float8_dtype)
        else:
            self.input_scale = self.amax_to_scale(self.input_amax_trials.max(), self.input_max_value)
            self.input_scale_reciprocal = self.input_scale.reciprocal()
            self.input_scale_initialized = True
            return self.to_fp8_saturated(x, self.input_scale, self.input_max_value).to(self.input_float8_dtype)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Run the forward pass of the linear layer, quantized.

        Parameters
        ----------
        x : torch.Tensor
            The input to the linear layer.

        Returns
        -------
        torch.Tensor
            The output of the linear layer.
        """
        if self.input_scale_initialized:
            x = self.to_fp8_saturated(x, self.input_scale, self.input_max_value).to(self.input_float8_dtype)
        else:
            x = self.quantize_input(x)

        prev_dims = x.shape[:-1]
        x = x.view(-1, self.in_features)

        # float8 matmul, much faster than float16 matmul w/ float32 accumulate on ADA devices!
        out = torch._scaled_mm(
            x,
            self.float8_data.T,
            scale_a=self.input_scale_reciprocal,
            scale_b=self.scale_reciprocal,
            bias=self.bias,
            out_dtype=self.weight.dtype,
            use_fast_accum=True,
        )
        out = out.reshape(*prev_dims, self.out_features)
        return out

    @classmethod
    def from_linear(
        cls,
        linear: torch.nn.Linear,
        float8_dtype=torch.float8_e4m3fn,
        input_float8_dtype=torch.float8_e5m2,
    ) -> "F8Linear":
        """
        Create a new F8Linear instance from a nn.Linear instance.

        Parameters
        ----------
        linear : torch.nn.Linear
            The linear layer to convert to F8Linear.
        float8_dtype : torch.dtype
            The float8 dtype to use for weight quantization.
        input_float8_dtype : torch.dtype
            The float8 dtype to use for input quantization.

        Returns
        -------
        F8Linear
            The new F8Linear instance.
        """
        f8_lin = cls(
            in_features=linear.in_features,
            out_features=linear.out_features,
            bias=linear.bias is not None,
            device=linear.weight.device,
            dtype=linear.weight.dtype,
            float8_dtype=float8_dtype,
            float_weight=linear.weight.data,
            float_bias=(linear.bias.data if linear.bias is not None else None),
            input_float8_dtype=input_float8_dtype,
        )
        # quantize the weight of the linear layer
        f8_lin.quantize_weight()
        return f8_lin


def quantize_linear_layer_fp8(
    parent: torch.nn.Module,
    child_name: str,
    float8_dtype: torch.dtype,
    input_float8_dtype: torch.dtype,
) -> None:
    """
    Quantize a linear layer with fp8 quantization.

    Parameters
    ----------
    parent : torch.nn.Module
        The parent module of the linear layer.
    child_name : str
        The name of the linear layer.
    float8_dtype : torch.dtype
        The float8 dtype to use for weight quantization.
    input_float8_dtype : torch.dtype
        The float8 dtype to use for input quantization.

    Returns
    -------
    None
        This function modifies the model in-place and does not return anything.
    """
    child = getattr(parent, child_name)
    quantized_linear = F8Linear.from_linear(
        child,
        float8_dtype=float8_dtype,
        input_float8_dtype=input_float8_dtype,
    )
    setattr(parent, child_name, quantized_linear)
    del child
