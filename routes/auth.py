from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse, MessageResponse
from auth_utils import hash_password, verify_password, create_access_token, get_current_user
from database import get_db

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest):
    db = get_db()

    # Check duplicate email in same org
    existing = await db.users.find_one({
        "email": body.email,
        "organization_id": body.organization_id
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered in this organization"
        )

    # Check if org_id already has an admin when role is admin
    if body.role == "admin":
        admin_exists = await db.users.find_one({
            "organization_id": body.organization_id,
            "role": "admin"
        })
        if admin_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An admin already exists for this organization ID"
            )

    user_doc = {
        "organization_id":   body.organization_id,
        "organization_name": body.organization_name,
        "full_name":         body.full_name,
        "email":             body.email,
        "password_hash":     hash_password(body.password),
        "role":              body.role or "admin",
        "created_at":        datetime.utcnow(),
        "is_active":         True,
    }

    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    token = create_access_token({"sub": user_id, "org": body.organization_id})

    user_resp = UserResponse(
        id=user_id,
        organization_id=body.organization_id,
        organization_name=body.organization_name,
        full_name=body.full_name,
        email=body.email,
        role=user_doc["role"],
        created_at=user_doc["created_at"],
    )
    return TokenResponse(access_token=token, user=user_resp)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    db = get_db()

    user = await db.users.find_one({
        "email":           body.email,
        "organization_id": body.organization_id
    })

    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid organization ID, email, or password"
        )

    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is deactivated")

    user_id = str(user["_id"])
    token   = create_access_token({"sub": user_id, "org": user["organization_id"]})

    user_resp = UserResponse(
        id=user_id,
        organization_id=user["organization_id"],
        organization_name=user["organization_name"],
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"],
        created_at=user["created_at"],
    )
    return TokenResponse(access_token=token, user=user_resp)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["_id"],
        organization_id=current_user["organization_id"],
        organization_name=current_user["organization_name"],
        full_name=current_user["full_name"],
        email=current_user["email"],
        role=current_user["role"],
        created_at=current_user["created_at"],
    )
