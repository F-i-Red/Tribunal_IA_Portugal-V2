# main.py
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

from utils.loader import carregar_documentos, resumir_para_contexto
from agentes.detetive import DetetiveJudicial
from agentes.advogados import Acusacao, Defesa
from agentes.juiz import ColetivoJuizes
from agentes.escrivao import EscrivaoDireito

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    console = Console()
    RICH = True
except ImportError:
    RICH = False

def imprimir(texto: str, estilo: str = "", titulo: str = ""):
    if RICH and titulo:
        console.print(Panel(texto, title=titulo, style=estilo or "white", expand=False))
    elif RICH:
        console.print(texto, style=estilo)
    else:
        if titulo:
            print(f"\n{'='*60}\n  {titulo}\n{'='*60}")
        print(texto)

def separador(titulo: str = ""):
    if RICH:
        console.rule(f"[bold]{titulo}[/bold]" if titulo else "", style="dim")
    else:
        print(f"\n{'─'*60}")
        if titulo: print(f"  {titulo}\n{'─'*60}")

def input_formatado(prompt: str) -> str:
    if RICH:
        console.print(f"\n[bold yellow]{prompt}[/bold yellow]")
        return input("  > ").strip()
    else:
        return input(f"\n{prompt}\n  > ").strip()

def banner():
    msg = """
   ╔══════════════════════════════════════════════════════════╗
   ║        🏛️  TRIBUNAL IA PORTUGAL  🇵🇹                      ║
   ║        Simulador Judicial de Alta Fidelidade              ║
   ║        Baseado no Direito Português Vigente               ║
   ╚══════════════════════════════════════════════════════════╝
    """
    if RICH: console.print(msg, style="bold blue")
    else: print(msg)


