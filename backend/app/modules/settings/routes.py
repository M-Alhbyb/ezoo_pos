"""
Settings API Routes - REST endpoints for system configuration and payment method management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.settings.service import SettingsService
from app.modules.settings.schemas import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse,
    PaymentMethodListResponse,
    SettingResponse,
    SettingUpdate,
    SettingListResponse,
    FeePresetsUpdate,
    FeePresetsResponse,
    FeePresetsListResponse,
)
from app.websocket.manager import manager

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Dedicated payment methods router for cleaner structure if needed,
# but we'll include it here with appropriate prefixes for the settings page.
# Note: The POS already uses /api/payment-methods, so we should keep compatible paths.


def get_settings_service(db: AsyncSession = Depends(get_db)) -> SettingsService:
    """Dependency injection for SettingsService."""
    return SettingsService(db)


@router.get(
    "/payment-methods",
    response_model=PaymentMethodListResponse,
    summary="List all payment methods",
)
async def list_payment_methods(
    active_only: bool = Query(False, description="Filter for active only"),
    service: SettingsService = Depends(get_settings_service),
):
    """
    List all payment methods (active or all).

    Args:
        active_only: Filter for active methods
        service: Injected SettingsService

    Returns:
        List of payment methods
    """
    methods = await service.list_payment_methods(active_only)
    return PaymentMethodListResponse(items=methods)


@router.post(
    "/payment-methods",
    response_model=PaymentMethodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a payment method",
)
async def create_payment_method(
    data: PaymentMethodCreate,
    service: SettingsService = Depends(get_settings_service),
):
    """
    Add a new payment method.

    Args:
        data: Payment method creation data
        service: Injected SettingsService

    Returns:
        Created payment method
    """
    try:
        return await service.create_payment_method(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/payment-methods/{pm_id}",
    response_model=PaymentMethodResponse,
    summary="Update a payment method",
)
async def update_payment_method(
    pm_id: UUID,
    data: PaymentMethodUpdate,
    service: SettingsService = Depends(get_settings_service),
):
    """
    Update an existing payment method.

    Args:
        pm_id: Payment method ID
        data: Update fields
        service: Injected SettingsService

    Returns:
        Updated payment method
    """
    pm = await service.update_payment_method(pm_id, data)
    if not pm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment method {pm_id} not found",
        )
    return pm


@router.delete(
    "/payment-methods/{pm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a payment method",
)
async def deactivate_payment_method(
    pm_id: UUID,
    service: SettingsService = Depends(get_settings_service),
):
    """
    Deactivate (soft delete) a payment method.

    Args:
        pm_id: Payment method ID
        service: Injected SettingsService
    """
    success = await service.soft_delete_payment_method(pm_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment method {pm_id} not found",
        )


# General System Settings


@router.get(
    "",
    response_model=SettingListResponse,
    summary="List all settings",
)
async def list_settings(
    service: SettingsService = Depends(get_settings_service),
):
    """List all system configuration settings."""
    settings = await service.list_settings()
    return SettingListResponse(items=settings)


@router.patch(
    "/{key}",
    response_model=SettingResponse,
    summary="Update a setting",
)
async def update_setting(
    key: str,
    data: SettingUpdate,
    service: SettingsService = Depends(get_settings_service),
):
    """
    Update a setting value by key.

    Args:
        key: Setting unique key
        data: Value update
        service: Injected SettingsService

    Returns:
        Updated setting
    """
    setting = await service.update_setting(key, data)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with key {key} not found",
        )
    return setting


# Fee Presets


@router.get(
    "/fee-presets",
    response_model=FeePresetsListResponse,
    summary="Get all fee presets for a location",
)
async def get_fee_presets(
    location_id: int = Query(..., description="Store location ID"),
    service: SettingsService = Depends(get_settings_service),
):
    """
    Get all fee presets for a location.

    Args:
        location_id: Store location ID
        service: Injected SettingsService

    Returns:
        Presets grouped by fee type
    """
    presets = await service.get_fee_presets(location_id)
    return FeePresetsListResponse(presets_by_fee_type=presets)


@router.post(
    "/fee-presets",
    response_model=FeePresetsResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update fee presets",
)
async def upsert_fee_presets(
    data: FeePresetsUpdate,
    service: SettingsService = Depends(get_settings_service),
):
    """
    Create or update fee presets for a location and fee type.

    Arguments:
        data: Preset update data (location_id, fee_type, presets)
        service: Injected SettingsService

    Returns:
        Updated presets for the fee type

    Note:
        Manager role check placeholder - currently single-user system.
        Future: Add role-based access control check here.
    """
    from decimal import Decimal

    try:
        # Convert Decimal list to Decimal list (already Decimal from Pydantic)
        result = await service.upsert_fee_presets(
            location_id=data.location_id,
            fee_type=data.fee_type,
            presets=list(data.presets),  # Already Decimal from Pydantic
        )

        # T047: Broadcast preset update via WebSocket
        presets_list = [float(p) for p in result[data.fee_type]]
        await manager.broadcast_preset_update(
            fee_type=data.fee_type, location_id=data.location_id, presets=presets_list
        )

        return FeePresetsResponse(fee_type=data.fee_type, presets=result[data.fee_type])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/fee-presets/{fee_type}",
    response_model=FeePresetsResponse,
    summary="Get presets for a specific fee type",
)
async def get_fee_presets_by_type(
    fee_type: str,
    location_id: int = Query(..., description="Store location ID"),
    service: SettingsService = Depends(get_settings_service),
):
    """
    Get presets for a specific fee type at a location.

    Args:
        fee_type: Type of fee (shipping, installation, custom)
        location_id: Store location ID
        service: Injected SettingsService

    Returns:
        Presets for the specified fee type
    """
    # Validate fee_type
    from app.schemas.sale import FeeType

    if fee_type not in [
        FeeType.SHIPPING.value,
        FeeType.INSTALLATION.value,
        FeeType.CUSTOM.value,
    ]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid fee_type: {fee_type}. Must be one of: shipping, installation, custom",
        )

    presets = await service.get_fee_presets(location_id)

    if fee_type not in presets or not presets[fee_type]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No presets found for fee_type={fee_type} at location_id={location_id}",
        )

    return FeePresetsResponse(fee_type=fee_type, presets=presets[fee_type])


@router.delete(
    "/fee-presets/{fee_type}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete fee presets for a fee type",
)
async def delete_fee_presets(
    fee_type: str,
    location_id: int = Query(..., description="Store location ID"),
    service: SettingsService = Depends(get_settings_service),
):
    """
    Delete all presets for a specific fee type at a location.

    Args:
        fee_type: Type of fee (shipping, installation, custom)
        location_id: Store location ID
        service: Injected SettingsService

    Note:
        Manager role check placeholder - currently single-user system.
        Future: Add role-based access control check here.
    """
    # Validate fee_type
    from app.schemas.sale import FeeType

    if fee_type not in [
        FeeType.SHIPPING.value,
        FeeType.INSTALLATION.value,
        FeeType.CUSTOM.value,
    ]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid fee_type: {fee_type}. Must be one of: shipping, installation, custom",
        )

    success = await service.delete_fee_presets(location_id, fee_type)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No presets found for fee_type={fee_type} at location_id={location_id}",
        )
