from pathlib import Path
from uav_assistant.services.telemetry_repository import TelemetryRepository

def test_reset_and_step(tmp_path):
    csv = Path("data/test_dataset.csv")
    repo = TelemetryRepository(csv)

    repo.reset()
    assert repo.state is not None

    df = repo.step(5)
    assert df.shape[0] == 1
    assert "speed_h_ms" in df.columns
