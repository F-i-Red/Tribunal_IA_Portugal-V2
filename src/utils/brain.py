"""
Interface central com a API Claude via OpenRouter.
Inclui retry com backoff exponencial, circuit breaker e monitorização de custos.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from .config import get_config
from .logger import get_logger


@dataclass
class LLMResponse:
    """Resposta estruturada do modelo."""
    content: str
    model: str
    tokens_input: int
    tokens_output: int
    duration_ms: float
    cost_usd: float


class CircuitBreakerOpen(Exception):
    """Circuit breaker aberto — API temporariamente indisponível."""
    pass


class TribunalBrain:
    """
    Cliente para API Claude via OpenRouter.
    Padrões: Circuit Breaker, Retry, Logging estruturado.
    """

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()
        self._failure_count = 0
        self._failure_threshold = 5
        self._circuit_open = False
        self._last_failure_time: Optional[float] = None
        self._circuit_timeout = 60  # segundos

    def _check_circuit(self):
        """Verifica se o circuit breaker está aberto."""
        if self._circuit_open:
            if self._last_failure_time and (time.time() - self._last_failure_time) > self._circuit_timeout:
                self._circuit_open = False
                self._failure_count = 0
                self.logger.info("Circuit breaker fechado — tentando novamente")
            else:
                raise CircuitBreakerOpen(
                    f"Circuit breaker aberto. Aguarde {self._circuit_timeout}s."
                )

    def _record_success(self):
        """Regista sucesso e reseta contador de falhas."""
        self._failure_count = 0

    def _record_failure(self):
        """Regista falha e verifica threshold do circuit breaker."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self._failure_threshold:
            self._circuit_open = True
            self.logger.error(
                f"Circuit breaker ABERTO após {self._failure_count} falhas consecutivas"
            )

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        reraise=True,
    )
    def call(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> LLMResponse:
        """
        Chama a API com retry automático e circuit breaker.

        Args:
            messages: Lista de {"role": "user"/"assistant", "content": "..."}
            system_prompt: Instruções de sistema
            temperature: Criatividade (0.0-1.0)
            max_tokens: Máximo de tokens na resposta

        Returns:
            LLMResponse com conteúdo e métricas
        """
        self._check_circuit()

        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/F-i-Red/Tribunal_IA_Portugal",
            "X-Title": "Tribunal IA Portugal",
        }

        payload = {
            "model": self.config.modelo,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            with httpx.Client(timeout=self.config.request_timeout) as client:
                response = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()

                duration_ms = (time.time() - start_time) * 1000

                # Extrair métricas
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                tokens_input = usage.get("prompt_tokens", 0)
                tokens_output = usage.get("completion_tokens", 0)

                # Calcular custo
                cost = self._estimate_cost(tokens_input, tokens_output)

                llm_response = LLMResponse(
                    content=content,
                    model=self.config.modelo,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    duration_ms=duration_ms,
                    cost_usd=cost,
                )

                # Log
                self.logger.log_api_call(
                    model=self.config.modelo,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    duration_ms=duration_ms,
                )

                self._record_success()
                return llm_response

        except httpx.HTTPStatusError as e:
            self._record_failure()
            self.logger.error(
                f"Erro HTTP {e.response.status_code}: {e.response.text[:200]}",
                status_code=e.response.status_code,
            )
            raise
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            self._record_failure()
            self.logger.error(f"Erro de conexão: {str(e)}")
            raise

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estima custo em USD."""
        pricing = {
            "claude-sonnet-4-6": (3.0, 15.0),
            "claude-opus-4-6": (15.0, 75.0),
            "claude-haiku-4-5-20251001": (0.25, 1.25),
        }
        input_price, output_price = pricing.get(self.config.modelo, (3.0, 15.0))
        return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


# Singleton
_brain: Optional[TribunalBrain] = None


def get_brain() -> TribunalBrain:
    """Retorna instância singleton do brain."""
    global _brain
    if _brain is None:
        _brain = TribunalBrain()
    return _brain
