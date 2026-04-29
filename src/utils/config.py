"""
Configuração centralizada com validação de segurança.
Todas as variáveis são validadas no arranque da aplicação.
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv


class ConfigError(Exception):
    """Erro de configuração crítico que impede o arranque."""
    pass


@dataclass(frozen=True)
class Config:
    """Configuração imutável do sistema."""

    # API
    openrouter_api_key: str
    modelo: str = "claude-sonnet-4-6"

    # Retry
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    request_timeout: int = 60

    # Dados
    pasta_leis: Path = field(default_factory=lambda: Path("data/leis"))
    pasta_precedentes: Path = field(default_factory=lambda: Path("data/precedentes"))

    # Output
    guardar_atas: bool = True
    pasta_atas: Path = field(default_factory=lambda: Path("output_atas"))

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Anonimização
    anonimizar_entidades: bool = True
    tipos_entidades: List[str] = field(default_factory=lambda: [
        "PESSOA", "LOCAL", "ORGANIZACAO", "DATA", "CONTACTO", "NIF"
    ])

    # Vector Store
    chroma_db_path: Path = field(default_factory=lambda: Path("data/chroma_db"))
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # Segurança
    watermark_atas: bool = True
    disclaimer_obrigatorio: bool = True

    @classmethod
    def from_env(cls) -> "Config":
        """Carrega e valida configuração do ambiente."""
        load_dotenv()

        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

        # Validações críticas de segurança
        if not api_key:
            raise ConfigError(
                "❌ OPENROUTER_API_KEY não definida.\n"
                "   Copie .env.example para .env e preencha a chave."
            )

        if api_key.startswith("sk-or-v1-") and len(api_key) < 30:
            raise ConfigError(
                "❌ OPENROUTER_API_KEY parece incompleta ou inválida."
            )

        if "sua_chave_aqui" in api_key.lower() or "xxxx" in api_key.lower():
            raise ConfigError(
                "❌ OPENROUTER_API_KEY contém placeholder. Substitua pela chave real."
            )

        # Validação de diretórios
        pasta_atas = Path(os.getenv("PASTA_ATAS", "output_atas"))
        pasta_atas.mkdir(parents=True, exist_ok=True)

        return cls(
            openrouter_api_key=api_key,
            modelo=os.getenv("MODELO", "claude-sonnet-4-6"),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_backoff_factor=float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "60")),
            pasta_leis=Path(os.getenv("PASTA_LEIS", "data/leis")),
            pasta_precedentes=Path(os.getenv("PASTA_PRECEDENTES", "data/precedentes")),
            guardar_atas=os.getenv("GUARDAR_ATAS", "true").lower() == "true",
            pasta_atas=pasta_atas,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            log_format=os.getenv("LOG_FORMAT", "json"),
            anonimizar_entidades=os.getenv("ANONIMIZAR_ENTIDADES", "true").lower() == "true",
            tipos_entidades=os.getenv("TIPOS_ENTIDADES", "PESSOA,LOCAL,ORGANIZACAO,DATA,CONTACTO,NIF").split(","),
            chroma_db_path=Path(os.getenv("CHROMA_DB_PATH", "data/chroma_db")),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
            watermark_atas=os.getenv("WATERMARK_ATAS", "true").lower() == "true",
            disclaimer_obrigatorio=os.getenv("DISCLAIMER_OBRIGATORIO", "true").lower() == "true",
        )

    def validate_directories(self) -> None:
        """Garante que todos os diretórios necessários existem."""
        for path in [self.pasta_leis, self.pasta_precedentes, self.chroma_db_path]:
            path.mkdir(parents=True, exist_ok=True)


# Singleton global
_config: Optional[Config] = None


def get_config() -> Config:
    """Retorna configuração singleton (lazy loading)."""
    global _config
    if _config is None:
        _config = Config.from_env()
        _config.validate_directories()
    return _config
