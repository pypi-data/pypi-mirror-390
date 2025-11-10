__all__ = [
    "get_plotly_layout",
    "line_plot",
    "multi_line_plot",
    "bar_chart",
    "heatmap",
    "histogram",
    "plot_3d_line",
    "plot_3d_surface",
    "plot_3d_scatter",
    "plot_waveform",
    "plot_mel_spectrogram",
    "plot_pitch_energy",
    "plot_stft_spectrogram",
    "plot_energy_curve",
    "plot_hnr_curve",
    "plot_loss_curve",
    "plot_gan_loss",
    "plot_normalized_losses",
    "plot_loss_anomalies",
    "plot_normalized_heatmap",
    "plot_anomaly_curve",
    "plot_anomaly_mask",
    "line_plot_avg",
    "plot_token_heatmap_grid",
    "plot_to_image",
    "get_image",
]

import plotly.graph_objects as go
import plotly.express as px
from lt_utils.common import *
import numpy as np
from lt_utils.type_utils._cos_tp import CMAP_TP
from torch import Tensor


def line_plot_avg(
    data: Dict[str, List[Any]],
    title: str = "Loss",
    xaxis_title="Step/Epoch",
    yaxis_title="Loss",
    template="plotly_dark",
    smoothing: Optional[Literal["ema", "avg"]] = None,
    alpha: float = 0.5,
    *args,
    **kwargs,
):
    from lt_utils.math_ops import time_weighted_avg, time_weighted_ema

    fig = go.Figure()
    for mode, values in data.items():
        if values:
            if not smoothing:
                items = values
            elif smoothing == "avg":
                items = time_weighted_avg(values, kwargs.get("smoothing_alpha", alpha))
            else:
                items = time_weighted_ema(values, kwargs.get("smoothing_alpha", alpha))
            fig.add_trace(go.Scatter(y=items, name=mode.capitalize()))
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        template=template,
    )
    return fig


def get_plotly_layout(
    title: str = "", x_label: str = "", y_label: str = "", dark=False
):
    """Usage: ``fig.update_layout(**get_plotly_layout(title, x_label, y_label, dark=dark))``"""
    return {
        "title": dict(text=title, x=0.5),
        "xaxis": dict(title=x_label, showgrid=True),
        "yaxis": dict(title=y_label, showgrid=True),
        "template": "plotly_dark" if dark else "plotly_white",
        "margin": dict(l=60, r=20, t=60, b=40),
        "legend": dict(title="Legend", x=0.01, y=0.99),
    }


def line_plot(
    x,
    y,
    title: str = "Styled Line Plot",
    x_label: str = "X",
    y_label: str = "Y",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
    line_color: str = "royalblue",
    line_width: int = 2,
    x_gridcolor: str = "LightGray",
    y_gridcolor: str = "LightGray",
    y_gridwidth: int = 1,
    x_gridwidth: int = 1,
):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers",
            line=dict(color=line_color, width=line_width),
            marker=dict(size=6),
            hovertemplate=f"{x_label}: %{{x}}<br>{y_label}: %{{y}}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis=dict(
            title=x_label, showgrid=True, gridwidth=y_gridwidth, gridcolor=x_gridcolor
        ),
        yaxis=dict(
            title=y_label, showgrid=True, gridwidth=x_gridwidth, gridcolor=y_gridcolor
        ),
        template=template,
        margin=dict(l=60, r=20, t=60, b=40),
    )
    return fig


def multi_line_plot(
    x,
    y_list,
    series_names: list[str],
    title: str = "Multi-Series Plot",
    x_label: str = "X",
    y_label: str = "Y",
    colors: Optional[Any] = None,
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    fig = go.Figure()
    if colors is None:
        colors = ["blue", "red", "green", "orange", "purple"]

    for i, (y, name) in enumerate(zip(y_list, series_names)):
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name=name,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=5),
                hovertemplate=f"{x_label}: %{{x}}<br>{name}: %{{y}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis=dict(title=x_label, showgrid=True),
        yaxis=dict(title=y_label, showgrid=True),
        legend=dict(title="Series", x=0.01, y=0.99),
        template=template,
    )
    return fig


