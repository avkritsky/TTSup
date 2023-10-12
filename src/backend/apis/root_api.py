from fastapi import APIRouter

from src.backend.apis.v1 import root_one


router = APIRouter(
    prefix='',
)

# import v1 router
router.include_router(root_one.router)
