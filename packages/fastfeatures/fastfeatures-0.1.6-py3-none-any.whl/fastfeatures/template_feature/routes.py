"""This module provides the routes for the FeatureName feature."""

from app.core import get_session
from app.features.feature_name.models.feature_name import FeatureName, FeatureNameCreate, FeatureNameLoad, \
    FeatureNameUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from .services.feature_name_services import FeatureNameService

router = APIRouter(
    prefix="/api/v1/feature_name",
    tags=["feature_name"]
)

feature_name_service = FeatureNameService(FeatureName, FeatureNameCreate, FeatureNameLoad, FeatureNameUpdate)


@router.get("/load/{feature_name_id}", response_model=FeatureNameLoad)
async def get_feature_name(feature_name_id: int, session: AsyncSession = Depends(get_session)):
    """Loads a FeatureName by its ID.

    Args:
        feature_name_id: The ID of the FeatureName to load.
        session: The database session.

    Returns:
        The loaded FeatureName.

    Raises:
        HTTPException: If the FeatureName is not found.
    """
    feature_name = await feature_name_service.load(session, feature_name_id)
    if not feature_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FeatureName not found")
    return feature_name


@router.post("/create", response_model=FeatureNameLoad)
async def create(feature_name: FeatureNameCreate, session: AsyncSession = Depends(get_session)):
    """Creates a new FeatureName.

    Args:
        feature_name: The data for the new FeatureName.
        session: The database session.

    Returns:
        The created FeatureName.
    """
    return await feature_name_service.create(session, feature_name)


@router.put('/update/{feature_name_id}', response_model=FeatureNameLoad)
async def update(feature_name_id: int, feature_name_update: FeatureNameUpdate, session: AsyncSession = Depends(get_session)):
    """Updates a FeatureName.

    Args:
        feature_name_id: The ID of the FeatureName to update.
        feature_name_update: The new data for the FeatureName.
        session: The database session.

    Returns:
        The updated FeatureName.

    Raises:
        HTTPException: If the FeatureName is not found.
    """
    db_obj = await feature_name_service.load(session, feature_name_id)
    if not db_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FeatureName not found")
    return await feature_name_service.update(session, db_obj, feature_name_update)


@router.delete("/delete/{feature_name_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(feature_name_id: int, session: AsyncSession = Depends(get_session)):
    """Deletes a FeatureName.

    Args:
        feature_name_id: The ID of the FeatureName to delete.
        session: The database session.

    Raises:
        HTTPException: If the FeatureName is not found.
    """
    db_obj = await feature_name_service.load(session, feature_name_id)
    if not db_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FeatureName not found")
    await feature_name_service.delete(session, db_obj)
    return {"message": "FeatureName deleted successfully"}
