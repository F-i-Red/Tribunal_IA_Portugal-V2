#!/usr/bin/env python3
"""
Verificação rápida da configuração e ligação à API.
Corre ANTES de processar um caso.

Uso:
    python verificar.py
    python verificar.py --modelos    # lista todos os modelos disponíveis
"""

import sys
import time
from pathlib import Path

# ─── Modelos disponíveis via OpenRouter ──────────────────────────────────────
MODELOS_INFO = {
    # Gratuitos
    "google/gemini-2.0-flash-exp:free":          ("🟢 GRATUITO", "Gemini 2.0 Flash — recomendado gratuito, bom"),
    "google/gemma-3-27b-it:free":                ("🟢 GRATUITO", "Gemma 3 27B — Google, bom para português"),
    "meta-llama/llama-4-maverick:free":          ("🟢 GRATUITO", "Llama 4 Maverick — Meta, muito bom"),
    "mistralai/mistral-small-3.1-24b-instruct:free": ("🟢 GRATUITO", "Mistral Small — europeu, bom"),
    "deepseek/deepseek-chat-v3-0324:free":       ("🟢 GRATUITO", "DeepSeek V3 — excelente, gratuito"),
    "openrouter/auto":                           ("🟢 GRATUITO", "OpenRouter escolhe automaticamente"),
    # Pagos baratos
    "anthropic/claude-haiku-4-5":                ("💛 PAGO",     "~0.01€/caso — Claude Haiku, muito bom"),
    "google/gemini-2.0-flash-001":               ("💛 PAGO",     "~0.01€/caso — Gemini Flash, muito bom"),
    "mistralai/mistral-small-24b":               ("💛 PAGO",     "~0.01€/caso — Mistral Small"),
    "deepseek/deepseek-chat-v3-0324":            ("💛 PAGO",     "~0.02€/caso — DeepSeek V3 pago"),
    # Pagos premium
    "anthropic/claude-sonnet-4.6":               ("🔴 PAGO",     "~0.05€/caso — Claude Sonnet, excelente"),
    "google/gemini-2.5-pro":                     ("🔴 PAGO",     "~0.05€/caso — Gemini 2.5 Pro, excelente"),
    "openai/gpt-4.1-mini":                       ("🔴 PAGO",     "~0.02€/caso — GPT-4.1 Mini"),
    "openai/gpt-4.1":                            ("🔴 PAGO",     "~0.10€/caso — GPT-4.1"),
}

