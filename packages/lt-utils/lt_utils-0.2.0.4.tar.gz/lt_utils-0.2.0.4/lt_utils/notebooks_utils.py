from __future__ import annotations

__all__ = ["show_audio", "show_image", "show_video"]

from typing import Union, List, Any, TYPE_CHECKING
from lt_utils.type_utils import is_tensor

if TYPE_CHECKING:
    from torch import Tensor
    from numpy import ndarray


def show_audio(
    audio_track: Union["ndarray", "Tensor", List],
    sample_rate: int = 24000,
):
    import IPython.display as iDisplay
    import numpy as np

    if is_tensor(audio_track):
        audio_track = audio_track.clone().detach().cpu().squeeze().numpy()
    else:
        audio_track = np.asarray(audio_track).squeeze()
    return iDisplay.display(iDisplay.Audio(audio_track, rate=sample_rate))


def show_image(image: Any):
    import IPython.display as iDisplay

    try:
        return iDisplay.display(iDisplay.Image(image))
    except Exception as e:
        try:
            return iDisplay.display(image)
        except:
            raise e


def show_video(video: Any):
    import IPython.display as iDisplay

    try:
        return iDisplay.display(iDisplay.Video(video))
    except Exception as e:
        try:
            return iDisplay.display(video)
        except:
            raise e


display_video = show_video
