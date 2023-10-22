from fastapi import APIRouter

from src.backend.apis.v1.auth import root_auth
from src.backend.apis.v1.tickets import root_tickets


router = APIRouter(
    prefix='/v1',
    tags=[
        'v1',
    ],
)


# include auth router
router.include_router(root_auth.router)

# include tickets router
router.include_router(root_tickets.router)
