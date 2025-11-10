__all__ = [
    "sub_outer",
    "normalize_minmax",
    "normalize_zscore",
    "spectral_norm",
    "channel_randomizer",
    "non_zero",
    "log_magnitude",
    "view_as_complex",
    "dot_product",
    "log_norm",
    "compact_embeddings",
    "ensure_2d",
    "ensure_3d",
    "move_dict_to_device",
    "move_list_to_device",
    "clip_gradients",
]
import torch
from torch import nn, Tensor
from lt_utils.common import *


def dot_product(x: Tensor, y: Tensor, dim: int = -1) -> Tensor:
    """Computes dot product along the specified dimension."""
    return torch.sum(x * y, dim=dim)


def view_as_complex(tensor: Tensor):
    if not torch.is_complex(tensor):
        if tensor.size(-1) == 2 and torch.ndim > 2:  # maybe real+imag as last dim
            try:
                return torch.view_as_complex(tensor)
            except:
                pass

        # treat as real and multiply by 1j
        return tensor * (1j)
    return tensor


def ensure_2d(x: Tensor):
    if x.ndim == 2:
        return x
    B = 1 if x.ndim < 2 else x.size(0)
    return x.view(B, -1)


def ensure_3d(x: Tensor, t_centered: bool = False):
    if x.ndim != 3:
        B = 1 if x.ndim < 2 else x.size(0)
        T = 1 if not x.ndim else x.size(-1)  # scalar
        x = x.view(B, -1, T)
        if t_centered:
            x = x.transpose(-1, -2)
    return x


def compact_embeddings(
    x: Tensor,
    factor: int = 2,
    normalize: bool = True,
) -> Tensor:
    """
    Compact embeddings along the feature dimension by averaging groups of size `factor`.
    Args:
        x: [B, D] or [B, T, D] tensor
        factor: reduction factor
        normalize: whether to L2-normalize after compaction
    Returns:
        compacted tensor with reduced feature dimension
    """
    if x.shape[-1] % factor != 0:
        raise ValueError(f"Feature dim {x.shape[-1]} not divisible by factor={factor}")

    new_dim = x.shape[-1] // factor
    shape = list(x.shape[:-1]) + [new_dim, factor]
    x = x.reshape(shape).mean(dim=-1)

    if normalize:
        norm = torch.norm(x, p=2, dim=-1, keepdim=True).clamp(min=1e-6)
        x = x / norm
    return x


def log_magnitude(stft_complex: Tensor, eps: float = 1e-6) -> Tensor:
    """
    Compute magnitude from STFT tensor.
    Args:
        stft: [B, F, T] tensor (complex or real)
    Returns:
        magnitude: [B, F, T] real tensor
    """
    if not torch.is_complex(stft):
        stft = view_as_complex(stft)
    magnitude = torch.abs(stft_complex)
    return torch.log(magnitude + eps)


def sub_outer(tensor: Tensor, other: Tensor):
    return tensor.reshape(-1, 1) - other


def normalize_minmax(
    x: Tensor,
    min_val: float = -1.0,
    max_val: float = 1.0,
    dim: Union[Sequence[int], int] = (),
    eps: float = 1e-6,
) -> Tensor:
    """Scales tensor to [min_val, max_val] range."""
    x_min, x_max = x.amin(dim=dim), x.amax(dim=dim)
    return (x - x_min) / (x_max - x_min + eps) * (max_val - min_val) + min_val


def normalize_zscore(
    x: Tensor, dim: int = -1, keep_dims: bool = True, eps: float = 1e-6
):
    mean = x.mean(dim=dim, keepdim=keep_dims)
    std = x.std(dim=dim, keepdim=keep_dims)
    return (x - mean) / (std + eps)


def spectral_norm(x: Tensor, c: int = 1, eps: float = 1e-6) -> Tensor:
    return torch.log(torch.clamp(x, min=eps) * c)


def channel_randomizer(
    x: Tensor,
    combinations: int = 1,
    dim: int = 1,
) -> Tensor:
    """
    Randomizes channels along a dimension, with optional grouping.
    Args:
        x: Tensor [B, C, T] or [C, T]
        combinations: Number of groups/combinations to split channels into.
                groups=1 -> shuffle all channels freely
                groups=C -> no shuffle
        dim: channel dimension (1 for [B, C, T], 0 for [C, T])
    Returns:
        shuffled tensor
    """
    C = x.shape[dim]
    if C % combinations != 0:
        raise ValueError(
            f"Number of channels {C} not divisible by groups={combinations}"
        )

    # reshape into groups
    group_size = C // combinations
    shape = list(x.shape)
    shape[dim] = combinations
    shape.insert(dim + 1, group_size)
    xg = x.reshape(shape)

    # permutation of groups
    perm = torch.randperm(combinations, device=x.device)
    xg = xg.index_select(dim, perm)

    # flatten back
    x = xg.reshape(list(x.shape))
    return x


def non_zero(value: Union[float, Tensor]):
    if not (value == 0).any().item():
        return value + torch.finfo(value.dtype).tiny
    return value


def log_norm(
    self, entry: Tensor, std: Number = 4, mean: Number = -4, eps: float = 1e-5
) -> Tensor:
    return (torch.log(eps + entry.unsqueeze(0)) - mean) / max(
        std + torch.finfo(entry.dtype).tiny
    )


def clip_gradients(model: nn.Module, max_norm: float = 1.0):
    """Applies gradient clipping."""
    return nn.utils.clip_grad_norm_(model.parameters(), max_norm)


def move_list_to_device(
    entries: Union[List[Union[Any, Tensor]], Tuple[Union[Any, Tensor], ...]],
    device: Union[str, torch.device],
    max_depth: int = 3,
    *,
    _depth: int = 0,
):
    was_tuple = isinstance(entries, tuple)
    if was_tuple:
        entries_list = [x for x in entries]
        entries = entries_list

    for i in range(len(entries)):
        if isinstance(entries[i], Tensor):
            entries[i] = entries[i].to(device=device)
        elif _depth >= max_depth:
            continue
        elif isinstance(entries[i], dict):
            entries[i] = move_dict_to_device(
                entries[i], device=device, _depth=_depth + 1
            )
        elif isinstance(entries[i], (tuple, list)):
            entries[i] = move_list_to_device(
                entries[i], device=device, _depth=_depth + 1
            )
    if was_tuple:
        return tuple(entries)
    return entries


def move_dict_to_device(
    entries: Dict[str, Union[Any, Tensor]],
    device: Union[str, torch.device],
    max_depth: int = 3,
    *,
    _depth: int = 0,
):
    keys = list(entries.keys())
    for k in keys:
        if isinstance(entries[k], Tensor):
            entries[k] = entries[k].to(device)
        elif _depth >= max_depth:
            continue
        elif isinstance(entries[k], dict):
            entries[k] = move_dict_to_device(
                entries[k], device=device, _depth=_depth + 1
            )
        elif isinstance(entries[k], (list, tuple)):
            entries[k] = move_list_to_device(
                entries[k], device=device, _depth=_depth + 1
            )
    return entries
