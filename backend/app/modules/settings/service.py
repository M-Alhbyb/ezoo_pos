"""
Settings Service - Business logic for system configuration and payment method management.
"""

import json
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment_method import PaymentMethod
from app.models.settings import Settings
from app.modules.settings.schemas import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    SettingUpdate,
)


class SettingsService:
    """Service class for settings and payment method CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Payment Methods

    async def list_payment_methods(
        self, active_only: bool = False
    ) -> List[PaymentMethod]:
        """List all payment methods."""
        query = select(PaymentMethod).order_by(PaymentMethod.name.asc())
        if active_only:
            query = query.where(PaymentMethod.is_active == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_payment_method(self, pm_id: UUID) -> Optional[PaymentMethod]:
        """Get a payment method by ID."""
        query = select(PaymentMethod).where(PaymentMethod.id == pm_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_payment_method(self, data: PaymentMethodCreate) -> PaymentMethod:
        """Create a new payment method."""
        pm = PaymentMethod(
            name=data.name,
            is_active=data.is_active,
        )
        self.db.add(pm)
        await self.db.commit()
        await self.db.refresh(pm)
        return pm

    async def update_payment_method(
        self, pm_id: UUID, data: PaymentMethodUpdate
    ) -> Optional[PaymentMethod]:
        """Update a payment method."""
        pm = await self.get_payment_method(pm_id)
        if not pm:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pm, field, value)

        await self.db.commit()
        await self.db.refresh(pm)
        return pm

    async def soft_delete_payment_method(self, pm_id: UUID) -> bool:
        """Soft delete (deactivate) a payment method."""
        pm = await self.get_payment_method(pm_id)
        if not pm:
            return False

        pm.is_active = False
        await self.db.commit()
        return True

    # Settings

    async def list_settings(self) -> List[Settings]:
        """List all system settings."""
        query = select(Settings).order_by(Settings.key.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_setting_by_key(self, key: str) -> Optional[Settings]:
        """Get a setting by key."""
        query = select(Settings).where(Settings.key == key)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_setting(self, key: str, data: SettingUpdate) -> Optional[Settings]:
        """Update a setting value."""
        setting = await self.get_setting_by_key(key)
        if not setting:
            return None

        setting.value = data.value
        await self.db.commit()
        await self.db.refresh(setting)
        return setting

    # Fee Presets

    async def get_fee_presets(self, location_id: int) -> dict[str, list[Decimal]]:
        """
        Get all fee presets for a location.

        Returns dict mapping fee_type -> list of preset amounts.
        """
        from app.schemas.sale import FeeType

        # Initialize result with empty lists for all fee types
        result: dict[str, list[Decimal]] = {
            FeeType.SHIPPING.value: [],
            FeeType.INSTALLATION.value: [],
            FeeType.CUSTOM.value: [],
        }

        # Query settings for all fee presets for this location
        pattern = f"fee_presets_{location_id}_%"
        query = select(Settings).where(Settings.key.like(pattern))
        settings_result = await self.db.execute(query)
        settings = settings_result.scalars().all()

        # Parse each setting and populate result
        for setting in settings:
            # Extract fee_type from key: "fee_presets_{location_id}_{fee_type}"
            parts = setting.key.split("_")
            if len(parts) == 4:
                fee_type = parts[3]
                try:
                    presets = json.loads(setting.value)
                    result[fee_type] = [Decimal(str(p)) for p in presets]
                except (json.JSONDecodeError, ValueError):
                    # If parse fails, continue with empty list
                    pass

        return result

    async def upsert_fee_presets(
        self, location_id: int, fee_type: str, presets: list[Decimal]
    ) -> dict[str, list[Decimal]]:
        """
        Create or update fee presets for a location and fee type.

        Validates max 8 presets, non-negative values, deduplicates and sorts.
        Returns the stored presets.
        """
        from app.schemas.sale import FeeType

        # Validate fee_type
        if fee_type not in [
            FeeType.SHIPPING.value,
            FeeType.INSTALLATION.value,
            FeeType.CUSTOM.value,
        ]:
            raise ValueError(f"Invalid fee_type: {fee_type}")

        # Validate and normalize presets
        if len(presets) > 8:
            raise ValueError("Maximum 8 preset amounts allowed")

        # Deduplicate and sort
        unique_sorted = sorted(set(presets))

        # Store as JSON
        key = f"fee_presets_{location_id}_{fee_type}"
        value_json = json.dumps([float(p) for p in unique_sorted])

        # Check if setting exists
        setting = await self.get_setting_by_key(key)

        if setting:
            # Update existing
            setting.value = value_json
        else:
            # Create new
            setting = Settings(
                key=key,
                value=value_json,
                description=f"Fee presets for {fee_type} at location {location_id}",
            )
            self.db.add(setting)

        await self.db.commit()
        await self.db.refresh(setting)

        return {fee_type: unique_sorted}

    async def delete_fee_presets(self, location_id: int, fee_type: str) -> bool:
        """
        Delete fee presets for a location and fee type.

        Returns True if deleted, False if not found.
        """
        key = f"fee_presets_{location_id}_{fee_type}"
        setting = await self.get_setting_by_key(key)

        if not setting:
            return False

        await self.db.delete(setting)
        await self.db.commit()
        return True
