# analyze_uav_export.py
# Usage:
#   1) Extract uav_export.zip (or have path_evolve.csv + stats.csv ready)
#   2) python analyze_uav_export.py --path_evolve path_evolve.csv --stats stats.csv
#
# Optional:
#   python analyze_uav_export.py --zip uav_export.zip
#   python analyze_uav_export.py --save_dir out_plots

from __future__ import annotations

import argparse
import os
import zipfile
from io import TextIOWrapper
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def read_from_zip(zip_path: str, member: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as z:
        with z.open(member) as f:
            return pd.read_csv(TextIOWrapper(f, encoding="utf-8"))


def ensure_dir(p: str | None) -> None:
    if not p:
        return
    Path(p).mkdir(parents=True, exist_ok=True)


def save_or_show(fig, save_dir: str | None, filename: str) -> None:
    if save_dir:
        out = Path(save_dir) / filename
        fig.savefig(out, bbox_inches="tight", dpi=160)
        plt.close(fig)
    else:
        plt.show()


def plot_cost_by_mission(path_df: pd.DataFrame, save_dir: str | None) -> None:
    for mid, g in path_df.groupby("mission_id"):
        g = g.sort_values("generation")
        fig = plt.figure()
        plt.plot(g["generation"], g["cost"])
        title = f"Mission {mid} — Cost vs Generation"
        if "algo" in g.columns and "objective" in g.columns:
            algo = str(g["algo"].iloc[0])
            obj = str(g["objective"].iloc[0])
            title = f"Mission {mid} ({algo}, {obj}) — Cost vs Generation"
        plt.title(title)
        plt.xlabel("Generation")
        plt.ylabel("Cost")
        plt.grid(True)
        save_or_show(fig, save_dir, f"mission_{mid}_cost.png")


def plot_distance_by_mission(path_df: pd.DataFrame, save_dir: str | None) -> None:
    for mid, g in path_df.groupby("mission_id"):
        g = g.sort_values("generation")
        fig = plt.figure()
        # distance shown in km for readability
        plt.plot(g["generation"], g["total_distance_m"] / 1000.0)
        title = f"Mission {mid} — Distance vs Generation"
        if "algo" in g.columns and "objective" in g.columns:
            algo = str(g["algo"].iloc[0])
            obj = str(g["objective"].iloc[0])
            title = f"Mission {mid} ({algo}, {obj}) — Distance vs Generation"
        plt.title(title)
        plt.xlabel("Generation")
        plt.ylabel("Distance (km)")
        plt.grid(True)
        save_or_show(fig, save_dir, f"mission_{mid}_distance.png")


def plot_best_so_far_cost(path_df: pd.DataFrame, save_dir: str | None) -> None:
    for mid, g in path_df.groupby("mission_id"):
        g = g.sort_values("generation")
        best_so_far = g["cost"].cummin()

        fig = plt.figure()
        plt.plot(g["generation"], g["cost"], label="Cost")
        plt.plot(g["generation"], best_so_far, label="Best-so-far")
        title = f"Mission {mid} — Cost & Best-so-far"
        if "algo" in g.columns and "objective" in g.columns:
            algo = str(g["algo"].iloc[0])
            obj = str(g["objective"].iloc[0])
            title = f"Mission {mid} ({algo}, {obj}) — Cost & Best-so-far"
        plt.title(title)
        plt.xlabel("Generation")
        plt.ylabel("Cost")
        plt.grid(True)
        plt.legend()
        save_or_show(fig, save_dir, f"mission_{mid}_best_so_far_cost.png")


def plot_overlay_by_algo_objective(path_df: pd.DataFrame, save_dir: str | None) -> None:
    # Requires algo/objective columns in path_evolve.csv
    if "algo" not in path_df.columns or "objective" not in path_df.columns:
        print("Skipping overlay_by_algo_objective: 'algo'/'objective' not found in path_evolve.csv")
        return

    # Overlay cost curves grouped by (algo, objective) for all missions
    for (algo, obj), group in path_df.groupby(["algo", "objective"]):
        fig = plt.figure()
        for mid, g in group.groupby("mission_id"):
            g = g.sort_values("generation")
            plt.plot(g["generation"], g["cost"], label=f"mission {mid}")
        plt.title(f"{algo} / {obj} — Cost vs Generation (all missions)")
        plt.xlabel("Generation")
        plt.ylabel("Cost")
        plt.grid(True)
        plt.legend()
        safe_algo = str(algo).replace("/", "_")
        safe_obj = str(obj).replace("/", "_")
        save_or_show(fig, save_dir, f"overlay_cost_{safe_algo}_{safe_obj}.png")


def plot_final_best_cost_bar(stats_df: pd.DataFrame, save_dir: str | None) -> None:
    # Bar chart of best achieved cost per mission
    col = "best_cost_run" if "best_cost_run" in stats_df.columns else None
    if col is None:
        print("Skipping final_best_cost_bar: 'best_cost_run' not found in stats.csv")
        return

    df = stats_df.copy()
    df = df.dropna(subset=[col])
    df = df.sort_values(col)

    fig = plt.figure()
    plt.bar(df["mission_id"].astype(str), df[col])
    plt.title("Best achieved cost per mission")
    plt.xlabel("Mission ID")
    plt.ylabel("Best cost")
    plt.grid(True, axis="y")
    save_or_show(fig, save_dir, "bar_best_cost_per_mission.png")


def plot_cost_and_distance_same_graph(path_df, save_dir=None):
    """
    One figure per mission:
      - Left Y-axis: cost
      - Right Y-axis: distance (km)
    """

    for mid, g in path_df.groupby("mission_id"):
        g = g.sort_values("generation")

        fig, ax_cost = plt.subplots(figsize=(8, 5))

        # --- Cost (left axis)
        ax_cost.plot(
            g["generation"],
            g["cost"],
            color="tab:blue",
            label="Cost",
            linewidth=2,
        )
        ax_cost.set_xlabel("Generation")
        ax_cost.set_ylabel("Cost", color="tab:blue")
        ax_cost.tick_params(axis="y", labelcolor="tab:blue")
        ax_cost.grid(True)

        # --- Distance (right axis, in km)
        ax_dist = ax_cost.twinx()
        ax_dist.plot(
            g["generation"],
            g["total_distance_m"] / 1000.0,
            color="tab:orange",
            linestyle="--",
            label="Distance (km)",
            linewidth=2,
        )
        ax_dist.set_ylabel("Distance (km)", color="tab:orange")
        ax_dist.tick_params(axis="y", labelcolor="tab:orange")

        # --- Title
        title = f"Mission {mid}"
        if "algo" in g.columns and "objective" in g.columns:
            algo = g["algo"].iloc[0]
            obj = g["objective"].iloc[0]
            title += f" — {algo} / {obj}"
        ax_cost.set_title(title)

        # --- Combined legend
        lines1, labels1 = ax_cost.get_legend_handles_labels()
        lines2, labels2 = ax_dist.get_legend_handles_labels()
        ax_cost.legend(lines1 + lines2, labels1 + labels2, loc="best")

        if save_dir:
            import os
            out = os.path.join(save_dir, f"mission_{mid}_cost_distance.png")
            fig.savefig(out, dpi=160, bbox_inches="tight")
            plt.close(fig)
        else:
            plt.show()

def plot_cost_and_distance_overlay(path_df, save_dir=None):

    if not {"algo", "objective"}.issubset(path_df.columns):
        print("Overlay plot skipped (algo/objective not present)")
        return

    for (algo, obj), group in path_df.groupby(["algo", "objective"]):
        fig, ax_cost = plt.subplots(figsize=(8, 5))
        ax_dist = ax_cost.twinx()

        for mid, g in group.groupby("mission_id"):
            g = g.sort_values("generation")
            ax_cost.plot(
                g["generation"],
                g["cost"],
                linewidth=1.5,
                label=f"M{mid} cost",
            )
            ax_dist.plot(
                g["generation"],
                g["total_distance_m"] / 1000.0,
                linestyle="--",
                linewidth=1.5,
                label=f"M{mid} dist",
            )

        ax_cost.set_xlabel("Generation")
        ax_cost.set_ylabel("Cost")
        ax_dist.set_ylabel("Distance (km)")
        ax_cost.set_title(f"{algo} / {obj} — Cost & Distance evolution")
        ax_cost.grid(True)

        # Legend (combined)
        lines1, labels1 = ax_cost.get_legend_handles_labels()
        lines2, labels2 = ax_dist.get_legend_handles_labels()
        ax_cost.legend(lines1 + lines2, labels1 + labels2, fontsize=8)

        if save_dir:
            safe_algo = str(algo).replace("/", "_")
            safe_obj = str(obj).replace("/", "_")
            out = f"{save_dir}/overlay_cost_distance_{safe_algo}_{safe_obj}.png"
            fig.savefig(out, dpi=160, bbox_inches="tight")
            plt.close(fig)
        else:
            plt.show()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", dest="zip_path", default=None, help="Path to uav_export.zip")
    ap.add_argument("--path_evolve", default=None, help="Path to path_evolve.csv")
    ap.add_argument("--stats", default=None, help="Path to stats.csv")
    ap.add_argument("--save_dir", default=None, help="Directory to save plots (if omitted, shows plots)")
    args = ap.parse_args()

    ensure_dir(args.save_dir)

    if args.zip_path:
        path_df = read_from_zip(args.zip_path, "path_evolve.csv")
        stats_df = read_from_zip(args.zip_path, "stats.csv")
    else:
        if not args.path_evolve or not args.stats:
            raise SystemExit("Provide either --zip or both --path_evolve and --stats")
        path_df = pd.read_csv(args.path_evolve)
        stats_df = pd.read_csv(args.stats)

    # Basic sanity
    required_cols = {"mission_id", "generation", "cost", "total_distance_m"}
    missing = required_cols - set(path_df.columns)
    if missing:
        raise ValueError(f"path_evolve.csv missing columns: {sorted(missing)}")

    # Plots
    plot_cost_and_distance_same_graph(path_df, args.save_dir)
    plot_cost_and_distance_overlay(path_df, args.save_dir)
    print("Done.")


if __name__ == "__main__":
    main()
