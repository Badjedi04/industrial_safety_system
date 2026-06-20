import os
from typing import List

import matplotlib.pyplot as plt
import pandas as pd


METRICS_FILE = "data/performance_metrics.csv"
OUTPUT_DIR = "data/graphs"


def ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_plot(filename: str) -> None:
    ensure_output_dir()
    output_path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")


def require_columns(df: pd.DataFrame, columns: List[str]) -> bool:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        print(f"Skipping graph because columns are missing: {missing}")
        return False
    return True


def plot_fps(df: pd.DataFrame) -> None:
    if not require_columns(df, ["frame_number", "fps"]):
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["frame_number"], df["fps"])
    plt.xlabel("Frame Number")
    plt.ylabel("FPS")
    plt.title("Frames Per Second Over Time")
    plt.grid(True)
    save_plot("fps_over_time.png")


def plot_frame_latency(df: pd.DataFrame) -> None:
    if not require_columns(df, ["frame_number", "frame_processing_time_ms"]):
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["frame_number"], df["frame_processing_time_ms"])
    plt.xlabel("Frame Number")
    plt.ylabel("Latency (ms)")
    plt.title("Frame Processing Latency")
    plt.grid(True)
    save_plot("frame_processing_latency.png")


def plot_ppe_latency(df: pd.DataFrame) -> None:
    if not require_columns(df, ["frame_number", "ppe_detection_time_ms"]):
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["frame_number"], df["ppe_detection_time_ms"])
    plt.xlabel("Frame Number")
    plt.ylabel("PPE Detection Time (ms)")
    plt.title("Computer Vision Inference Latency")
    plt.grid(True)
    save_plot("ppe_detection_latency.png")


def plot_cpu_usage(df: pd.DataFrame) -> None:
    if not require_columns(df, ["frame_number", "cpu_percent"]):
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["frame_number"], df["cpu_percent"])
    plt.xlabel("Frame Number")
    plt.ylabel("CPU Usage (%)")
    plt.title("CPU Usage Over Time")
    plt.grid(True)
    save_plot("cpu_usage.png")


def plot_memory_usage(df: pd.DataFrame) -> None:
    if not require_columns(df, ["frame_number", "memory_mb"]):
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["frame_number"], df["memory_mb"])
    plt.xlabel("Frame Number")
    plt.ylabel("Memory Usage (MB)")
    plt.title("Memory Usage Over Time")
    plt.grid(True)
    save_plot("memory_usage.png")


def plot_decision_distribution(df: pd.DataFrame) -> None:
    if not require_columns(df, ["decision"]):
        return

    decision_counts = df["decision"].value_counts()
    plt.figure(figsize=(8, 5))
    decision_counts.plot(kind="bar")
    plt.xlabel("Safety Decision")
    plt.ylabel("Number of Frames")
    plt.title("Distribution of Safety Decisions")
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y")
    save_plot("decision_distribution.png")


def plot_sensor_values(df: pd.DataFrame) -> None:
    columns = ["frame_number", "gas", "temperature", "vibration"]
    if not require_columns(df, columns):
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["frame_number"], df["gas"], label="Gas")
    plt.plot(df["frame_number"], df["temperature"], label="Temperature")
    plt.plot(df["frame_number"], df["vibration"], label="Vibration")
    plt.xlabel("Frame Number")
    plt.ylabel("Sensor Value")
    plt.title("Sensor Values Over Time")
    plt.legend()
    plt.grid(True)
    save_plot("sensor_values_over_time.png")


def plot_detection_counts(df: pd.DataFrame) -> None:
    columns = [
        "frame_number",
        "num_ppe_detections",
        "num_fall_detections",
        "num_zone_detections",
    ]
    if not require_columns(df, columns):
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["frame_number"], df["num_ppe_detections"], label="PPE Detections")
    plt.plot(df["frame_number"], df["num_fall_detections"], label="Fall Detections")
    plt.plot(df["frame_number"], df["num_zone_detections"], label="Zone Detections")
    plt.xlabel("Frame Number")
    plt.ylabel("Detection Count")
    plt.title("Detection Counts Over Time")
    plt.legend()
    plt.grid(True)
    save_plot("detection_counts_over_time.png")


def plot_processing_stage_average(df: pd.DataFrame) -> None:
    stage_columns = [
        "sensor_read_time_ms",
        "frame_read_time_ms",
        "ppe_detection_time_ms",
        "fall_detection_time_ms",
        "zone_detection_time_ms",
        "fusion_time_ms",
        "alert_time_ms",
        "logging_time_ms",
        "annotation_time_ms",
        "display_time_ms",
    ]
    available_columns = [column for column in stage_columns if column in df.columns]
    if not available_columns:
        print("Skipping processing stage graph because no stage timing columns were found.")
        return

    averages = df[available_columns].mean().sort_values(ascending=False)
    plt.figure(figsize=(11, 5))
    averages.plot(kind="bar")
    plt.xlabel("Processing Stage")
    plt.ylabel("Average Time (ms)")
    plt.title("Average Processing Time by Pipeline Stage")
    plt.xticks(rotation=35, ha="right")
    plt.grid(axis="y")
    save_plot("average_processing_stage_time.png")


def save_summary_table(df: pd.DataFrame) -> None:
    ensure_output_dir()
    metric_map = {
        "Average FPS": "fps",
        "Minimum FPS": "fps",
        "Maximum FPS": "fps",
        "Average Frame Latency (ms)": "frame_processing_time_ms",
        "Average PPE Detection Time (ms)": "ppe_detection_time_ms",
        "Average Fusion Time (ms)": "fusion_time_ms",
        "Average Alert Time (ms)": "alert_time_ms",
        "Average Logging Time (ms)": "logging_time_ms",
        "Average CPU Usage (%)": "cpu_percent",
        "Average Memory Usage (MB)": "memory_mb",
    }

    rows = []
    for label, column in metric_map.items():
        if column not in df.columns:
            continue
        if label.startswith("Minimum"):
            value = df[column].min()
        elif label.startswith("Maximum"):
            value = df[column].max()
        else:
            value = df[column].mean()
        rows.append({"Metric": label, "Value": round(float(value), 3)})

    rows.append({"Metric": "Total Frames", "Value": len(df)})
    summary_df = pd.DataFrame(rows)
    output_path = os.path.join(OUTPUT_DIR, "performance_summary_table.csv")
    summary_df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")


def main() -> None:
    if not os.path.exists(METRICS_FILE):
        raise FileNotFoundError(
            f"Metrics file not found: {METRICS_FILE}. Run main.py first."
        )

    df = pd.read_csv(METRICS_FILE)
    if df.empty:
        raise ValueError("Metrics file is empty. Run the system for more frames.")

    plot_fps(df)
    plot_frame_latency(df)
    plot_ppe_latency(df)
    plot_cpu_usage(df)
    plot_memory_usage(df)
    plot_decision_distribution(df)
    plot_sensor_values(df)
    plot_detection_counts(df)
    plot_processing_stage_average(df)
    save_summary_table(df)

    print("All research performance graphs generated successfully.")


if __name__ == "__main__":
    main()
