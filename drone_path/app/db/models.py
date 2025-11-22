import enum
from sqlalchemy import Integer, String, Enum as SqlEnum, Index, UniqueConstraint, Float
from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class WaypointRole(enum.StrEnum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    STATION = "STATION"

class Waypoint(Base):
    __tablename__ = "waypoints"
    __table_args__ = (
        UniqueConstraint("name", "latitude", "longitude", name="uq_waypoints_name_lat_lon"),
        Index("ix_waypoints_role", "role"),
        Index("ix_waypoints_lat_lon", "latitude", "longitude"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    role: Mapped[WaypointRole] = mapped_column(
        SqlEnum(
            WaypointRole,
            name="waypoint_role",
            native_enum=True,
            create_types=False,
            validate_strings=True,
        ),
        nullable=False,
        default=WaypointRole.OPTIONAL,
        server_default="OPTIONAL",
    )
    visits: Mapped[int] = mapped_column(Integer, nullable=False, default=2, server_default="2")
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False, default=4.0, server_default="4")
    loss_chance: Mapped[float] = mapped_column(Float, nullable=False, default=0.2, server_default="0.2")


    def __repr__(self) -> str:
        return f"Waypoint(id={self.id}, name={self.name}, lat={self.latitude}, lon={self.longitude} role={self.role})"

class Drone(Base):
    __tablename__ = "drones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, server_default="Unnamed Drone")
    speed: Mapped[float] = mapped_column(Float, nullable=False, server_default="4.0")  # m/s
    payload: Mapped[float] = mapped_column(Float, nullable=False, server_default="4.0") # kg