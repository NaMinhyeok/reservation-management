from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
