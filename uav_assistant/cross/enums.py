import enum

class WaypointRole(enum.StrEnum):
    REQUIRED = "REQUIRED"
    START = "START"
    END = "END"
    STATION = "STATION"

class Status(enum.StrEnum):
    COMPLETE = "COMPLETE"
    PENDING = "PENDING"

