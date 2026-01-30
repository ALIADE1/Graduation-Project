from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.database import get_session
from src.db.models import User, Category
from src.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=["Categories"])

class CategoryCreate(BaseModel):
    name: str
    description: str = None

@router.get("", response_model=List[Category])
async def list_categories(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement = select(Category).where(Category.user_id == current_user.id)
    result = await session.exec(statement)
    return result.all()

@router.post("", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    new_cat = Category(
        name=data.name,
        description=data.description,
        user_id=current_user.id
    )
    session.add(new_cat)
    await session.commit()
    await session.refresh(new_cat)
    return new_cat
