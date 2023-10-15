from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.backend.db import session, repository
from src.backend.db.redis import session as redis
from src.backend.schemas import schemas_auth
from src.backend.core import security


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
        redis_sess: redis.redis.Redis = Depends(redis.new_jwt_redis_session)
):
    res = await repository.users.create_new_user(source, db)

    access_token, refresh_token = await security.get_new_tokens(
        decoded_token=res.model_dump(),
        session=redis_sess,
    )

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content=res.model_dump(),
    )

    security.set_tokens_in_response(response, access_token, refresh_token)

    return res
