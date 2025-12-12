from fastapi import HTTPException, status, APIRouter
from .. import models, schemas
from ..models import SessionDep, get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, session: SessionDep):

    hashed_password = get_password_hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, session: SessionDep):
    new_user = session.get(models.User, id)
    if not new_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} not found")

    return new_user
