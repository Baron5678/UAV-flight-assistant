from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    Integer,
    String,
    Float,
    ForeignKey,
    UniqueConstraint,
    Index,
)

from uav_assistant.cross.enums import WaypointRole

class Base(DeclarativeBase):
    pass


class Waypoint(Base):
    __tablename__ = "waypoints"
    __table_args__ = (
        UniqueConstraint(
            "name", "latitude", "longitude",
            name="uq_waypoints_name_lat_lon",
        ),
        Index("ix_waypoints_role", "role"),
        Index("ix_waypoints_lat_lon", "latitude", "longitude"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=WaypointRole.REQUIRED,
        server_default=WaypointRole.REQUIRED,
    )

    wind_speed: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=20.0,
        server_default="20.0",
    )

    wind_direction: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=20.0,
        server_default="20.0",
    )

    def __repr__(self) -> str:
        return (
            f"Waypoint(id={self.id}, name={self.name}, "
            f"lat={self.latitude}, lon={self.longitude}, role={self.role})"
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

    speed: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        server_default="4.0",
    )

    payload: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        server_default="4.0",
    )

class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    start_waypoint_id: Mapped[int] = mapped_column(
        ForeignKey("waypoints.id", ondelete="CASCADE"),
        nullable=False,
    )

    end_waypoint_id: Mapped[int] = mapped_column(
        ForeignKey("waypoints.id", ondelete="CASCADE"),
        nullable=False,
    )

    path_size: Mapped[int] = mapped_column(Integer, nullable=False)

    algo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="GA",
        server_default="GA",
    )

    objective: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="DISTANCE",
        server_default="DISTANCE",
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

    seed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=127,
        server_default="127",
    )
    mutation_probability: Mapped[int] = mapped_column(
        Float,
        nullable=False,
        default=20,
        server_default="0.1",
    )

    keep_elitism: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
        server_default="10",
    )

    k_tournament: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        server_default="3",
    )

    sigma0: Mapped[int] = mapped_column(
        Float,
        nullable=False,
        default=0.25,
        server_default="0.25",
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
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )

    generation: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
    )

    distance_m: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
    )

class PathSummary(Base):
    __tablename__ = "path_summaries"
    __table_args__ = (
        Index("ix_path_summaries_mission_gen", "mission_id", "generation"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    mission_id: Mapped[int] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )

    generation: Mapped[int] = mapped_column(Integer, nullable=False)

    cost: Mapped[float] = mapped_column(Float, nullable=False)

    total_distance_m: Mapped[float] = mapped_column(Float, nullable=False)

class PathWaypoint(Base):
    __tablename__ = "path_waypoints"
    __table_args__ = (
        UniqueConstraint("path_id", "seq", name="uq_path_points_path_seq"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    path_id: Mapped[int] = mapped_column(
        ForeignKey("paths.id", ondelete="CASCADE"),
        nullable=False,
    )

    seq: Mapped[int] = mapped_column(Integer, nullable=False)

    waypoint_id: Mapped[int] = mapped_column(
        ForeignKey("waypoints.id", ondelete="CASCADE"),
        nullable=False,
    )

class MissionWaypoint(Base):
    __tablename__ = "mission_waypoints"
    __table_args__ = (
        UniqueConstraint("mission_id", "waypoint_id", name="uq_mission_waypoint"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    mission_id: Mapped[int] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )

    waypoint_id: Mapped[int] = mapped_column(
        ForeignKey("waypoints.id", ondelete="CASCADE"),
        nullable=False,
    )

class MissionDrone(Base):
    __tablename__ = "mission_drones"
    __table_args__ = (
        UniqueConstraint("mission_id", "drone_id", name="uq_mission_drone"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    mission_id: Mapped[int] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )

    drone_id: Mapped[int] = mapped_column(
        ForeignKey("drones.id", ondelete="CASCADE"),
        nullable=False,
    )
