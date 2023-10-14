from fastapi import APIRouter, Depends

from src.backend.db import session, repository
from src.backend.schemas import schemas_auth


router = APIRouter(
    prefix='/auth',
    tags=[
        'auth',
    ],
)


@router.post(
    '/',
    response_model=schemas_auth.NewUserResult,
    responses={
        '409': {
            'description': 'Login already used (may be)',
            'model': schemas_auth.ErrorNewUser,
        },
    }
)
async def create_user(
        source: schemas_auth.NewUser,
        db: session.AsyncSession = Depends(session.database.new_session),
):
    res = await repository.users.create_new_user(source, db)
    return res
