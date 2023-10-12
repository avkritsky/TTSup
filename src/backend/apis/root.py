from fastapi import APIRouter

from src.backend.apis.v1 import root


router = APIRouter(
    prefix='/',
)

# import v1 router
router.include_router(root.router)
