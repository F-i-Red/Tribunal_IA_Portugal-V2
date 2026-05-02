#!/usr/bin/env python3
"""
Gestão da base de conhecimento jurídico (RAG) — Fase 2.

Permite:
  - Ver o estado da base de conhecimento
  - Testar pesquisas
  - Adicionar novos ficheiros de leis/jurisprudência

Uso:
    python gerir_base.py              # Estado e estatísticas
    python gerir_base.py --pesquisar "tortura sons vizinho"
    python gerir_base.py --listar
"""

import sys
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag import MotorRAG, ValidadorCitacoes


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gestão da base RAG — Tribunal IA Portugal")
    parser.add_argument("--pesquisar", "-p", type=str, help="Pesquisar na base de conhecimento")
    parser.add_argument("--listar", "-l", action="store_true", help="Listar todos os ficheiros indexados")
    parser.add_argument("--validar", "-v", type=str, help="Validar citações num texto")
    parser.add_argument("--n", type=int, default=5, help="Número de resultados (default: 5)")
    args = parser.parse_args()

    rag = MotorRAG(Path("."))
    n = rag.indexar()
    stats = rag.estatisticas()

    print("\n📚 BASE DE CONHECIMENTO JURÍDICO — TRIBUNAL IA PORTUGAL")
    print("=" * 60)
    print(f"  Fragmentos indexados: {stats['total_fragmentos']}")
    print(f"  De leis:              {stats['fragmentos_leis']}")
    print(f"  De jurisprudência:    {stats['fragmentos_jurisprudencia']}")
    print(f"\n  Fontes disponíveis:")
    for fonte in sorted(stats['fontes']):
        print(f"    • {fonte}")

    if not stats['total_fragmentos']:
        print("\n⚠️  Nenhum ficheiro indexado.")
        print("   Adiciona ficheiros .txt em:")
        print("   data/leis/          — diplomas legais")
        print("   data/jurisprudencia/ — acórdãos e jurisprudência")
        return

    if args.listar:
        validador = ValidadorCitacoes(Path("data/leis"))
        print(f"\n📂 FICHEIROS NAS PASTAS:")
        for pasta in [Path("data/leis"), Path("data/jurisprudencia")]:
            if pasta.exists():
                print(f"\n  {pasta}/")
                for f in sorted(pasta.glob("*.txt")):
                    tamanho = f.stat().st_size // 1024
                    print(f"    📄 {f.name} ({tamanho} KB)")

    if args.pesquisar:
        print(f"\n🔍 PESQUISA: \"{args.pesquisar}\"")
        print("-" * 60)
        resultados = rag.pesquisar(args.pesquisar, n_resultados=args.n)
        if not resultados:
            print("  Nenhum resultado encontrado.")
        else:
            for i, r in enumerate(resultados, 1):
                print(f"\n  [{i}] {r.fonte} — {r.tipo.upper()} (relevância: {r.relevancia})")
                if r.artigo:
                    print(f"       Artigo: {r.artigo}")
                print(f"       {r.conteudo[:200].strip()}...")

    if args.validar:
        print(f"\n✅ VALIDAÇÃO DE CITAÇÕES")
        print("-" * 60)
        validador = ValidadorCitacoes(Path("data/leis"))
        _, problemas = validador.validar_texto(args.validar)
        print(validador.relatorio_citacoes(problemas))

    if not any([args.pesquisar, args.listar, args.validar]):
        print("\n💡 COMANDOS DISPONÍVEIS:")
        print("  python gerir_base.py --pesquisar \"tortura sons vizinho\"")
        print("  python gerir_base.py --pesquisar \"despedimento justa causa\" --n 3")
        print("  python gerir_base.py --listar")
        print("  python gerir_base.py --validar \"art. 143.º CP e art. 256 CPP\"")
        print("\n📁 PARA ADICIONAR LEIS:")
        print("  Copia ficheiros .txt para data/leis/ ou data/jurisprudencia/")
        print("  Podes descarregar leis em: https://dre.pt")

    print()


if __name__ == "__main__":
    main()
