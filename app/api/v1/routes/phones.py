from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.api.schemas import PhoneListResponse, PhoneResponse
from app.database.crud import get_all_phones
from app.database.models import PhoneSpec


router = APIRouter(prefix="/phones", tags=["Samsung Phone Catalog"])



@router.get("/", response_model=PhoneListResponse, status_code=status.HTTP_200_OK)
def list_phones(
	skip: int = Query(default=0, ge=0),
	limit: int = Query(default=50, ge=1, le=100),
	db: Session = Depends(get_db_session),
):
	all_phones = get_all_phones(db)
	return PhoneListResponse(total_count=len(all_phones), phones=all_phones[skip : skip + limit])


@router.get("/{model_name}", response_model=PhoneResponse, status_code=status.HTTP_200_OK)
def get_phone(model_name: str, db: Session = Depends(get_db_session)):
	statement = select(PhoneSpec).where(PhoneSpec.model_name.ilike(f"%{model_name.strip()}%"))
	phone = db.execute(statement).scalars().first()
	if not phone:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Phone model '{model_name}' not found in database.",
		)
	return phone
