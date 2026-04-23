# agentes/juiz.py
# O Coletivo de Juízes e o Motor de Realidades Paralelas

class ColetivoJuizes:
    def __init__(self):
        self.versao = "2.0 - Predição Jurisprudencial"

    def deliberar(self, analise_detetive, tese_acusacao, tese_defesa):
        """Gera as 3 Realidades Paralelas baseadas no equilíbrio de forças."""
        status_prova = analise_detetive['status']
        
        realidades = {
            "Rigorosa": self._sentenca_rigorosa(status_prova),
            "Garantista": self._sentenca_garantista(status_prova),
            "Equilibrada": self._sentenca_equilibrada(status_prova)
        }
        
        return realidades

    def _sentenca_rigorosa(self, status):
        return "Condenação Máxima: Foco na punição. Interpretação estrita da lei."

    def _sentenca_garantista(self, status):
        if "🔴" in status:
            return "Absolvição: Insuficiência de prova para condenação criminal."
        return "Pena Mínima: Foco na reabilitação e direitos do réu."

    def _sentenca_equilibrada(self, status):
        return "Solução de Compromisso: Condenação moderada com suspensão de execução."
