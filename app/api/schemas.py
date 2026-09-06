from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Phone Schemas ---
class PhoneBase(BaseModel):
    model_name: str
    brand: str = "Samsung"
    release_date: Optional[str] = None
    dimensions: Optional[str] = None
    weight_g: Optional[float] = None
    os: Optional[str] = None
    display_type: Optional[str] = None
    display_size_inches: Optional[float] = None
    resolution: Optional[str] = None
    chipset: Optional[str] = None
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    storage_ram: Optional[str] = None
    main_camera: Optional[str] = None
    selfie_camera: Optional[str] = None
    battery_capacity_mah: Optional[int] = None
    charging_speed: Optional[str] = None
    price: Optional[str] = None


class PhoneResponse(PhoneBase):
    id: int
    source_url: str
    image_url: Optional[str] = None
    raw_specs: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PhoneListResponse(BaseModel):
    total_count: int
    phones: List[PhoneResponse]


# --- RAG Chatbot Schemas ---
class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        json_schema_extra={"example": "What is the camera setup on the Galaxy S23 Ultra?"},
    )
    reset_history: bool = Field(default=False, description="Clear conversation memory before generating response")


class ChatResponse(BaseModel):
    query: str
    response: str


# --- Multi-Agent Review Schemas ---
class ReviewRequest(BaseModel):
    phone_name: Optional[str] = Field(
        default=None,
        min_length=2,
        json_schema_extra={"example": "Galaxy S24"},
    )
    query: Optional[str] = Field(default=None, min_length=2)
    review_focus: str = Field(
        default="General Consumer & Performance Review",
        json_schema_extra={"example": "Battery endurance and camera low-light performance"},
    )


class ReviewResponse(BaseModel):
    phone_name: Optional[str] = None
    review_focus: str
    technical_dossier: str
    final_review: str


# --- Health & Status Schemas ---
class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    total_indexed_phones: int
    timestamp: datetime