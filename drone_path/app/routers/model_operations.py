from typing import List
from drone_path.app.db.models import Waypoint

def get_coords_by_id(waypoints: List[Waypoint], wp_id: int) -> tuple:
    for wp in waypoints:
        if wp.id == wp_id:
            return wp.latitude, wp.longitude
    return 0.0, 0.0