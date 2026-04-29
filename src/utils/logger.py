"""
Sistema de logging estruturado com suporte a tracing de agentes.
Todos os eventos são JSON para integração com ferramentas de observabilidade.
"""

import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

from .config import get_config


class AgentTraceFilter(logging.Filter):
    """Adiciona contexto de tracing a todos os logs."""

    def __init__(self):
        super().__init__()
        self._trace_id: Optional[str] = None
        self._agent_name: Optional[str] = None
        self._case_id: Optional[str] = None

    def set_trace(self, trace_id: str, case_id: str, agent_name: str = "system"):
        self._trace_id = trace_id
        self._case_id = case_id
        self._agent_name = agent_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = self._trace_id or "no-trace"
        record.case_id = self._case_id or "no-case"
        record.agent_name = self._agent_name or "system"
        record.timestamp = datetime.now(timezone.utc).isoformat()
        return True


class TribunalLogger:
    """Logger singleton com tracing de processos jurídicos."""

    _instance: Optional["TribunalLogger"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        config = get_config()
        self.logger = logging.getLogger("tribunal_ia")
        self.logger.setLevel(getattr(logging, config.log_level))
        self.logger.handlers = []

        # Filtro de tracing
        self.trace_filter = AgentTraceFilter()
        self.logger.addFilter(self.trace_filter)

        # Handler para stdout
        handler = logging.StreamHandler(sys.stdout)

        if config.log_format == "json":
            formatter = jsonlogger.JsonFormatter(
                "%(timestamp)s %(levelname)s %(agent_name)s %(trace_id)s %(case_id)s %(message)s",
                rename_fields={"levelname": "level", "agent_name": "agent"}
            )
        else:
            formatter = logging.Formatter(
                "[%(timestamp)s] %(levelname)-8s | %(agent_name)-12s | %(trace_id)s | %(message)s"
            )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self._initialized = True

    def start_case(self, case_description: str) -> str:
        """Inicia um novo caso e retorna o trace_id."""
        trace_id = str(uuid.uuid4())[:8]
        case_id = f"case_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self.trace_filter.set_trace(trace_id, case_id, "orquestrador")

        self.logger.info(
            "Novo caso iniciado",
            extra={
                "event": "case_started",
                "case_description_hash": hash(case_description) & 0xFFFFFFFF,
            }
        )
        return trace_id

    def set_agent(self, agent_name: str):
        """Define o agente atual para tracing."""
        self.trace_filter._agent_name = agent_name

    def log_agent_action(self, agent: str, action: str, details: Dict[str, Any]):
        """Log estruturado de ação de agente."""
        self.set_agent(agent)
        self.logger.info(
            f"Agente {agent}: {action}",
            extra={
                "event": "agent_action",
                "action": action,
                "details": details,
            }
        )

    def log_api_call(self, model: str, tokens_input: int, tokens_output: int, duration_ms: float):
        """Log de chamada API para monitorização de custos."""
        self.logger.info(
            f"API call: {model}",
            extra={
                "event": "api_call",
                "model": model,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "duration_ms": duration_ms,
                "estimated_cost_usd": self._estimate_cost(model, tokens_input, tokens_output),
            }
        )

    def log_anonymization(self, entities_found: int, entity_types: list):
        """Log de anonimização para auditoria RGPD."""
        self.logger.info(
            "Anonimização aplicada",
            extra={
                "event": "anonymization",
                "entities_found": entities_found,
                "entity_types": entity_types,
            }
        )

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estima custo em USD (preços aproximados OpenRouter)."""
        pricing = {
            "claude-sonnet-4-6": (3.0, 15.0),   # $3/M input, $15/M output
            "claude-opus-4-6": (15.0, 75.0),
            "claude-haiku-4-5-20251001": (0.25, 1.25),
        }
        input_price, output_price = pricing.get(model, (3.0, 15.0))
        return (input_tokens * input_price + output_tokens * output_price) / 1_000_000

    def debug(self, msg: str, **kwargs):
        self.logger.debug(msg, extra=kwargs)

    def info(self, msg: str, **kwargs):
        self.logger.info(msg, extra=kwargs)

    def warning(self, msg: str, **kwargs):
        self.logger.warning(msg, extra=kwargs)

    def error(self, msg: str, **kwargs):
        self.logger.error(msg, extra=kwargs)


def get_logger() -> TribunalLogger:
    """Retorna instância singleton do logger."""
    return TribunalLogger()
