from fastapi import APIRouter, Depends

from src.backend.db import session


router = APIRouter(
    prefix='/auth',
    tags=[
        'auth',
    ],
)


@router.post('/')
async def create_user(
        db: session.AsyncSession = Depends(session.new_session),
):
    pass
