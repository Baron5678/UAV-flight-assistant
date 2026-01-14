from pathlib import Path
import random
import pandas as pd
import numpy as np
from typing import List, Optional

from uav_assistant.dtos.ForecastRequest import UAVState


class TelemetryRepository:
    def __init__(self, csv_path: Path):
        df = pd.read_csv(csv_path)
        df = df.sort_values(["flight", "time"]).reset_index(drop=True)

        df["_airborne"] = (
            (df["speed_h_ms"] > 0.1) | (df["alt"] > 1)
        )

        self.state: pd.Series | None = None
        self.flight_groups = {
            f: g.reset_index(drop=True)
            for f, g in df.groupby("flight")
            if g["_airborne"].sum() > 20
        }


    def reset(self):
        flight_id = random.choice(list(self.flight_groups.keys()))
        df = self.flight_groups[flight_id]
        flying = df[df["_airborne"]]

        start = int(0.05 * len(flying))
        end = int(0.6 * len(flying))
        idx = random.randint(start, end)

        self.state = flying.iloc[idx].drop("_airborne").copy()


    def step(self, dt: float) -> pd.DataFrame:
        """
        Advance telemetry state by dt seconds.
        """
        if self.state is None:
            self.reset()

        s = self.state.copy()
        s["time"] += dt

        s["speed_h_ms"] = max(
            0.0,
            s["speed_h_ms"] + np.random.normal(0, 0.1)
        )

        s["alt"] += (
            s.get("velocity_z", 0.0) * dt +
            np.random.normal(0, 0.2)
        )

        if s["alt"] < 0:
            s["alt"] = 0

        self.state = s
        return pd.DataFrame([s])