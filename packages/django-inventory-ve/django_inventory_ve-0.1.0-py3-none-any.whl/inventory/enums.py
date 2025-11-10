from enum import Enum


class MoveType(str, Enum):
    IN = "in"
    OUT = "out"
    TRANSFER = "transfer"