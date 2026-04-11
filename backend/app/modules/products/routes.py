"""
Product API Routes - REST endpoints for product catalog management.

Implements all endpoints from contracts/products-api.md
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.modules.products.service import ProductService
from app.models.product_assignment import ProductAssignment
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

router = APIRouter(prefix="/api/products", tags=["products"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    """Dependency injection for ProductService."""
    return ProductService(db)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Creates a new product in the catalog with validation",
)
async def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    """
    Create a new product.

    Constitution VII: Backend validates all business rules.
    Constitution VI: All monetary values use Decimal type.

    Args:
        product_data: Product data with validation
        service: Injected ProductService

    Returns:
        Created product

    Raises:
        HTTPException 400: Validation error
        HTTPException 409: Duplicate SKU
        HTTPException 404: Category not found
    """
    try:
        product = await service.create_product(product_data)
        return _prepare_product_response(product)
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "CONFLICT",
                        "message": error_msg,
                        "details": {"field": "sku"},
                    }
                },
            )
        elif "Category" in error_msg and "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
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


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products with filters",
    description="Retrieves a paginated list of products with optional filters",
)
async def list_products(
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(
        None, max_length=200, description="Search by name or SKU"
    ),
    active_only: bool = Query(True, description="Only return active products"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    service: ProductService = Depends(get_product_service),
    db: AsyncSession = Depends(get_db),
):
    """
    List products with optional filters and pagination.

    Includes active product assignment information for each product.

    Args:
        category_id: Filter by category UUID
        search: Search by name (partial) or SKU (exact)
        active_only: Only return active products
        page: Page number (1-indexed)
        page_size: Items per page (max 100)
        service: Injected ProductService
        db: Database session

    Returns:
        Paginated list of products with assignment information
    """
    products, total = await service.list_products(
        category_id=category_id,
        search=search,
        active_only=active_only,
        page=page,
        page_size=page_size,
    )

    # Fetch assignments for each product
    product_responses = []
    for product in products:
        assignment = await _get_product_assignment(db, product.id)
        product_responses.append(_prepare_product_response(product, assignment))

    return ProductListResponse(
        items=product_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/search/by-sku",
    response_model=ProductResponse,
    summary="Search product by SKU",
    description="Exact SKU lookup for barcode scanning",
)
async def search_by_sku(
    sku: str = Query(..., min_length=1, max_length=50, description="SKU to search"),
    service: ProductService = Depends(get_product_service),
):
    """
    Search for a product by exact SKU match.

    Used primarily for barcode scanner integration.

    Args:
        sku: SKU string
        service: Injected ProductService

    Returns:
        Product matching the SKU

    Raises:
        HTTPException 404: SKU not found
    """
    product = await service.get_by_sku(sku)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Product with SKU '{sku}' not found",
                }
            },
        )

    return _prepare_product_response(product)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Retrieves a single product by ID with assignment information",
)
async def get_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single product by ID.

    Includes active product assignment information if the product is assigned to a partner.

    Args:
        product_id: Product UUID
        service: Injected ProductService
        db: Database session

    Returns:
        Product details with assignment information

    Raises:
        HTTPException 404: Product not found
    """
    product = await service.get_product(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Product {product_id} not found",
                }
            },
        )

    # Fetch active assignment for this product
    assignment = await _get_product_assignment(db, product_id)

    return _prepare_product_response(product, assignment)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Partial update product",
    description="Updates product details (cannot update stock_quantity)",
)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    """
    Update product details.

    Note: stock_quantity cannot be updated directly (use inventory endpoints).

    Args:
        product_id: Product UUID
        product_data: Fields to update
        service: Injected ProductService

    Returns:
        Updated product

    Raises:
        HTTPException 400: Validation error
        HTTPException 404: Product not found
        HTTPException 409: Duplicate SKU
    """
    try:
        product = await service.update_product(product_id, product_data)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Product {product_id} not found",
                    }
                },
            )

        return _prepare_product_response(product)
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "CONFLICT",
                        "message": error_msg,
                        "details": {"field": "sku"},
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


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft delete product",
    description="Soft deletes a product (sets is_active = False)",
)
async def delete_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    """
    Soft delete a product.

    Products referenced in sales cannot be hard deleted,
    so this always performs a soft delete for consistency.

    Args:
        product_id: Product UUID
        service: Injected ProductService

    Returns:
        Success message

    Raises:
        HTTPException 404: Product not found
    """
    deleted = await service.soft_delete_product(product_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Product {product_id} not found",
                }
            },
        )

    return {"message": "Product deactivated successfully"}


def _prepare_product_response(product, assignment=None) -> dict:
    """
    Convert Product instance to response dictionary.

    Ensures category_name is included and all values are properly formatted.
    Optionally includes assignment information if the product has an active assignment.

    Args:
        product: Product model instance
        assignment: Optional ProductAssignment instance

    Returns:
        Dictionary with product data and optional assignment
    """
    response = {
        "id": str(product.id),
        "name": product.name,
        "sku": product.sku,
        "category_id": str(product.category_id),
        "category_name": product.category.name if product.category else None,
        "base_price": str(product.base_price),
        "selling_price": str(product.selling_price),
        "stock_quantity": product.stock_quantity,
        "is_active": product.is_active,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }

    # Include assignment information if provided
    if assignment:
        from app.schemas.product_assignment import ProductAssignmentResponse

        response["assignment"] = {
            "id": str(assignment.id),
            "partner_id": str(assignment.partner_id),
            "partner_name": "Partner",  # TODO: Fetch from relationship
            "product_id": str(assignment.product_id),
            "product_name": product.name,
            "assigned_quantity": assignment.assigned_quantity,
            "remaining_quantity": assignment.remaining_quantity,
            "share_percentage": float(assignment.share_percentage),
            "status": assignment.status,
            "created_at": assignment.created_at,
            "updated_at": assignment.updated_at,
            "fulfilled_at": assignment.fulfilled_at,
        }
    else:
        response["assignment"] = None

    return response


async def _get_product_assignment(
    db: AsyncSession, product_id: UUID
) -> Optional[ProductAssignment]:
    """
    Fetch the active assignment for a product if it exists.

    Args:
        db: Database session
        product_id: Product UUID

    Returns:
        ProductAssignment or None
    """
    query = select(ProductAssignment).where(
        ProductAssignment.product_id == product_id,
        ProductAssignment.status == "active",
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()
