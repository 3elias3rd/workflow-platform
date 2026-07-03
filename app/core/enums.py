import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    member = "member"

class TriggerTypeEnum(str, enum.Enum):
    webhook = "webhook"
    manual = "manual"


class ActionTypeEnum(str, enum.Enum):
    log = "log"
    http_request = "http_request"


class ExecutionStatusEnum(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
