from enum import Enum

class StatusVisitEnum(str, Enum):
    AGENDADO = "AGENDADO"
    REAGENDADO = "REAGENDADO"
    CANCELADO = "CANCELADO"
    ATENDIDO = "ATENDIDO"
    NO_ATENDIDO = "NO_ATENDIDO"
