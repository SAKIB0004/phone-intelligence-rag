from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from app.agents.workflow import workflow
from app.api.schemas import ReviewRequest, ReviewResponse


router = APIRouter(prefix="/agents", tags=["Multi-Agent Review System"])


def _run_workflow(payload: ReviewRequest):
	query = payload.query or f"Review Samsung {payload.phone_name}: {payload.review_focus}"
	return workflow.invoke({
		"query": query,
		"phone_name": payload.phone_name or "",
		"review_focus": payload.review_focus,
	})


@router.post("/review", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
def generate_review(
	payload: ReviewRequest,
):
	state = _run_workflow(payload)
	return ReviewResponse(
		phone_name=payload.phone_name or ", ".join(state.get("phone_names", [])) or None,
		review_focus=payload.review_focus,
		technical_dossier=state.get("technical_dossier", state.get("specs_result", "")),
		final_review=state.get("review", ""),
	)


@router.post("/review/stream", status_code=status.HTTP_200_OK)
def stream_review(
	payload: ReviewRequest,
):
	state = _run_workflow(payload)
	dossier = state.get("technical_dossier", state.get("specs_result", ""))
	review_stream = iter([state.get("review", "")])

	def event_generator():
		yield f"--- TECHNICAL DOSSIER ---\n{dossier}\n\n--- EDITORIAL REVIEW ---\n"
		yield from review_stream

	return StreamingResponse(event_generator(), media_type="text/plain")