class TribunalMaestro:
    def __init__(self):
        banner()
        imprimir("A carregar documentos legislativos...", estilo="dim")
        pasta_leis = os.getenv("PASTA_LEIS", "data/leis/")
        corpus_raw = carregar_documentos(pasta_leis)
        self.corpus_legal = resumir_para_contexto(corpus_raw, max_chars=10000)

        self.detetive = DetetiveJudicial(corpus_legal=self.corpus_legal)
        self.acusacao = Acusacao(corpus_legal=self.corpus_legal)
        self.defesa = Defesa(corpus_legal=self.corpus_legal)
        self.juiz = ColetivoJuizes(corpus_legal=self.corpus_legal)
        self.escrivao = EscrivaoDireito()

        self.caso_completo = ""
        self.guardar_atas = os.getenv("GUARDAR_ATAS", "true").lower() == "true"

    def iniciar_sessao(self):
        separador("INÍCIO DA SESSÃO")
        imprimir(
            "Bem-vindo ao Tribunal IA Portugal.\n"
            "Este sistema simula um julgamento com múltiplos agentes de IA:\n"
            "  🔍 Detetive (Instrução)  |  🐍 Acusação  |  🛡️  Defesa  |  🔨 Coletivo de Juízes  |  📜 Escrivão\n\n"
            "Apresente o seu caso em linguagem corrente. O Detetive irá analisar e\n"
            "fazer perguntas até o processo estar maduro para julgamento."
        )
        caso_inicial = input_formatado("⚖️  Descreva o caso (factos, quem está envolvido, o que aconteceu):")
        if not caso_inicial:
            imprimir("❌ Nenhum caso descrito. A encerrar.", estilo="red")
            return
        self.caso_completo = caso_inicial
        self._loop_instrucao()

    def _loop_instrucao(self):
        """Loop de instrução: o Detetive interroga até o caso estar maduro."""
        MAX_ITERACOES = 5

        for i in range(MAX_ITERACOES):
            separador(f"🔍 INSTRUÇÃO — FASE {i+1}")
            imprimir("O Detetive está a analisar os factos e a avaliar as provas...", estilo="dim italic")

            resultado = self.detetive.analisar_caso(self.caso_completo)
            imprimir(
                resultado["resposta_completa"],
                titulo=f"Agente de Instrução | Termómetro: {resultado['termometro']}",
                estilo="cyan",
            )

            if resultado["pronto"]:
                imprimir("✅ O processo está maduro para audiência de julgamento.", estilo="bold green")
                break

            if resultado["lacunas"]:
                imprimir(
                    "O Detetive identificou lacunas. Responda para enriquecer o processo,\n"
                    "ou escreva [bold]JULGAR[/bold] para avançar directamente para julgamento." if RICH else
                    "O Detetive identificou lacunas. Responda ou escreva JULGAR para avançar.",
                    estilo="yellow",
                )
                resposta = input_formatado("📝 Resposta às lacunas (ou 'JULGAR' para avançar):")
                if resposta.upper() in ("JULGAR", "J", ""):
                    break
                self.caso_completo += f"\n[Informação adicional #{i+1}]: {resposta}"
            else:
                # Sem lacunas identificadas — avança
                break
        else:
            imprimir("⚠️  Número máximo de iterações atingido. A avançar para julgamento.", estilo="yellow")

        self._correr_julgamento()

    def _correr_julgamento(self):
        """Executa o debate completo e gera as sentenças."""

        # 1. Relatório de Instrução
        separador("📋 RELATÓRIO DE INSTRUÇÃO")
        imprimir("O Detetive está a redigir o relatório formal...", estilo="dim italic")
        relatorio = self.detetive.relatorio_para_tribunal(self.caso_completo)
        imprimir(relatorio, titulo="Relatório de Instrução", estilo="cyan")

        # Pausa para não exceder o rate limit dos modelos gratuitos
        time.sleep(5)

        # 2. Alegações da Acusação
        separador("🐍 ALEGAÇÕES DA ACUSAÇÃO")
        imprimir("O Advogado da Acusação está a construir a tese de culpa...", estilo="dim italic")
        tese_acusacao = self.acusacao.construir_alegacoes(relatorio)
        imprimir(tese_acusacao, titulo="Acusação — Ministério Público", estilo="red")

        time.sleep(5)

        # 3. Alegações da Defesa
        separador("🛡️  ALEGAÇÕES DA DEFESA")
        imprimir("O Patrono da Defesa está a preparar o contraditório...", estilo="dim italic")
        tese_defesa = self.defesa.construir_alegacoes(relatorio, tese_acusacao)
        imprimir(tese_defesa, titulo="Defesa — Patrono Garantista", estilo="green")

        time.sleep(5)

        # 4. NOVA FASE: Detetive intervém após o debate
        separador("🔍 NOTA DE INSTRUÇÃO PÓS-DEBATE (Agente de Instrução)")
        imprimir(
            "O Detetive analisa o debate entre acusação e defesa\n"
            "e identifica pontos por esclarecer para orientar o Coletivo de Juízes...",
            estilo="dim italic"
        )
        nota_pos_debate = self.detetive.questoes_pos_debate(tese_acusacao, tese_defesa, self.caso_completo)
        imprimir(nota_pos_debate, titulo="Nota de Instrução Pós-Debate", estilo="cyan")

        time.sleep(5)

        # 5. Deliberação do Coletivo (agora com a nota pós-debate)
        separador("🔨 DELIBERAÇÃO DO COLETIVO DE JUÍZES")
        imprimir(
            "O Coletivo de Juízes está a deliberar (3 perfis: Rigoroso, Garantista, Equilibrado)...\n"
            "Este processo pode demorar alguns momentos...",
            estilo="dim italic"
        )
        # Passa a nota pós-debate como contexto adicional para os juízes
        relatorio_completo = relatorio + f"\n\n---\nNOTA DE INSTRUÇÃO PÓS-DEBATE:\n{nota_pos_debate}"
        sentencas = self.juiz.deliberar(relatorio_completo, tese_acusacao, tese_defesa)

        # 6. Tradução para linguagem vulgar
        separador("📖 TRADUÇÃO PARA LINGUAGEM VULGAR")
        imprimir("O Escrivão está a traduzir as sentenças para linguagem acessível...", estilo="dim italic")
        traducoes = {}
        for perfil, sentenca in sentencas.items():
            traducoes[perfil] = self.escrivao.traduzir_sentenca(sentenca, perfil)

        # 7. Ata Final
        separador("📜 ATA FINAL DA AUDIÊNCIA")
        ata = self.escrivao.redigir_ata_final(
            caso_original=self.caso_completo,
            relatorio_instrucao=relatorio,
            nota_pos_debate=nota_pos_debate,
            tese_acusacao=tese_acusacao,
            tese_defesa=tese_defesa,
            sentencas=sentencas,
            traducoes=traducoes,
        )
        if RICH: console.print(ata, style="white")
        else: print(ata)

        if self.guardar_atas:
            pasta_atas = os.getenv("PASTA_ATAS", "output_atas/")
            caminho = self.escrivao.guardar_ata(ata, pasta=pasta_atas)
            imprimir(f"✅ Ata guardada em: {caminho}", estilo="bold green")

        separador("FIM DA SESSÃO")
        imprimir(
            "⚠️  AVISO LEGAL: Esta simulação tem fins exclusivamente educativos.\n"
            "Para questões jurídicas reais, consulte um Advogado inscrito na Ordem dos Advogados.",
            estilo="dim yellow",
        )


if __name__ == "__main__":
    try:
        tribunal = TribunalMaestro()
        tribunal.iniciar_sessao()
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🏛️  Sessão interrompida pelo utilizador. Até breve.")
        sys.exit(0)
