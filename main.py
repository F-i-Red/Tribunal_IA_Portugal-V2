# main.py - Tribunal IA Portugal (Versão RAG)
import os
from agentes.detetive import DetetiveJudicial
from agentes.advogados import Acusacao, Defesa
from agentes.juiz import ColetivoJuizes
from agentes.escrivao import EscrivaoDireito
from utils.loader import carregar_documentos # O carregador que criámos

class TribunalMaestro:
    def __init__(self):
        print("📂 [SISTEMA] A carregar base de dados jurídica...")
        self.documentos = self._inicializar_base_dados()
        
        self.detetive = DetetiveJudicial()
        self.acusacao = Acusacao()
        self.defesa = Defesa()
        self.juiz = ColetivoJuizes()
        self.escrivao = EscrivaoDireito()
        
        self.caso_completo = ""
        self.debate_encerrado = False

    def _inicializar_base_dados(self):
        # Verifica se a pasta existe, se não, cria
        if not os.path.exists("data/leis"):
            os.makedirs("data/leis")
        
        docs = carregar_documentos("data/leis/")
        print(f"✅ [RAG] {len(docs)} fragmentos de lei/jurisprudência carregados.")
        return docs

    def iniciar_sessao(self):
        print("\n🏛️  TRIBUNAL IA PORTUGAL - Versão 2.0 (RAG Ativado)")
        print("="* 50)
        
        if not self.documentos:
            print("⚠️  AVISO: Nenhuns documentos encontrados em data/leis/. O bot usará apenas conhecimento geral.")
        
        caso_inicial = input("⚖️  Descreva o caso (ex: herança, dano, conflito): ")
        self.caso_completo = caso_inicial
        self.correr_fluxo()

    def correr_fluxo(self):
        # Lógica de loop (idêntica à anterior, mas agora com suporte a docs)
        while not self.debate_encerrado:
            print("\n🔍 Detetive analisando factos e documentos...")
            lacunas = self.detetive.analisar_caso(self.caso_completo)
            
            if lacunas:
                print(f"🌡️  STATUS: {self.detetive.termometro_evidencia}")
                print("❓ Lacunas identificadas:")
                for i, p in enumerate(lacunas, 1): print(f"   {i}. {p}")
                
                resp = input("\n📝 Resposta (ou 'JULGAR'): ")
                if resp.upper() == "JULGAR": self.debate_encerrado = True
                else: self.caso_completo += f" [Adicional: {resp}]"
            else:
                self.debate_encerrado = True

        # Entrega ao Juiz e Escrivão para a Ata Final
        relatorio = self.detetive.relatorio_para_o_juiz()
        realidades = self.juiz.deliberar(relatorio, "", "") # Simplificado
        traducoes = self.escrivao.traduzir_para_cidadao(realidades)
        
        print(self.escrivao.redigir_ata_final(
            self.caso_completo, realidades, traducoes, self.escrivao.calcular_custas_estimadas()
        ))

if __name__ == "__main__":
    tribunal = TribunalMaestro()
    tribunal.iniciar_sessao()
