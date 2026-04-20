"""
Category API Routes - REST endpoints for category management.

Implements all endpoints from contracts/categories-api.md
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.category import Category
from app.modules.categories.service import CategoryService
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)

router = APIRouter(prefix="/api/categories", tags=["categories"])


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    """Dependency injection for CategoryService."""
    return CategoryService(db)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    description="Creates a new product category",
)
async def create_category(
    category_data: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    """
    Create a new category.

    Args:
        category_data: Category data with validation
        service: Injected CategoryService

    Returns:
        Created category

    Raises:
        HTTPException 409: Duplicate category name
    """
    try:
        category = await service.create_category(category_data)
        return _prepare_category_response(category, product_count=0)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "CONFLICT",
                    "message": str(e),
                }
            },
        )


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="List all categories",
    description="Retrieves all categories with product counts",
)
async def list_categories(
    service: CategoryService = Depends(get_category_service),
):
    """
    List all categories with product counts.

    Args:
        service: Injected CategoryService

    Returns:
        List of categories
    """
    categories_with_counts = await service.list_categories()

    items = [
        _prepare_category_response(category, product_count=count)
        for category, count in categories_with_counts
    ]

    return CategoryListResponse(items=items)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category by ID",
    description="Retrieves a single category by ID",
)
async def get_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    """
    Get a single category by ID.

    Args:
        category_id: Category UUID
        service: Injected CategoryService

    Returns:
        Category details

    Raises:
        HTTPException 404: Category not found
    """
    category = await service.get_category(category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Category {category_id} not found",
                }
            },
        )

    product_count = await service._count_active_products(category_id)
    return _prepare_category_response(category, product_count=product_count)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update category",
    description="Updates category name",
)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    """
    Update category name.

    Args:
        category_id: Category UUID
        category_data: Name to update
        service: Injected CategoryService

    Returns:
        Updated category

    Raises:
        HTTPException 404: Category not found
        HTTPException 409: Duplicate category name
    """
    try:
        category = await service.update_category(category_id, category_data)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Category {category_id} not found",
                    }
                },
            )

        product_count = await service._count_active_products(category_id)
        return _prepare_category_response(category, product_count=product_count)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "CONFLICT",
                    "message": str(e),
                }
            },
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete category",
    description="Deletes a category (only if no products reference it)",
)
async def delete_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    """
    Delete a category.

    Only allowed if no active products reference it.

    Args:
        category_id: Category UUID
        service: Injected CategoryService

    Returns:
        Success message

    Raises:
        HTTPException 404: Category not found
        HTTPException 409: Category has active products
    """
    try:
        deleted = await service.delete_category(category_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Category {category_id} not found",
                    }
                },
            )

        return {"message": "Category deleted successfully"}
    except ValueError as e:
        error_msg = str(e)
        if "active products" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "CATEGORY_HAS_PRODUCTS",
                        "message": error_msg,
                    }
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": error_msg,
                    }
                },
            )


def _prepare_category_response(category: Category, product_count: int = 0) -> dict:
    """
    Convert Category instance to response dictionary.

    Args:
        category: Category instance
        product_count: Number of active products

    Returns:
        Dictionary ready for response
    """
    return {
        "id": str(category.id),
        "name": category.name,
        "product_count": product_count,
        "created_at": category.created_at,
        "updated_at": category.updated_at,
    }
