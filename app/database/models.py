from datetime import datetime
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PhoneSpec(Base):
    __tablename__ = "samsung_phones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False, unique=True, index=True)
    brand = Column(String(100), default="Samsung", nullable=False)
    source_url = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=True)

    # Key Specifications
    release_date = Column(String(100), nullable=True)
    dimensions = Column(String(150), nullable=True)
    weight_g = Column(Float, nullable=True)
    os = Column(String(200), nullable=True)
    display_type = Column(String(200), nullable=True)
    display_size_inches = Column(Float, nullable=True)
    resolution = Column(String(150), nullable=True)
    chipset = Column(String(200), nullable=True)
    cpu = Column(String(250), nullable=True)
    gpu = Column(String(150), nullable=True)
    storage_ram = Column(String(250), nullable=True)
    main_camera = Column(Text, nullable=True)
    selfie_camera = Column(Text, nullable=True)
    battery_capacity_mah = Column(Integer, nullable=True)
    charging_speed = Column(String(200), nullable=True)
    price = Column(String(100), nullable=True)

    # Full raw specs mapped as key-value pairs
    raw_specs = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )