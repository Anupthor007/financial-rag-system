from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str


class AssignRole(BaseModel):
    user_id: int
    role_name: str