from pathlib import Path
import pandas as pd
import numpy as np
from typing import List, Optional

from uav_assistant.dtos.ForecastRequest import UAVState


class TelemetryRepository:
    """
    Loads a prepared test dataset ONCE and provides slices of telemetry
    ready for ML inference.

    The ML engines do NOT know about CSV files.
    """

    def __init__(self, csv_path: Path, features: List[str]):
        self.features = features
        if not csv_path.exists():
            raise FileNotFoundError(f"Telemetry CSV not found: {csv_path}")

        df = pd.read_csv(csv_path)
        df = df.sort_values(["flight", "time"]).reset_index(drop=True)
        self.df = df
        self.test_flights = df["flight"].unique()

    def get_random_test_flight(self) -> pd.DataFrame:
        """Selects one random flight from test split."""
        flight = np.random.choice(self.test_flights)
        return self.df[self.df["flight"] == flight].reset_index(drop=True)

    def get_flight_by_id(self, flight_id: int) -> pd.DataFrame:
        """Retrieves a specific flight (if frontend wants to choose)."""
        df = self.df[self.df["flight"] == flight_id]
        if df.empty:
            raise ValueError(f"Flight {flight_id} not found in telemetry dataset.")
        return df.reset_index(drop=True)

    def prepare_features(self, base_df, uav: UAVState, training_features=None):
        """
        Returns a dataframe with EXACTLY the same columns the MLR model was trained on.
        Missing columns get filled with 0.
        Some columns (wind_speed, payload, etc.) get overwritten using the UAVState.
        """

        df = base_df.copy()

        # Overwrite columns that exist both in training data and UAVState
        replacements = {
            "wind_speed": getattr(uav, "wind_speed", None),
            "payload": getattr(uav, "payload", None),
        }

        for col, value in replacements.items():
            if value is not None and col in df.columns:
                df[col] = value

        # Create final output with exact training columns
        out = {}

        for col in training_features:
            if col in df.columns:
                out[col] = df[col].fillna(0.0)
            else:
                # Feature missing in telemetry → fill with 0
                out[col] = 0.0

        return pd.DataFrame(out)

