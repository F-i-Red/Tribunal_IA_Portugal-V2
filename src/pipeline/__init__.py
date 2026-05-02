from .case_processor import CaseProcessor, CaseResult, process_case
from .instancias import INSTANCIAS, InstanciaJudicial, listar_instancias_menu, detectar_instancia_por_keywords

__all__ = [
    "CaseProcessor", "CaseResult", "process_case",
    "INSTANCIAS", "InstanciaJudicial", "listar_instancias_menu", "detectar_instancia_por_keywords",
]
