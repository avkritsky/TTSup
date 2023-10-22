from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.security import get_current_user
from src.backend.db.models import User
from src.backend.db.sessions import database

router = APIRouter(
    prefix='/tickets',
    tags=[
        'tickets',
    ],
)


@router.post('')
async def create_new_ticket(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(database.new_session),
):
    return {}