def bar_chart(
    x,
    y,
    title: str = "Styled Bar Chart",
    x_label: str = "Categories",
    y_label: str = "Values",
    bar_color="steelblue",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x,
            y=y,
            marker=dict(color=bar_color),
            hovertemplate=f"{x_label}: %{{x}}<br>{y_label}: %{{y}}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        template=template,
    )
    return fig


def heatmap(
    z,
    x=None,
    y=None,
    title: str = "Styled Heatmap",
    x_label: str = "X Axis",
    y_label: str = "Y Axis",
    colorscale="Viridis",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale=colorscale,
            colorbar=dict(title="Intensity"),
            hovertemplate="X: %{x}<br>Y: %{y}<br>Value: %{z}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        template=template,
    )
    return fig


def histogram(
    data,
    nbins=30,
    title: str = "Styled Histogram",
    x_label: str = "Values",
    y_label: str = "Frequency",
    color="indianred",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=data,
            nbinsx=nbins,
            marker_color=color,
            hovertemplate=f"{x_label}: %{{x}}<br>Count: %{{y}}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        template=template,
    )
    return fig


def plot_3d_line(
    x,
    y,
    z,
    title: str = "3D Line Plot",
    x_label: str = "X",
    y_label: str = "Y",
    z_label: str = "Z",
    line_color="cyan",
    line_width=4,
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    fig = go.Figure(
        data=go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines+markers",
            line=dict(color=line_color, width=line_width),
            marker=dict(size=4),
            hovertemplate="X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        scene=dict(xaxis_title=x_label, yaxis_title=y_label, zaxis_title=z_label),
        template=template,
    )
    return fig


def plot_3d_surface(
    z,
    x=None,
    y=None,
    title: str = "3D Surface",
    x_label: str = "X",
    y_label: str = "Y",
    z_label: str = "Z",
    colorscale="Viridis",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    fig = go.Figure(
        data=go.Surface(
            z=z,
            x=x,
            y=y,
            colorscale=colorscale,
            hovertemplate="X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        scene=dict(xaxis_title=x_label, yaxis_title=y_label, zaxis_title=z_label),
        template=template,
    )
    return fig


def plot_3d_scatter(
    x,
    y,
    z,
    title: str = "3D Scatter",
    x_label: str = "X",
    y_label: str = "Y",
    z_label: str = "Z",
    point_color="red",
    point_size=5,
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    fig = go.Figure(
        data=go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="markers",
            marker=dict(size=point_size, color=point_color),
            hovertemplate="X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        scene=dict(xaxis_title=x_label, yaxis_title=y_label, zaxis_title=z_label),
        template=template,
    )
    return fig


def plot_waveform(
    samples,
    sr: int,
    title="Waveform",
    color="royalblue",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_white",
):
    times = np.arange(len(samples)) / sr
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=samples,
            mode="lines",
            line=dict(color=color),
            hovertemplate="Time: %{x:.3f}s<br>Amplitude: %{y:.3f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        template=template,
    )
    return fig


def plot_mel_spectrogram(
    mel,
    sr,
    hop_length,
    title="Log-Mel Spectrogram",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_white",
):

    time_axis = np.arange(mel.shape[1]) * hop_length / sr
    mel_axis = np.arange(mel.shape[0])

    fig = go.Figure(
        data=go.Heatmap(
            z=mel,
            x=time_axis,
            y=mel_axis,
            colorscale="Viridis",
            colorbar=dict(title="Log-Mel"),
            hovertemplate="Time: %{x:.3f}s<br>Mel: %{y}<br>Value: %{z:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Time (s)",
        yaxis_title="Mel Bin",
        template=template,
    )
    return fig


def plot_pitch_energy(
    pitch,
    energy,
    sr,
    hop_length,
    title="Pitch & Energy",
    color_pitch="tomato",
    color_energy="dodgerblue",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_white",
):

    time_axis = np.arange(len(pitch)) * hop_length / sr

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time_axis,
            y=pitch,
            name="Pitch (Hz)",
            line=dict(color=color_pitch),
            hovertemplate="Time: %{x:.3f}s<br>Pitch: %{y:.1f} Hz<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=time_axis,
            y=energy,
            name="Energy",
            line=dict(color=color_energy),
            hovertemplate="Time: %{x:.3f}s<br>Energy: %{y:.3f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Time (s)",
        yaxis_title="Value",
        legend=dict(x=0.01, y=0.99),
        template=template,
    )
    return fig


def plot_stft_spectrogram(
    mag,
    sr,
    hop_length,
    fft_bins=None,
    title="STFT Spectrogram",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_white",
):

    time_axis = np.arange(mag.shape[1]) * hop_length / sr
    freq_axis = np.linspace(0, sr // 2, mag.shape[0]) if fft_bins is None else fft_bins

    fig = go.Figure(
        data=go.Heatmap(
            z=mag,
            x=time_axis,
            y=freq_axis,
            colorscale="Cividis",
            colorbar=dict(title="Magnitude (dB)"),
            hovertemplate="Time: %{x:.3f}s<br>Freq: %{y:.1f} Hz<br>Mag: %{z:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Time (s)",
        yaxis_title="Frequency (Hz)",
        template=template,
    )
    return fig


def plot_energy_curve(
    energy,
    sr,
    hop_length,
    title="Energy Over Time",
    color="limegreen",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_white",
):

    time_axis = np.arange(len(energy)) * hop_length / sr

    fig = go.Figure(
        go.Scatter(
            x=time_axis,
            y=energy,
            mode="lines",
            line=dict(color=color),
            hovertemplate="Time: %{x:.3f}s<br>Energy: %{y:.3f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Time (s)",
        yaxis_title="Energy",
        template=template,
    )
    return fig


def plot_hnr_curve(
    hnr,
    sr,
    hop_length,
    title="Harmonics-to-Noise Ratio (HNR)",
    color="orange",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_white",
):

    time_axis = np.arange(len(hnr)) * hop_length / sr

    fig = go.Figure(
        go.Scatter(
            x=time_axis,
            y=hnr,
            mode="lines",
            line=dict(color=color),
            hovertemplate="Time: %{x:.3f}s<br>HNR: %{y:.2f} dB<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Time (s)",
        yaxis_title="HNR (dB)",
        template=template,
    )
    return fig


def plot_loss_curve(
    losses,
    title="Training Loss",
    smooth=0.0,
    color="orange",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_white",
):

    if smooth > 0:
        import pandas as pd

        losses = pd.Series(losses).ewm(alpha=1 - smooth).mean().values

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(len(losses))),
            y=losses,
            mode="lines",
            name="Loss",
            line=dict(color=color),
            hovertemplate="Step %{x}<br>Loss: %{y:.4f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Step",
        yaxis_title="Loss",
        template=template,
    )
    return fig


def plot_gan_loss(
    gen_losses,
    disc_losses,
    title="GAN Training Loss",
    smooth=0.1,
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    if smooth > 0:
        import pandas as pd

        gen_losses = pd.Series(gen_losses).ewm(alpha=1 - smooth).mean().values
        disc_losses = pd.Series(disc_losses).ewm(alpha=1 - smooth).mean().values

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=gen_losses,
            mode="lines",
            name="Generator",
            line=dict(color="deepskyblue"),
            hovertemplate="Step %{x}<br>G Loss: %{y:.4f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            y=disc_losses,
            mode="lines",
            name="Discriminator",
            line=dict(color="crimson"),
            hovertemplate="Step %{x}<br>D Loss: %{y:.4f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Step",
        yaxis_title="Loss",
        template=template,
    )
    return fig


def plot_normalized_losses(
    loss_dict: dict,
    title="Normalized Losses",
    normalize_to="max",
    smooth=0.0,
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_white",
):
    import pandas as pd

    fig = go.Figure()

    for name, loss in loss_dict.items():
        loss_np = np.array(loss)
        if normalize_to == "max":
            loss_np = loss_np / np.max(loss_np)
        elif normalize_to == "first":
            loss_np = loss_np / (loss_np[0] + 1e-8)
        elif normalize_to == "mean":
            loss_np = loss_np / np.mean(loss_np)

        if smooth > 0:
            loss_np = pd.Series(loss_np).ewm(alpha=1 - smooth).mean().values

        fig.add_trace(
            go.Scatter(
                y=loss_np,
                mode="lines",
                name=name,
                hovertemplate=f"Step %{{x}}<br>{name}: %{{y:.4f}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Step",
        yaxis_title="Normalized Loss",
        template=template,
    )
    return fig


def plot_loss_anomalies(
    losses,
    threshold_std=3.0,
    title="Loss Anomalies",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):

    losses = np.array(losses)
    mean = np.mean(losses)
    std = np.std(losses)
    anomalies = np.where(np.abs(losses - mean) > threshold_std * std)[0]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(len(losses))),
            y=losses,
            mode="lines",
            name="Loss",
            line=dict(color="lightgray"),
            hovertemplate="Step %{x}<br>Loss: %{y:.4f}<extra></extra>",
        )
    )

    if len(anomalies) > 0:
        fig.add_trace(
            go.Scatter(
                x=anomalies,
                y=losses[anomalies],
                mode="markers",
                name="Anomalies",
                marker=dict(color="red", size=8, symbol="x"),
                hovertemplate="Step %{x}<br>Loss: %{y:.4f} ⚠️<extra></extra>",
            )
        )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Step",
        yaxis_title="Loss",
        template=template,
    )
    return fig


def plot_normalized_heatmap(
    matrix,
    x_labels=None,
    y_labels=None,
    title="Normalized Feature Map",
    colorscale="RdBu",
    zmin=-1.0,
    zmax=1.0,
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=x_labels,
            y=y_labels,
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            colorbar=dict(title="Norm Value"),
            hovertemplate="X: %{x}<br>Y: %{y}<br>Val: %{z:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="X",
        yaxis_title="Y",
        template=template,
    )
    return fig


def plot_anomaly_curve(
    signal,
    threshold,
    title="Anomaly Detection Curve",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_white",
    anomaly_color="crimson",
    normal_color="gray",
):

    time = np.arange(len(signal))
    anomalies = np.where(signal > threshold)[0]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time,
            y=signal,
            name="Signal",
            line=dict(color=normal_color),
            hovertemplate="Index: %{x}<br>Value: %{y:.3f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=time[anomalies],
            y=signal[anomalies],
            mode="markers",
            name="Anomaly",
            marker=dict(color=anomaly_color, size=8, symbol="x"),
            hovertemplate="Anomaly @ %{x}<br>Value: %{y:.3f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[time[0], time[-1]],
            y=[threshold, threshold],
            mode="lines",
            name="Threshold",
            line=dict(dash="dash", color="orange"),
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Time Index",
        yaxis_title="Value",
        template=template,
    )
    return fig


def plot_anomaly_mask(
    mask,
    x_labels=None,
    y_labels=None,
    title="Anomaly Mask",
    on_color="red",
    off_color="black",
    template: Union[Literal["plotly_dark", "plotly_white"], str] = "plotly_dark",
):
    custom_colorscale = [[0, off_color], [1, on_color]]

    fig = go.Figure(
        data=go.Heatmap(
            z=mask,
            x=x_labels,
            y=y_labels,
            colorscale=custom_colorscale,
            showscale=False,
            hovertemplate="X: %{x}<br>Y: %{y}<br>State: %{z}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="X",
        yaxis_title="Y",
        template=template,
    )
    return fig


def plot_token_heatmap_grid(
    tokens_ids: List[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    decoded_tokens: List[str] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    token_scores: List[float] = [
        0.9206,
        0.911,
        0.7963,
        0.9423,
        0.2089,
        0.2474,
        0.9381,
        0.0112,
        0.8727,
        0.7906,
    ],
    c_map: CMAP_TP = "deep",
    n_cols: int = 5,
    title: str = "Token Heatmap",
    template="plotly_dark",
):
    import math

    n_tokens = len(tokens_ids)
    n_rows = math.ceil(n_tokens / n_cols)

    # Pad so grid is rectangular
    pad_size = n_rows * n_cols - n_tokens
    tokens_ids = tokens_ids + [None] * pad_size
    decoded_tokens = decoded_tokens + [""] * pad_size
    token_scores = token_scores + [np.nan] * pad_size

    # Reshape into grid
    ids_grid = np.array(tokens_ids).reshape(n_rows, n_cols)
    txts_grid = np.array(decoded_tokens).reshape(n_rows, n_cols)
    scores_grid = np.array(token_scores).reshape(n_rows, n_cols)

    # Build hover text
    hover_grid = np.empty_like(txts_grid, dtype=object)
    for i in range(n_rows):
        for j in range(n_cols):
            if ids_grid[i, j] is None:
                hover_grid[i, j] = ""
            else:
                hover_grid[i, j] = (
                    f"Token: {txts_grid[i, j]}<br>"
                    f"ID: {ids_grid[i, j]}<br>"
                    f"Score: {scores_grid[i, j]:.4f}"
                )

    # Create heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=scores_grid,
            text=txts_grid,  # show tokens in cells
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverinfo="text",
            customdata=hover_grid,
            hovertemplate="%{customdata}<extra></extra>",
            colorscale=c_map,
            colorbar=dict(title="Score"),
        )
    )

    fig.update_layout(
        title=title,
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False, autorange="reversed"),
        height=300 + n_rows * 30,
        template=template,
    )
    return fig


