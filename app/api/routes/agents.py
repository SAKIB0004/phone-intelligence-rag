from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from app.api.dependencies import get_review_orchestrator
from app.api.schemas import ReviewRequest, ReviewResponse
from app.agents.workflow import SamsungReviewOrchestrator

router = APIRouter(prefix="/agents", tags=["Multi-Agent Review System"])


@router.post(
    "/review",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a complete multi-agent editorial review (JSON response)",
)
def generate_review(
    payload: ReviewRequest,
    orchestrator: SamsungReviewOrchestrator = Depends(get_review_orchestrator),
):
    """Executes the two-agent sequential workflow:
    1. SpecRetrievalAgent queries database and produces a technical dossier.
    2. ReviewGenerationAgent synthesizes the dossier into an editorial review.
    """
    result = orchestrator.generate_phone_review(
        phone_name=payload.phone_name,
        review_focus=payload.review_focus,
    )
    return ReviewResponse(
        phone_name=payload.phone_name,
        review_focus=payload.review_focus,
        technical_dossier=result["technical_dossier"],
        final_review=result["final_review"],
    )


@router.post(
    "/review/stream",
    status_code=status.HTTP_200_OK,
    summary="Stream multi-agent review generation in real-time",
)
def stream_review(
    payload: ReviewRequest,
    orchestrator: SamsungReviewOrchestrator = Depends(get_review_orchestrator),
):
    """Retrieves technical dossier upfront, then streams the generated review tokens in real time."""
    spec_dossier, review_stream = orchestrator.stream_phone_review(
        phone_name=payload.phone_name,
        review_focus=payload.review_focus,
    )

    def event_generator():
        yield f"--- TECHNICAL DOSSIER ---\n{spec_dossier}\n\n--- EDITORIAL REVIEW ---\n"
        for token in review_stream:
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")