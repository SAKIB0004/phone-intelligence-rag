from typing import Any, Dict, List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database.models import PhoneSpec
from app.utils.logger import logger


def upsert_phone(db: Session, phone_data) -> PhoneSpec:
    """Insert or update a phone record based on model_name."""
    stmt = insert(PhoneSpec).values(**phone_data)
    update_dict = {
        col.name: stmt.excluded[col.name]
        for col in PhoneSpec.__table__.columns
        if col.name not in ("id", "created_at")
    }

    stmt = stmt.on_conflict_do_update(
        index_elements=["model_name"], set_=update_dict
    )

    db.execute(stmt)
    db.commit()
    logger.info(f"Upserted record for: {phone_data.get('model_name')}")
    return (
        db.query(PhoneSpec)
        .filter(PhoneSpec.model_name == phone_data["model_name"])
        .first()
    )


def get_all_phones(db: Session):
    return db.query(PhoneSpec).all()


def get_phone_by_name(db: Session, model_name: str):
    return (
        db.query(PhoneSpec).filter(PhoneSpec.model_name == model_name).first()
    )