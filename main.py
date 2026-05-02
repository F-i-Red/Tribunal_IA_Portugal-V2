#!/usr/bin/env python3
"""
Tribunal IA Portugal — Sistema de Simulação Jurídica
"""

import argparse
import sys
import time
from pathlib import Path

from src.utils import ConfigError, get_config, get_logger
from src.pipeline.case_processor import CaseProcessor
from src.pipeline.instancias import (
    INSTANCIAS, listar_instancias_menu, detectar_instancia_por_keywords
)

BANNER = """
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

DISCLAIMER = """
Este simulador não constitui parecer jurídico nem decisão judicial.
Para situações reais, consulte sempre um Advogado inscrito na
Ordem dos Advogados de Portugal (www.oa.pt).

Ao continuar, confirma que compreende esta limitação.
"""


def aceitar_disclaimer() -> bool:
    print(DISCLAIMER)
    r = input("Aceita as condições? (s/N): ").strip().lower()
    return r in ("s", "sim", "y", "yes")


def ler_caso() -> str:
    print("\n" + "─" * 70)
    print("📝  DESCRIÇÃO DO CASO")
    print("─" * 70)
    print("Descreve o caso jurídico com o máximo de detalhe possível.")
    print("Não precisas de saber termos jurídicos — usa linguagem comum.")
    print("(Termina com uma linha vazia)\n")
    lines = []
    while True:
        try:
            line = input("> ")
            if line.strip() == "" and lines:
                break
            if line.strip():
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Interrompido.")
            sys.exit(0)
    return "\n".join(lines)


def seleccionar_instancia(case_description: str) -> str:
    """
    Permite ao utilizador escolher a instância judicial, ou deixar a IA decidir.
    Retorna o código da instância (ex: 'TIC', 'TC_CIVEL', etc.)
    """
    print("\n" + "═" * 70)
    print("🏛️  SELECÇÃO DO TRIBUNAL")
    print("═" * 70)
    print("\nAntes de avançar, é necessário saber qual o tipo de tribunal.")
    print("Podes escolher tu, ou deixar que o sistema analise o teu caso.\n")
    print("  [1] Deixar o sistema decidir pelo caso que descreveste (recomendado)")
    print("  [2] Escolher manualmente")

    while True:
        opc = input("\nOpção (1 ou 2): ").strip()
        if opc in ("1", ""):
            # Auto-detecção
            codigo = detectar_instancia_por_keywords(case_description)
            inst = INSTANCIAS[codigo]
            print(f"\n  ✅ Tribunal identificado: {inst.nome}")
            print(f"     Matéria: {inst.materia}")
            print(f"     {inst.descricao}")
            confirmar = input("\n  Confirmas? (s/N, ou 'trocar' para escolher manualmente): ").strip().lower()
            if confirmar in ("s", "sim", "y", "yes", ""):
                return codigo
            elif confirmar == "trocar":
                opc = "2"  # cair no manual abaixo
            else:
                return codigo
        if opc == "2":
            print("\nTipos de tribunal disponíveis:")
            print(listar_instancias_menu())
            print("\n  [AUTO] Deixar o sistema decidir automaticamente")
            codigo_input = input("\nEscreve o código (ex: TIC, TC_CIVEL, TRAB) ou AUTO: ").strip().upper()
            # Se escrever "1" ou "2" por engano, redirecionar
            if codigo_input in ("1", ""):
                codigo = detectar_instancia_por_keywords(case_description)
                inst = INSTANCIAS[codigo]
                print(f"\n  ✅ Tribunal identificado automaticamente: {inst.nome}")
                return codigo
            if codigo_input in ("AUTO", "2"):
                codigo = detectar_instancia_por_keywords(case_description)
                inst = INSTANCIAS[codigo]
                print(f"\n  ✅ Tribunal identificado: {inst.nome}")
                return codigo
            if codigo_input in INSTANCIAS:
                inst = INSTANCIAS[codigo_input]
                print(f"\n  ✅ {inst.nome}")
                print(f"     Matéria: {inst.materia}")
                print(f"     {inst.descricao}")
                confirmar = input("\n  Confirmas este tribunal? (s/N): ").strip().lower()
                if confirmar in ("s", "sim", "y", "yes", ""):
                    return codigo_input
                continue  # voltar ao menu
            print(f"  ❌ Código '{codigo_input}' não reconhecido.")
            print(f"     Usa um dos códigos da lista acima (ex: TIC, TC_CIVEL, TRAB, AUTO)")


def fase_instrucao(processor: CaseProcessor, case_description: str,
                   instancia_codigo: str) -> dict:
    """Fase de instrução interativa com perguntas geradas pela IA."""
    inst = INSTANCIAS[instancia_codigo]
    print("\n" + "═" * 70)
    print(f"🔍  FASE DE INSTRUÇÃO — {inst.nome.upper()}")
    print("═" * 70)
    print(f"O {inst.termo_mp} e o Juiz de Instrução analisam o caso")
    print("e solicitam esclarecimentos antes do julgamento.\n")
    print("⏳ A analisar o caso e preparar questões...")

    result = processor.gerar_perguntas_instrucao(case_description, instancia_codigo)

    print("\n" + "─" * 70)
    print(result.get("introducao", "O Juiz de Instrução solicita esclarecimentos."))
    print("─" * 70)

    perguntas = result.get("perguntas", [])
    if not perguntas:
        print("\nℹ️  Os factos descritos são suficientes para avançar.")
        return {"respostas": {}, "materiais": []}

    print(f"\nExistem {len(perguntas)} questão(ões).")
    print("Responde, escreve 'n/a' para saltar, ou 'fim' para terminar.\n")

    respostas = {}
    materiais = []

    for i, p in enumerate(perguntas, 1):
        print(f"\n{'─' * 60}")
        print(f"❓  Questão {i}/{len(perguntas)}")
        emoji_imp = "⚠️ " if p.get("importancia") == "critica" else "ℹ️  "
        print(f"    {p['categoria']}: {p['texto']}")
        if p.get("importancia") in ("critica", "relevante"):
            print(f"    {emoji_imp}[{p.get('importancia', '').upper()}]")
        print()

        linhas = []
        print("Resposta (linha vazia para terminar, 'n/a' para saltar):")
        fim_antecipado = False
        while True:
            try:
                linha = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if linha.lower() == "fim":
                fim_antecipado = True
                break
            if linha.lower() in ("n/a", "na", "nao sei", "não sei", "skip", ""):
                if not linhas:
                    respostas[p["id"]] = {
                        "pergunta": p["texto"], "resposta": "Sem resposta",
                        "categoria": p["categoria"]
                    }
                break
            linhas.append(linha)

        if linhas:
            respostas[p["id"]] = {
                "pergunta": p["texto"],
                "resposta": " ".join(linhas),
                "categoria": p["categoria"]
            }
            print("  ✅ Resposta registada.")

            if p.get("aceita_documentos"):
                doc = input("\n  📎 Tem documento ou prova para descrever? (ou 'não'): ").strip()
                if doc and doc.lower() not in ("não", "nao", "n", ""):
                    materiais.append({"questao_id": p["id"], "descricao": doc})
                    print("  📎 Referência registada.")

        if fim_antecipado:
            print("\n⏹️  Instrução terminada antecipadamente.")
            break

    respondidas = sum(1 for r in respostas.values() if r["resposta"] != "Sem resposta")
    print(f"\n{'═' * 70}")
    print(f"✅ Instrução concluída: {respondidas}/{len(perguntas)} questões respondidas")
    print(f"{'═' * 70}\n")

    return {"respostas": respostas, "materiais": materiais}


def mostrar_progresso(passo: int, total: int, desc: str):
    barra = "█" * passo + "░" * (total - passo)
    print(f"\r   [{barra}] {passo}/{total} — {desc:<40}", end="", flush=True)


def processar_e_mostrar(case_description: str, instancia_codigo: str = None,
                        skip_instrucao: bool = False):
    processor = CaseProcessor()

    # Selecção de instância (se não fornecida)
    if not instancia_codigo:
        instancia_codigo = detectar_instancia_por_keywords(case_description)

    inst = INSTANCIAS[instancia_codigo]

    print(f"\n🔒 A verificar e anonimizar dados sensíveis...")

    # Fase de instrução
    dados_instrucao = {}
    if not skip_instrucao:
        dados_instrucao = fase_instrucao(processor, case_description, instancia_codigo)
    else:
        print("ℹ️  Instrução dispensada (modo batch).\n")

    # Processamento
    print("\n" + "═" * 70)
    print(f"⚖️  PROCESSAMENTO — {inst.nome.upper()}")
    print("═" * 70)

    passos = [
        "Anonimização RGPD",
        f"Instrução factual ({inst.nome_curto})",
        "Alegações — Acusação / Autor",
        "Alegações — Defesa / Réu",
        "Sentença — Perfil Rigoroso",
        "Sentença — Perfil Garantista",
        "Sentença — Perfil Equilibrado",
        "Montagem da ata",
    ]
    for i, p in enumerate(passos, 1):
        mostrar_progresso(i, len(passos), p)
        time.sleep(0.05)
    print()

    try:
        result = processor.process(
            case_description,
            instancia_codigo=instancia_codigo,
            dados_instrucao=dados_instrucao
        )

        print(f"\n✅ Caso processado!")
        print(f"   Processo:  {result.case_id}")
        print(f"   Tribunal:  {inst.nome}")
        print(f"   Entidades protegidas: {len(result.entities_found)}")
        tipos = {}
        for e in result.entities_found:
            tipos[e["type"]] = tipos.get(e["type"], 0) + 1
        for t, c in sorted(tipos.items()):
            print(f"     • {t}: {c}")

        print(f"\n📄 Ata guardada em: output_atas/{result.case_id}.txt")

        # Preview
        print("\n" + "═" * 70)
        print("PREVIEW DA ATA (primeiros 2000 caracteres)")
        print("═" * 70)
        preview = result.ata_final[:2000] if result.ata_final else ""
        print(preview)
        if result.ata_final and len(result.ata_final) > 2000:
            print(f"\n... [+{len(result.ata_final) - 2000} caracteres] ...")
        print("═" * 70)
        print(f"\n📂 Lê a ata completa: output_atas/{result.case_id}.txt")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)


def interactive_mode():
    print(BANNER)
    if not aceitar_disclaimer():
        print("❌ Aviso legal não aceite.")
        sys.exit(0)

    case_description = ler_caso()
    if not case_description.strip():
        print("❌ Nenhum caso fornecido.")
        sys.exit(1)

    instancia_codigo = seleccionar_instancia(case_description)
    processar_e_mostrar(case_description, instancia_codigo)



def _diagnostico_config(cfg):
    """Mostra configuração activa e avisa de problemas comuns."""
    modelo = cfg.modelo
    gratuito = modelo.endswith(":free") or modelo in ("openrouter/auto", "openrouter/free")

    print(f"\n📋 Configuração activa:")
    print(f"   Modelo: {modelo}")

    if gratuito:
        print(f"   🟢 Modelo GRATUITO")
        print(f"      Qualidade limitada mas funcional.")
        print(f"      Para melhores sentenças: edita .env → MODELO=anthropic/claude-haiku-4-5")
        print(f"      Para ver todas as opções: python verificar.py --modelos")
    else:
        print(f"   💛 Modelo pago — qualidade superior")
    print()

def main():
    parser = argparse.ArgumentParser(description="Tribunal IA Portugal")
    parser.add_argument("--file", "-f", help="Ficheiro com o caso")
    parser.add_argument("--text", "-t", help="Texto do caso")
    parser.add_argument("--tribunal", help="Código do tribunal (ex: TIC, TC_CIVEL, TRAB)")
    parser.add_argument("--sem-instrucao", action="store_true")
    parser.add_argument("--listar-tribunais", action="store_true",
                        help="Listar todos os tribunais disponíveis")
    parser.add_argument("--anonimizar", "-a", action="store_true")
    args = parser.parse_args()

    if args.listar_tribunais:
        print("\n🏛️  TRIBUNAIS DISPONÍVEIS\n")
        print(listar_instancias_menu())
        print()
        sys.exit(0)

    try:
        cfg = get_config()
        _diagnostico_config(cfg)
    except ConfigError as e:
        print(f"\n❌ {e}")
        sys.exit(1)

    if args.anonimizar:
        from src.utils import anonymize_text
        texto = Path(args.file).read_text(encoding="utf-8") if args.file else args.text or ""
        anon, ents = anonymize_text(texto)
        print("=== ANONIMIZADO ===\n", anon)
        print(f"\n📊 {len(ents)} entidade(s):")
        for e in ents:
            print(f"  • {e.label}: {e.text[:60]}")
        return

    if args.file:
        processar_e_mostrar(
            Path(args.file).read_text(encoding="utf-8"),
            instancia_codigo=args.tribunal,
            skip_instrucao=True
        )
    elif args.text:
        processar_e_mostrar(
            args.text,
            instancia_codigo=args.tribunal,
            skip_instrucao=args.sem_instrucao
        )
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
