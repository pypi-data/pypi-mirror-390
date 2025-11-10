from enum import Enum


class CompType(str, Enum):
    EARNING = "earning"
    DEDUCTION = "deduction"