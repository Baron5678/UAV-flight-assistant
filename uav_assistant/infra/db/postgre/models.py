from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Integer,
    String,
    Float,
    ForeignKey,
    UniqueConstraint,
    Index, Table, Column, text,
)

from uav_assistant.cross.enums import WaypointRole


class Base(DeclarativeBase):
    pass

missions_drones = Table(
    "missions_drones",
    Base.metadata,
    Column("mission_id", ForeignKey("missions.id", ondelete="CASCADE"), primary_key=True),
    Column("drone_id", ForeignKey("drones.id", ondelete="CASCADE"), primary_key=True),
)

class Waypoint(Base):
    __tablename__ = "waypoints"
    __table_args__ = (
        UniqueConstraint(
            "mission_id", "name", "latitude", "longitude",
            name="uq_waypoints_mission_name_lat_lon",
        ),
        Index("ix_waypoints_mission_id", "mission_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id", ondelete="CASCADE"),nullable=False)
    mission: Mapped["Mission"] = relationship(back_populates="waypoints")
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=WaypointRole.REQUIRED,
        server_default="REQUIRED",
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

class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    waypoints: Mapped[list["Waypoint"]] = relationship(back_populates="mission", cascade="all, delete-orphan")
    configs: Mapped[list["AlgorithmConfiguration"]] = relationship(back_populates="mission", cascade="all, delete-orphan")
    drones: Mapped[list["Drone"]] = relationship(secondary=missions_drones, back_populates="missions")
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
    )

class AlgorithmConfiguration(Base):
    __tablename__ = "algorithm_configs"
    __table_args__ = (
        Index("ix_algorithm_configs_mission_id", "mission_id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id", ondelete="CASCADE"),nullable=False)
    mission: Mapped["Mission"] = relationship(back_populates="configs")

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

    parameters: Mapped[dict[str, str]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

class MissionOutcome(Base):
    __tablename__ = "mission_outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    config_id: Mapped[int] = mapped_column(
        ForeignKey("algorithm_configs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    first_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    best_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    min_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    max_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    avg_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    improvement_abs: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    improvement_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    improving_generations: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    last_improvement_generation: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    max_stagnation_generations: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    min_total_distance_m: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    max_total_distance_m: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    avg_total_distance_m: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    mongo_result_id: Mapped[str] = mapped_column(String(100), nullable=False, default="", server_default="")

class Drone(Base):
    __tablename__ = "drones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    missions: Mapped[list["Mission"]] = relationship(
        secondary=missions_drones,
        back_populates="drones",
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        server_default="Unnamed Drone",
    )

    speed: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=4.0,
        server_default="4.0",
    )

    battery_capacity_wh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=200.0,
        server_default="200.0",
    )

    per_meter_wh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=20.0,
        server_default="20.0",
    )
