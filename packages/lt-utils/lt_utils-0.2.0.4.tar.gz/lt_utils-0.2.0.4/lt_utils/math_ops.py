__all__ = [
    "percentage_difference",
    "mean",
    "median",
    "clamp",
    "round_to",
    "variance",
    "standard_deviation",
    "normalize",
    "distance_2d",
    "angle_between",
    "deg_to_rad",
    "rad_to_deg",
    "dot_product",
    "factorial_safe",
    "combinations",
    "permutations",
    "vector_norm",
    "cosine_similarity",
    "matrix_multiply",
    "linear_interpolation",
    "moving_average",
    "softmax",
    "sigmoid",
    "sub",
    "argmax",
    "time_weighted_avg",
    "time_weighted_ema",
]

import math
import numpy as np
from lt_utils.common import *
from torch import Tensor
import torch


def sub(*values: Number) -> float:
    match len(values):
        case 0:
            return float("nan")
        case 1:
            return values[0]
        case 2:
            return values[0] - values[1]
        case 3:
            return values[0] - values[1] - values[2]
        case _:
            return (
                float(values[0]) - np.array([float(x) for x in values[1:]]).sum().item()
            )


def time_weighted_avg(data: np.ndarray, alpha: float = 0.9) -> np.ndarray:
    """
    Compute time-weighted moving average for smoothing.
    Args:
        data: [T] or [N, T] tensor / array (time series)
        alpha: smoothing factor (0 < alpha < 1), higher = smoother
    Returns:
        smoothed array of same shape
    """
    data = np.asanyarray(data).squeeze()
    if data.ndim == 1:
        out = np.zeros_like(data)
        out[0] = data[0]
        for t in range(1, len(data)):
            out[t] = alpha * out[t - 1] + (1 - alpha) * data[t]
        return out
    elif data.ndim == 2:
        out = np.zeros_like(data)
        out[:, 0] = data[:, 0]
        for t in range(1, data.shape[1]):
            out[:, t] = alpha * out[:, t - 1] + (1 - alpha) * data[:, t]
        return out
    else:
        raise ValueError("Data must be 1D or 2D time series")


def time_weighted_ema(
    x: Tensor,
    time_weights: Optional[Tensor] = None,
    alpha: float = 0.9,
    normalize: bool = False,
    eps: float = 1e-8,
    ret_type: Literal["pytorch", "list", "numpy"] = "pytorch",
):
    """
    Compute a time-weighted exponential moving average (EMA) for a 1D or 2D tensor.

    Args:
        x (torch.Tensor): Input tensor of shape (T,) or (B, T)
        time_weights (torch.Tensor, optional): Relative weights per time step.
            Must be broadcastable to x.shape. If None, uses uniform spacing.
        alpha (float): Smoothing factor in [0,1]. Higher means slower decay.
        normalize (bool): If True, normalize EMA output to zero mean/unit variance.
        eps (float): Small constant to prevent division by zero.

    Returns:
        torch.Tensor: Time-weighted EMA of same shape as input.
    """
    assert ret_type in [
        "pytorch",
        "list",
        "numpy",
    ], (
        f'invalid return type {ret_type}. Use one of: "'
        + '", "'.join(["pytorch", "list", "numpy"])
        + '".'
    )
    x = torch.as_tensor(x)

    if x.ndim != 2:
        x = x.view(1, -1)

    T = x.size(-1)

    if time_weights is None:
        time_weights = torch.ones(T, device=x.device)
    else:
        time_weights = torch.as_tensor(time_weights, device=x.device)

    # Normalize time weights to ensure stability
    time_weights = time_weights / (time_weights.max() + eps)

    ema = torch.zeros_like(x)
    ema[:, 0] = x[:, 0]

    for t in range(1, T):
        # Adjust decay using time weighting
        decay = alpha ** time_weights[t]
        ema[:, t] = decay * ema[:, t - 1] + (1 - decay) * x[:, t]

    if normalize:
        mean = ema.mean(dim=-1, keepdim=True)
        std = ema.std(dim=-1, keepdim=True) + eps
        ema = (ema - mean) / std

    ema = ema.squeeze()
    if ret_type == "pytorch":
        return ema
    cl_ema = ema.clone().detach().cpu()

    if ret_type == "list":
        return cl_ema.tolist()
    return cl_ema.numpy(force=True)


def percentage_difference(num1: Union[int, float], num2: Union[int, float]):
    """
    Calculate the percentage difference between two numbers.

    Parameters:
    - num1 (float): The first number.
    - num2 (float): The second number.

    Returns:
    float: The percentage difference.
    """
    assert (
        num1 != 0
    ), "Cannot calculate percentage difference when the first number is zero."

    percentage_difference = ((num2 - num1) / num1) * 100
    return abs(percentage_difference)


def mean(values: List[Number]) -> float:
    return sum(values) / len(values) if values else float("nan")


def median(values: List[Number]) -> float:
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(val, max_val))


def round_to(val: float, base: float = 1.0) -> float:
    return base * round(val / base)


def variance(values: List[float], sample: bool = True) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / (
        len(values) - 1 if sample else len(values)
    )


def standard_deviation(values: List[float], sample: bool = True) -> float:
    return math.sqrt(variance(values, sample))


def normalize(values: List[float]) -> List[float]:
    max_val = max(values)
    min_val = min(values)
    range_val = max_val - min_val
    return (
        [(v - min_val) / range_val for v in values]
        if range_val != 0
        else [0.0] * len(values)
    )


def distance_2d(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def angle_between(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


def deg_to_rad(degrees: float) -> float:
    return math.radians(degrees)


def rad_to_deg(radians: float) -> float:
    return math.degrees(radians)


def dot_product(v1: List[float], v2: List[float]) -> float:
    return float(np.dot(v1, v2))


def factorial_safe(n: int) -> int:
    return math.factorial(n) if n >= 0 else 1


def combinations(n: int, r: int) -> int:
    return math.comb(n, r)


def permutations(n: int, r: int) -> int:
    return math.perm(n, r)


def vector_norm(v: List[float]) -> float:
    return float(np.linalg.norm(v))


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))


def matrix_multiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    return np.matmul(a, b).tolist()


def linear_interpolation(x0, y0, x1, y1, x: Number) -> float:
    if x1 == x0:
        return y0  # Avoid div by zero
    return y0 + ((x - x0) * (y1 - y0)) / (x1 - x0)


def moving_average(values: List[float], window_size: int) -> List[float]:
    if window_size <= 1:
        return values
    return [
        sum(values[i : i + window_size]) / window_size
        for i in range(len(values) - window_size + 1)
    ]


def softmax(logits: List[float]) -> List[float]:
    e_logits = np.exp(logits - np.max(logits))  # for numerical stability
    return (e_logits / e_logits.sum()).tolist()


def sigmoid(x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    return 1 / (1 + np.exp(-x))


def argmax(logits: List[float]) -> int:
    return np.argmax(np.array(logits).astype(np.float32).flatten()).item()
