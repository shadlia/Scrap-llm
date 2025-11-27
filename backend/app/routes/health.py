from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Welcome to Scrap LLM API!"}


@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@router.get("/ready", tags=["Health"])
def ready_check():
    return {"status": "ok"}
