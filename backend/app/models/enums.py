from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    agent = "agent"
    customer = "customer"

class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"