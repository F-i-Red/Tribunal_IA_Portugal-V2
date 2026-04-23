# agentes/detetive.py
# O Agente de Instrução e Análise Factual do Tribunal IA Portugal

class DetetiveJudicial:
    def __init__(self):
        self.nome = "Agente de Instrução"
        self.termometro_evidencia = "🔴 FRÁGIL"  # Inicial
        self.evidencias_encontradas = []
        self.lacunas = []

    def analisar_caso(self, relato_utilizador):
        """
        Analisa o texto do utilizador à procura de palavras-chave 
        que indiquem provas (ex: 'mensagem', 'foto', 'testemunha').
        """
        # Lógica de triagem (exemplo conceptual)
        palavras_prova = ['sms', 'mensagem', 'whatsapp', 'foto', 'video', 'testemunha', 'email', 'fatura']
        encontradas = [p for p in palavras_prova if p in relato_utilizador.lower()]
        
        self.evidencias_encontradas.extend(encontradas)
        self._atualizar_termometro()
        
        return self.gerar_interrogatorio(relato_utilizador)

    def _atualizar_termometro(self):
        """Atualiza a solidez do caso com base na quantidade e qualidade das provas."""
        num_provas = len(self.evidencias_encontradas)
        if num_provas == 0:
            self.termometro_evidencia = "🔴 FRÁGIL (Apenas testemunho verbal)"
        elif 1 <= num_provas <= 2:
            self.termometro_evidencia = "🟡 MODERADA (Existem indícios documentais/digitais)"
        else:
            self.termometro_evidencia = "🟢 SÓLIDA (Múltiplos cruzamentos de prova)"

    def gerar_interrogatorio(self, relato):
        """Identifica o que falta saber conforme o ramo do Direito."""
        perguntas = []
        
        # Lógica simplificada de identificação de lacunas
        if "hora" not in relato.lower() and "data" not in relato.lower():
            perguntas.append("Pode precisar a data e a hora exata do incidente?")
        
        if "testemunha" not in relato.lower():
            perguntas.append("Havia alguém presente que possa confirmar a sua versão?")
            
        if "mensagem" in relato.lower() or "sms" in relato.lower():
            perguntas.append("O conteúdo da mensagem era explícito quanto à intenção?")

        self.lacunas = perguntas
        return perguntas

    def relatorio_para_o_juiz(self):
        """Prepara o resumo factual para o Coletivo de Juízes."""
        return {
            "agente": self.nome,
            "status": self.termometro_evidencia,
            "provas_validadas": self.evidencias_encontradas,
            "conclusao_instrucao": "Pronto para debate" if not self.lacunas else "Aguardar esclarecimentos"
        }

# Exemplo de uso isolado:
# det = DetetiveJudicial()
# print(det.analisar_caso("O meu vizinho partiu o vidro, tenho o SMS aqui."))
