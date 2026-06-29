import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    member = "member"