def plot_to_image(image):
    """for plots of matplotlib"""
    from io import BytesIO
    import PIL.Image

    buf = BytesIO()
    image.savefig(buf, format="png", bbox_inches="tight")
    return PIL.Image(buf)


def get_image(
    image_tensor: Union[Tensor, np.ndarray],
    c_map: Optional[CMAP_TP] = None,
    width: Optional[Number] = None,
    height: Optional[Number] = None,
    title: Optional[str] = None,
    color_first: bool = True,
    return_plot: bool = False,
    template: Optional[Union[Literal["plotly_dark"]]] = None,
    scale_factor: Number = 1.0,
    x_axes_visible: bool = False,
    y_axes_visible: bool = False,
):
    import PIL.Image
    from io import BytesIO
    import torch

    if not isinstance(image_tensor, Tensor):
        image_tensor = torch.as_tensor(image_tensor)
    else:
        image_tensor = image_tensor.clone().detach().cpu()
    if image_tensor.ndim == 4:
        # dont process batched
        image_tensor = image_tensor[0, ...]
    if color_first:
        image_tensor = image_tensor.permute(1, 2, 0)
    H, W, C = image_tensor.shape
    image_tensor = image_tensor.numpy(force=True)

    top_space = 2
    if isinstance(title, str):
        if not title.strip():
            title = None
        else:
            top_space = 48

    if width is None:
        width = W
    if height is None:
        height = H

    image = px.imshow(
        image_tensor,
        color_continuous_scale=c_map,
        title=title,
        width=width,
        height=height,
    )
    image.update_layout(
        width=width * scale_factor,
        height=height * scale_factor,
        margin={"l": 2, "r": 2, "t": top_space, "b": 2},
        template=template,
    )
    image.update_xaxes(visible=x_axes_visible)
    image.update_yaxes(visible=y_axes_visible)
    if return_plot:
        return image
    return PIL.Image.open(BytesIO(image.to_image()))
