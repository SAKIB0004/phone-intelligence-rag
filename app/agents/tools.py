import json
from typing import Optional
from langchain_core.tools import tool
from app.database.connection import get_db
from app.database.models import PhoneSpec
from app.rag.retriever import SamsungRAGRetriever
from app.utils.logger import logger
from sqlalchemy import select

_retriever = SamsungRAGRetriever()


@tool
def get_phone_specs_from_db(model_name):
    """Lookup exact technical specifications for a Samsung phone model from PostgreSQL.

    Args:
        model_name: The name or partial name of the Samsung phone (e.g. 'Galaxy
          S23 Ultra', 'S22').
    """
    with get_db() as db:
        # 1. Direct ILIKE search
       

        stmt = select(PhoneSpec).where(PhoneSpec.model_name.ilike(f"%{model_name.strip()}%"))

        phone = db.execute(stmt).scalars().first()

        if phone:
            spec_dict = {
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
            logger.info(f"Spec Tool: Found record in DB for '{phone.model_name}'")
            return json.dumps(spec_dict, indent=2)

    # 2. Vector search fallback
    logger.info(f"Spec Tool: Direct DB match not found for '{model_name}'. Trying vector search.")
    fallback_context = _retriever.retrieve(model_name, top_k=2)
    return fallback_context


@tool
def list_available_phones():
    """Retrieve all available Samsung phone model names currently indexed in the database."""
    with get_db() as db:
        phones = db.query(PhoneSpec.model_name).all()
        names = [p[0] for p in phones]
        return json.dumps({"available_phones": names, "total_count": len(names)})