import json
from typing import Any
from langchain_core.tools import tool
from app.database.connection import get_db
from app.database.models import PhoneSpec
from app.rag.retriever import SamsungRAGRetriever
from app.utils.logger import logger
from sqlalchemy import select

_retriever = SamsungRAGRetriever()


def _phone_to_dict(phone: PhoneSpec) -> dict[str, Any]:
    return {
        "model_name": phone.model_name,
        "release_date": phone.release_date,
        "dimensions": phone.dimensions,
        "weight_g": phone.weight_g,
        "display": {
            "size_inches": phone.display_size_inches,
            "type": phone.display_type,
            "resolution": phone.resolution,
        },
        "hardware": {
            "os": phone.os,
            "chipset": phone.chipset,
            "cpu": phone.cpu,
            "gpu": phone.gpu,
            "storage_ram": phone.storage_ram,
        },
        "cameras": {
            "main_camera": phone.main_camera,
            "selfie_camera": phone.selfie_camera,
        },
        "battery": {
            "capacity_mah": phone.battery_capacity_mah,
            "charging_speed": phone.charging_speed,
        },
        "price": phone.price,
    }


def lookup_phone_specs(model_name: str) -> dict[str, Any] | str:
    """Look up a phone in PostgreSQL, falling back to the existing vector retriever."""
    with get_db() as db:
        statement = select(PhoneSpec).where(
            PhoneSpec.model_name.ilike(f"%{model_name.strip()}%")
        )
        phone = db.execute(statement).scalars().first()
        if phone:
            logger.info(f"Spec tool: found record in DB for '{phone.model_name}'")
            return _phone_to_dict(phone)

    logger.info(f"Spec tool: no direct DB match for '{model_name}', using vector search")
    return _retriever.retrieve(model_name, top_k=2)


@tool
def get_phone_specs_from_db(model_name):
    """Lookup exact technical specifications for a Samsung phone model from PostgreSQL.

    Args:
        model_name: The name or partial name of the Samsung phone (e.g. 'Galaxy
          S23 Ultra', 'S22').
    """
    result = lookup_phone_specs(model_name)
    return json.dumps(result, indent=2) if isinstance(result, dict) else result


@tool
def list_available_phones():
    """Retrieve all available Samsung phone model names currently indexed in the database."""
    with get_db() as db:
        phones = db.query(PhoneSpec.model_name).all()
        names = [p[0] for p in phones]
        return json.dumps({"available_phones": names, "total_count": len(names)})