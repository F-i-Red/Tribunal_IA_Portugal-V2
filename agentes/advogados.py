# agentes/advogados.py
# O Embate Jurídico: O Advogado do Diabo (Acusação) vs O Guardião (Defesa)

class Acusacao:
    def __init__(self):
        self.perfil = "Advogado do Diabo"
        self.foco = "Rigor Penal e Tipicidade"

    def construir_tese(self, dados_detetive):
        """Transforma factos em infrações penais/cíveis."""
        provas = dados_detetive['provas_validadas']
        status = dados_detetive['status']
        
        tese = "EXMO. SENHOR JUIZ,\n"
        tese += "A conduta do arguido revela um total desrespeito pelas normas vigentes. "
        
        if 'sms' in provas or 'mensagem' in provas:
            tese += "A prova digital demonstra premeditação e consciência da ilicitude. "
        
        if "🔴" in status:
            tese += "Apesar da escassez de prova física, o clamor social exige uma punição exemplar baseada nos indícios apresentados."
        else:
            tese += "Com provas sólidas, não resta outra alternativa senão a condenação máxima prevista no Código."
            
        return tese

class Defesa:
    def __init__(self):
        self.perfil = "Defensor Garantista"
        self.foco = "Direitos Fundamentais e Atenuantes"

    def construir_tese(self, dados_detetive):
        """Transforma factos em justificações ou dúvidas razoáveis."""
        provas = dados_detetive['provas_validadas']
        
        tese = "MERITÍSSIMO JUIZ,\n"
        tese += "Estamos perante uma situação que exige sensibilidade humana e não apenas frieza mecânica. "
        
        if not provas:
            tese += "In Dubio Pro Reo: Sem provas concretas, qualquer condenação seria um erro judiciário gravíssimo. "
        else:
            tese += f"A presença de {len(provas)} indício(s) não prova a intenção criminosa, apenas o contexto de conflito. "
            
        tese += "O meu constituinte agiu sob pressão e as circunstâncias atenuantes (Art. 71.º e 72.º do CP) devem prevalecer."
        
        return tese