def listar_modelos():
    print("\n📋 MODELOS DISPONÍVEIS VIA OPENROUTER")
    print("=" * 65)
    print("\nGRATUITOS — muda MODELO= no .env, sem custo:\n")
    for m, (cat, desc) in MODELOS_INFO.items():
        if "GRATUITO" in cat:
            print(f"  {m}")
            print(f"    → {desc}\n")
    print("\nPAGOS BARATOS — qualidade superior, custo mínimo:\n")
    for m, (cat, desc) in MODELOS_INFO.items():
        if cat == "💛 PAGO":
            print(f"  {m}")
            print(f"    → {desc}\n")
    print("\nPAGOS PREMIUM — melhor qualidade:\n")
    for m, (cat, desc) in MODELOS_INFO.items():
        if cat == "🔴 PAGO":
            print(f"  {m}")
            print(f"    → {desc}\n")
    print("Para mudar de modelo: edita .env e altera a linha MODELO=")
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--modelos", "-m", action="store_true",
                        help="Listar todos os modelos disponíveis")
    args = parser.parse_args()

    if args.modelos:
        listar_modelos()
        return

    print("\n🔍 VERIFICAÇÃO DO TRIBUNAL IA PORTUGAL")
    print("=" * 50)

    # 1. Dependências
    print("\n[1/4] Verificar dependências...")
    deps_ok = True
    for dep in ["httpx", "dotenv", "tenacity"]:
        try:
            __import__(dep.replace("-", "_"))
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} — corre: pip install {dep}")
            deps_ok = False
    if not deps_ok:
        print("\n❌ Instala: pip install -r requirements.txt")
        sys.exit(1)

    # 2. Ficheiro .env
    print("\n[2/4] Verificar ficheiro .env...")
    if not Path(".env").exists():
        print("  ❌ .env não encontrado!")
        print("     Windows: copy .env.example .env")
        print("     Mac/Linux: cp .env.example .env")
        print("     Depois edita .env e preenche OPENROUTER_API_KEY")
        sys.exit(1)
    print("  ✅ .env encontrado")

    # 3. Configuração
    print("\n[3/4] Verificar configuração...")
    try:
        import src.utils.config as cfg_mod
        cfg_mod._config = None
        from src.utils.config import get_config, ConfigError
        cfg = get_config()
        print(f"  ✅ API Key: ...{cfg.openrouter_api_key[-8:]}")
        print(f"  ✅ Modelo:  {cfg.modelo}")

        if cfg.modelo in MODELOS_INFO:
            cat, desc = MODELOS_INFO[cfg.modelo]
            print(f"  {cat}: {desc}")
        elif cfg.modelo.endswith(":free"):
            print(f"  🟢 GRATUITO: modelo gratuito personalizado")
        else:
            print(f"  ℹ️  Modelo personalizado")
            print(f"     Corre: python verificar.py --modelos  para ver opções")

    except ConfigError as e:
        print(f"  ❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        sys.exit(1)

    # 4. Ligação à API
    print("\n[4/4] Testar ligação à API OpenRouter...")
    try:
        import httpx

        headers = {
            "Authorization": f"Bearer {cfg.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/F-i-Red/Tribunal_IA_Portugal",
            "X-Title": "Tribunal IA Portugal",
        }
        payload = {
            "model": cfg.modelo,
            "messages": [
                {"role": "system", "content": "Responde apenas com a palavra OK."},
                {"role": "user", "content": "Teste de ligação."}
            ],
            "max_tokens": 10,
            "temperature": 0,
        }

        start = time.time()
        with httpx.Client(timeout=40) as client:
            resp = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )

        if resp.status_code == 200:
            data = resp.json()
            resposta = (data["choices"][0]["message"]["content"] or "").strip()
            ms = int((time.time() - start) * 1000)
            modelo_real = data.get("model", cfg.modelo)
            print(f"  ✅ API responde em {ms}ms")
            print(f"  ✅ Modelo confirmado: {modelo_real}")
            print(f"  ✅ Resposta de teste: \"{resposta[:50]}\"")
        elif resp.status_code == 401:
            print("  ❌ Chave API inválida (401)")
            print("     Verifica OPENROUTER_API_KEY no .env")
            sys.exit(1)
        elif resp.status_code == 402:
            print("  ❌ Sem créditos (402)")
            print("     Muda para modelo gratuito no .env:")
            print("     MODELO=google/gemini-2.0-flash-exp:free")
            sys.exit(1)
        elif resp.status_code == 400:
            print(f"  ❌ Modelo inválido (400): {resp.text[:200]}")
            print(f"     Modelo actual: {cfg.modelo}")
            print(f"     Corre: python verificar.py --modelos")
            sys.exit(1)
        elif resp.status_code == 429:
            print("  ⚠️  Rate limit (429) — aguarda 1 min e tenta novamente")
            sys.exit(1)
        else:
            print(f"  ❌ Erro HTTP {resp.status_code}: {resp.text[:200]}")
            sys.exit(1)

    except httpx.ConnectError:
        print("  ❌ Sem ligação à internet")
        sys.exit(1)
    except httpx.TimeoutException:
        print("  ❌ Timeout — API demorou mais de 40s")
        sys.exit(1)
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        sys.exit(1)

    # RAG
    print("\n[+] Verificar base de conhecimento (RAG)...")
    try:
        from src.rag import MotorRAG
        rag = MotorRAG(Path("."))
        n = rag.indexar()
        stats = rag.estatisticas()
        print(f"  ✅ {n} fragmentos indexados")
        print(f"     Leis: {stats['fragmentos_leis']} | "
              f"Jurisprudência: {stats['fragmentos_jurisprudencia']}")
    except Exception as e:
        print(f"  ⚠️  RAG: {e}")

    print("\n" + "=" * 50)
    print("✅ TUDO OK — Podes correr: python main.py")
    print("=" * 50)
    print(f"\nModelo activo: {cfg.modelo}")
    print("Para mudar: edita .env → linha MODELO=")
    print("Para ver opções: python verificar.py --modelos\n")


if __name__ == "__main__":
    main()
