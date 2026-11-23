from datetime import datetime, timezone
from pathlib import Path
from platformdirs import user_data_dir
from sqlalchemy import create_engine, String, Integer, Float, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATA_DIR = Path(user_data_dir("CyberGuardian", "CyberGuardian"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{(DATA_DIR / 'cyberguardian.db').as_posix()}",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class SecurityEvent(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    severity: Mapped[str] = mapped_column(String(20), index=True)
    source: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(200))
    details: Mapped[str] = mapped_column(Text, default="")


class SecurityAlert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    severity: Mapped[str] = mapped_column(String(20), index=True)
    title: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(80))
    details: Mapped[str] = mapped_column(Text, default="")
    occurrences: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", index=True)


class ScanRecord(Base):
    __tablename__ = "scans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    target: Mapped[str] = mapped_column(String(255))
    scan_type: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(30))
    findings_count: Mapped[int] = mapped_column(Integer, default=0)


class ProcessSnapshot(Base):
    __tablename__ = "processes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    pid: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(255))
    cpu_percent: Mapped[float] = mapped_column(Float, default=0)
    memory_percent: Mapped[float] = mapped_column(Float, default=0)


class ConnectionSnapshot(Base):
    __tablename__ = "connections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    protocol: Mapped[str] = mapped_column(String(10))
    local_address: Mapped[str] = mapped_column(String(100), default="")
    remote_address: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(30), default="")
    pid: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ReportRecord(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    format: Mapped[str] = mapped_column(String(10))
    file_path: Mapped[str] = mapped_column(Text)


class AppSetting(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


def initialize_database():
    Base.metadata.create_all(engine)
