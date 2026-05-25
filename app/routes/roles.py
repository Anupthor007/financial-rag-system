from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleCreate, AssignRole

router = APIRouter(
    prefix="",
    tags=["Roles"]
)

ROLE_PERMISSIONS = {
    "Admin": [
        "full_access",
        "manage_users",
        "delete_documents"
    ],
    "Financial Analyst": [
        "upload_documents",
        "edit_documents"
    ],
    "Auditor": [
        "review_documents"
    ],
    "Client": [
        "view_company_documents"
    ]
}


@router.post("/roles/create")
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db)
):
    existing_role = db.query(Role).filter(
        Role.name == role.name
    ).first()

    if existing_role:
        raise HTTPException(
            status_code=400,
            detail="Role already exists"
        )

    new_role = Role(name=role.name)

    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return {
        "message": "Role created successfully"
    }


@router.post("/users/assign-role")
def assign_role(
    data: AssignRole,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    role = db.query(Role).filter(
        Role.name == data.role_name
    ).first()

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    user.role = role.name

    db.commit()

    return {
        "message": f"Role '{role.name}' assigned successfully"
    }


@router.get("/users/{user_id}/roles")
def get_user_role(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }


@router.get("/users/{user_id}/permissions")
def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    permissions = ROLE_PERMISSIONS.get(
        user.role,
        []
    )

    return {
        "role": user.role,
        "permissions": permissions
    }