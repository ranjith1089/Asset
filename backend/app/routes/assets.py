from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from app.database import supabase
from app.models.asset import Asset, AssetCreate, AssetUpdate
from app.dependencies import get_user
from app.models.user import User

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=List[Asset])
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    category: str = None,
    current_user: User = Depends(get_user)
):
    """Get all assets with optional filtering"""
    query = supabase.table("assets").select("*")
    
    if status:
        query = query.eq("status", status)
    if category:
        query = query.eq("category", category)
    
    query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
    response = query.execute()
    
    return response.data


@router.get("/{asset_id}", response_model=Asset)
async def get_asset(asset_id: UUID, current_user: User = Depends(get_user)):
    """Get a specific asset by ID"""
    response = supabase.table("assets").select("*").eq("id", str(asset_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return response.data[0]


@router.post("", response_model=Asset, status_code=201)
async def create_asset(asset: AssetCreate, current_user: User = Depends(get_user)):
    """Create a new asset"""
    try:
        # Check if asset_tag already exists
        existing = supabase.table("assets").select("id").eq("asset_tag", asset.asset_tag).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Asset tag already exists")
        
        asset_dict = asset.model_dump()
        # Convert date objects to strings for Supabase
        if asset_dict.get("purchase_date") and hasattr(asset_dict["purchase_date"], "isoformat"):
            asset_dict["purchase_date"] = asset_dict["purchase_date"].isoformat()
        
        response = supabase.table("assets").insert(asset_dict).execute()
        
        if not response.data:
            error_msg = "Failed to create asset"
            if hasattr(response, 'error') and response.error:
                error_msg = f"Failed to create asset: {response.error}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create asset: {str(e)}")


@router.put("/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: UUID,
    asset_update: AssetUpdate,
    current_user: User = Depends(get_user)
):
    """Update an existing asset"""
    # Check if asset exists
    existing = supabase.table("assets").select("*").eq("id", str(asset_id)).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Check if asset_tag is being updated and if it already exists
    update_dict = asset_update.model_dump(exclude_unset=True)
    if "asset_tag" in update_dict:
        tag_check = supabase.table("assets").select("id").eq("asset_tag", update_dict["asset_tag"]).neq("id", str(asset_id)).execute()
        if tag_check.data:
            raise HTTPException(status_code=400, detail="Asset tag already exists")
    
    response = supabase.table("assets").update(update_dict).eq("id", str(asset_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to update asset")
    
    return response.data[0]


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: UUID, current_user: User = Depends(get_user)):
    """Delete an asset"""
    # Check if asset has active assignments
    active_assignments = supabase.table("assignments").select("id").eq("asset_id", str(asset_id)).eq("status", "active").execute()
    if active_assignments.data:
        raise HTTPException(status_code=400, detail="Cannot delete asset with active assignments")
    
    response = supabase.table("assets").delete().eq("id", str(asset_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return None

