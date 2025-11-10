from enum import Enum


class ItemType(str, Enum):
    PRODUCT = "product"
    SERVICE = "service"