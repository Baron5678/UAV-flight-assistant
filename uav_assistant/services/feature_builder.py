import pandas as pd

from uav_assistant.dtos.ForecastRequest import UAVState

class FeatureBuilder:
    @staticmethod
    def add_is_flying(df):
        df = df.copy()
        if "speed_h_ms" in df.columns and "alt" in df.columns:
            df["is_flying"] = (
                (df["speed_h_ms"] > 0.1) | (df["alt"] > 1)
            ).astype(int)
        else:
            df["is_flying"] = 1

        return df
    
    @staticmethod
    def insert_uav_state(df: pd.DataFrame, uav: UAVState, training_features: list):
        df = df.copy()
        
        if "wind_speed" in df:
            df["wind_speed"] = uav.wind_speed
        if "payload" in df:
            df["payload"] = uav.payload

        out = {}
        for f in training_features:
            out[f] = df[f].iloc[0] if f in df else 0.0

        return pd.DataFrame([out])

