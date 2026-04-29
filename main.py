#!/usr/bin/env python3
"""
Tribunal IA Portugal — Sistema de Simulação Jurídica
Ponto de entrada principal.

Uso:
    python main.py                    # Modo interativo
    python main.py --file caso.txt    # Processar ficheiro
    python main.py --text "descrição" # Processar texto inline
"""

import argparse
import sys
from pathlib import Path

from src.utils import ConfigError, get_config, get_logger
from src.pipeline.case_processor import CaseProcessor


def print_banner():
    """Mostra banner de arranque."""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           🏛️  TRIBUNAL IA PORTUGAL  🇵🇹                              ║
║                                                                      ║
║   Simulador judicial de alta fidelidade — Direito Português          ║
║                                                                      ║
║   ⚠️  Fins exclusivamente educativos e de simulação                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def interactive_mode():
    """Modo interativo — o utilizador descreve o caso."""
    print_banner()
    print("Descreve o caso jurídico (termina com linha vazia):\n")

    lines = []
    while True:
        try:
            line = input("> ")
            if line.strip() == "":
                break
            lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Interrompido pelo utilizador.")
            sys.exit(0)

    case_description = "\n".join(lines)

    if not case_description.strip():
        print("❌ Nenhum caso fornecido.")
        sys.exit(1)

    process_and_display(case_description)


def process_and_display(case_description: str):
    """Processa caso e mostra resultados."""
    processor = CaseProcessor()

    print("\n🔍 A processar caso...")
    print("   1. Anonimização de dados sensíveis")
    print("   2. Instrução factual (Detetive)")
    print("   3. Alegações (Acusação + Defesa)")
    print("   4. Sentenças (3 perfis)")
    print("   5. Ata final + Watermarking\n")

    try:
        result = processor.process(case_description)

        print(f"\n✅ Caso processado com sucesso!")
        print(f"   ID: {result.case_id}")
        print(f"   Trace: {result.trace_id}")
        print(f"   Entidades anonimizadas: {len(result.entities_found)}")

        if result.entities_found:
            print("\n   Entidades encontradas:")
            for ent in result.entities_found:
                print(f"     • {ent['type']}: \"{ent['text'][:50]}...\" (score: {ent['score']:.2f})")

        print(f"\n📄 Ata guardada em: output_atas/{result.case_id}.txt")

        # Mostrar preview da ata
        print("\n" + "=" * 70)
        print("PREVIEW DA ATA:")
        print("=" * 70)
        preview = result.ata_final[:1500] if result.ata_final else ""
        print(preview)
        if result.ata_final and len(result.ata_final) > 1500:
            print(f"\n... [{len(result.ata_final) - 1500} caracteres restantes] ...")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Erro ao processar caso: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Tribunal IA Portugal — Simulação Jurídica",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Ficheiro com a descrição do caso",
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Texto do caso (inline)",
    )
    parser.add_argument(
        "--anonimizar-only", "-a",
        action="store_true",
        help="Apenas mostrar resultado da anonimização (sem processar)",
    )

    args = parser.parse_args()

    # Validar configuração
    try:
        config = get_config()
    except ConfigError as e:
        print(f"\n❌ {e}")
        sys.exit(1)

    logger = get_logger()
    logger.info("Tribunal IA Portugal iniciado")

    # Determinar modo
    if args.anonimizar_only:
        from src.utils import anonymize_text

        if args.file:
            text = Path(args.file).read_text(encoding="utf-8")
        elif args.text:
            text = args.text
        else:
            print("❌ Fornece --file ou --text para anonimização.")
            sys.exit(1)

        anonymized, entities = anonymize_text(text)
        print("\n=== TEXTO ORIGINAL ===")
        print(text[:500] + "..." if len(text) > 500 else text)
        print("\n=== TEXTO ANONIMIZADO ===")
        print(anonymized[:500] + "..." if len(anonymized) > 500 else anonymized)
        print(f"\nEntidades encontradas: {len(entities)}")
        for ent in entities:
            print(f"  • {ent.label}: \"{ent.text[:40]}...\"")

    elif args.file:
        case_text = Path(args.file).read_text(encoding="utf-8")
        process_and_display(case_text)

    elif args.text:
        process_and_display(args.text)

    else:
        interactive_mode()


if __name__ == "__main__":
    main()
