from fastapi import APIRouter, status

from app.scraper.pipeline import run_pipeline


router = APIRouter(prefix="/scraper", tags=["Samsung Phone Scraper"])


@router.post("/run", status_code=status.HTTP_200_OK)
def run_scraper():
	return run_pipeline()
