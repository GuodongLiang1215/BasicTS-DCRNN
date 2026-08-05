"""Plot DCRNN forecasts against METR-LA ground truth.

BasicTS writes these result files with ``numpy.memmap`` in the version used
for this reproduction. They are raw binary arrays even though their filenames
end in ``.npy``.
"""

from argparse import ArgumentParser
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


NUM_STEPS = 12
NUM_SENSORS = 207
NUM_FEATURES = 1
DTYPE = np.float32


def parse_args():
    parser = ArgumentParser(
        description="Plot DCRNN predictions against METR-LA ground truth."
    )
    parser.add_argument(
        "--result-dir",
        type=Path,
        required=True,
        help="Directory containing predictions.npy and targets.npy.",
    )
    parser.add_argument(
        "--sensor",
        type=int,
        default=0,
        help="Sensor index to plot (default: 0).",
    )
    parser.add_argument(
        "--start-sample",
        type=int,
        default=0,
        help="First test sample to plot (default: 0).",
    )
    parser.add_argument(
        "--num-points",
        type=int,
        default=288,
        help="Number of five-minute samples to plot (default: 288 = 24 hours).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output PNG path. Defaults to visualizations/dcrnn_sensor_<index>_comparison.png.",
    )
    return parser.parse_args()


def infer_shape(path: Path):
    bytes_per_sample = (
        np.dtype(DTYPE).itemsize * NUM_STEPS * NUM_SENSORS * NUM_FEATURES
    )
    file_size = path.stat().st_size
    if file_size % bytes_per_sample != 0:
        raise ValueError(
            f"Unexpected file size for {path}. The file is not compatible with "
            f"shape (*, {NUM_STEPS}, {NUM_SENSORS}, {NUM_FEATURES}) and {DTYPE}."
        )
    num_samples = file_size // bytes_per_sample
    return (num_samples, NUM_STEPS, NUM_SENSORS, NUM_FEATURES)


def main():
    args = parse_args()

    prediction_path = args.result_dir / "predictions.npy"
    target_path = args.result_dir / "targets.npy"
    if not prediction_path.is_file() or not target_path.is_file():
        raise FileNotFoundError(
            "The result directory must contain predictions.npy and targets.npy."
        )

    shape = infer_shape(target_path)
    expected_bytes = int(np.prod(shape)) * np.dtype(DTYPE).itemsize
    if prediction_path.stat().st_size != expected_bytes:
        raise ValueError("Predictions and targets do not have matching sizes.")

    if not 0 <= args.sensor < NUM_SENSORS:
        raise ValueError(f"Sensor must be between 0 and {NUM_SENSORS - 1}.")
    if args.start_sample < 0 or args.start_sample >= shape[0]:
        raise ValueError(f"start-sample must be between 0 and {shape[0] - 1}.")
    if args.num_points <= 0:
        raise ValueError("num-points must be greater than zero.")

    predictions = np.memmap(
        prediction_path,
        dtype=DTYPE,
        mode="r",
        shape=shape,
    )
    targets = np.memmap(
        target_path,
        dtype=DTYPE,
        mode="r",
        shape=shape,
    )

    end_sample = min(args.start_sample + args.num_points, shape[0])
    num_points = end_sample - args.start_sample
    time_hours = np.arange(num_points) * 5 / 60
    horizons = [
        (2, "15-minute forecast"),
        (5, "30-minute forecast"),
        (11, "60-minute forecast"),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)

    for ax, (horizon_index, title) in zip(axes, horizons):
        actual = np.asarray(
            targets[
                args.start_sample:end_sample,
                horizon_index,
                args.sensor,
                0,
            ]
        )
        predicted = np.asarray(
            predictions[
                args.start_sample:end_sample,
                horizon_index,
                args.sensor,
                0,
            ]
        )

        # METR-LA uses zero for missing traffic observations.
        valid = np.isfinite(actual) & np.isfinite(predicted) & (actual > 0)
        if not np.any(valid):
            raise ValueError(
                f"No valid observations for sensor {args.sensor} at horizon "
                f"{horizon_index + 1}."
            )

        actual_plot = np.where(valid, actual, np.nan)
        predicted_plot = np.where(valid, predicted, np.nan)
        mae = np.mean(np.abs(actual[valid] - predicted[valid]))

        ax.plot(
            time_hours,
            actual_plot,
            label="Ground truth",
            color="#1565C0",
            linewidth=1.8,
        )
        ax.plot(
            time_hours,
            predicted_plot,
            label="DCRNN prediction",
            color="#E53935",
            linewidth=1.5,
        )
        ax.set_title(f"{title} | MAE = {mae:.3f}")
        ax.set_ylabel("Speed (mph)")
        ax.grid(alpha=0.25)
        ax.legend()

    axes[-1].set_xlabel("Test time (hours)")
    fig.suptitle(
        f"DCRNN Prediction vs Ground Truth — Sensor {args.sensor}",
        fontsize=15,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    output_path = args.output or Path(
        f"visualizations/dcrnn_sensor_{args.sensor}_comparison.png"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

    print("Data shape:", shape)
    print("Figure saved to:", output_path.resolve())


if __name__ == "__main__":
    main()
