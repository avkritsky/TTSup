from fastapi import APIRouter


router = APIRouter(
    prefix='/auth',
    tags=[
        'auth',
    ],
)


@router.post('')
async def create_user():
    pass
