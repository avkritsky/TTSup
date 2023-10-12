from fastapi import APIRouter

from src.backend.apis.v1.auth import root_auth


router = APIRouter(
    prefix='/v1',
    tags=[
        'v1',
    ],
)


# include auth router
router.include_router(root_auth.router)
