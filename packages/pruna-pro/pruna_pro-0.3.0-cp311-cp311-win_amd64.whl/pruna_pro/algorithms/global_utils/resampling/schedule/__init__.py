from pruna_pro.algorithms.global_utils.resampling.schedule.resampling_schedule import ResamplingSchedule


def get_bottleneck_sampling_schedule(scale_factor: float, fraction: float) -> ResamplingSchedule:
    """
    Get a resampling schedule for bottleneck sampling.

    Parameters
    ----------
    scale_factor : float
        The scale factor for the resampling schedule.
    fraction : float
        The fraction of steps assigned to the bottleneck stage.

    Returns
    -------
    ResamplingSchedule
        The resampling schedule.
    """
    return ResamplingSchedule(1.0, 0.1, scale_factor, fraction)


def get_prores_schedule(scale_factor: float, fraction: float, stages: int) -> ResamplingSchedule:
    """
    Get a resampling schedule for ProRes.

    Parameters
    ----------
    scale_factor : float
        The scale factor for the resampling schedule.
    fraction : float
        The fraction of steps assigned to the bottleneck stage.
    stages : int
        The number of resampling stages.

    Returns
    -------
    ResamplingSchedule
        The resampling schedule.
    """
    if stages == 2:
        return ResamplingSchedule(scale_factor, fraction, scale_factor, 0.0)
    elif stages == 3:
        stage_2_scale_factor = (scale_factor + 1.0) / 2
        return ResamplingSchedule(scale_factor, fraction / 2, stage_2_scale_factor, fraction / 2)
    else:
        raise ValueError(f"Invalid number of stages: {stages}")
