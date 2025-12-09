from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from uav_assistant.cross.enums import WaypointRole
from sqlalchemy import (
    Integer,
    String,
    Enum as SqlEnum,
    Index,
    UniqueConstraint,
    Float,
    ForeignKey,
)

class Base(DeclarativeBase):
    pass

class Waypoint(Base):
    __tablename__ = "waypoints"
    __table_args__ = (
        UniqueConstraint("name", "latitude", "longitude", name="uq_waypoints_name_lat_lon"),
        Index("ix_waypoints_role", "role"),
        Index("ix_waypoints_lat_lon", "latitude", "longitude"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
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
        default=WaypointRole.REQUIRED,
        server_default="REQUIRED",
    )
    loss_chance: Mapped[float] = mapped_column(Float, nullable=False, default=0.2, server_default="0.2")

    def __repr__(self) -> str:
        return (
            f"Waypoint(id={self.id}, name={self.name}, "
            f"lat={self.latitude}, lon={self.longitude} role={self.role})"
        )

class Drone(Base):
    __tablename__ = "drones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        server_default="Unnamed Drone",
    )
    speed: Mapped[float] = mapped_column(Float, nullable=False, server_default="4.0")   # m/s
    payload: Mapped[float] = mapped_column(Float, nullable=False, server_default="4.0") # kg

class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    start_waypoint_id: Mapped[int] = mapped_column(
        ForeignKey("waypoints.id"),
        nullable=False,
    )
    end_waypoint_id: Mapped[int] = mapped_column(
        ForeignKey("waypoints.id"),
        nullable=False,
    )

    path_size: Mapped[int] = mapped_column(Integer, nullable=False)

    algo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="GA",
        server_default="GA",
    )

    generations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
        server_default="30",
    )
    population_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=20,
        server_default="20",
    )

    best_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="COMPLETED",
        server_default="COMPLETED",
    )

class Path(Base):
    __tablename__ = "paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(
        ForeignKey("missions.id"),
        nullable=False,
    )

    generation: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    distance_m: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")

class PathWaypoint(Base):
    __tablename__ = "path_waypoints"
    __table_args__ = (
        UniqueConstraint("path_id", "seq", name="uq_path_points_path_seq"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    path_id: Mapped[int] = mapped_column(
        ForeignKey("paths.id"),
        nullable=False,
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    waypoint_id: Mapped[int] = mapped_column(
        ForeignKey("waypoints.id"),
        nullable=False,
    )

class MissionWaypoint(Base):
    __tablename__ = "mission_waypoints"
    __table_args__ = (
        UniqueConstraint("mission_id", "waypoint_id", name="uq_mission_waypoint"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    mission_id: Mapped[int] = mapped_column(
        ForeignKey("missions.id"),
        nullable=False,
    )

    waypoint_id: Mapped[int] = mapped_column(
        ForeignKey("waypoints.id"),
        nullable=False,
    )

class MissionDrone(Base):
    __tablename__ = "mission_drones"
    __table_args__ = (
        UniqueConstraint("mission_id", "drone_id", name="uq_mission_drone"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    mission_id: Mapped[int] = mapped_column(
        ForeignKey("missions.id"),
        nullable=False,
    )

    drone_id: Mapped[int] = mapped_column(
        ForeignKey("drones.id"),
        nullable=False,
    )
