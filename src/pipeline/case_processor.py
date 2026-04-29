"""
Pipeline principal de processamento de casos jurídicos.
Orquestra anonimização, agentes, watermarking e geração de atas.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from ..utils import get_config, get_logger, get_brain, anonymize_text


@dataclass
class CaseResult:
    """Resultado completo de um caso processado."""
    case_id: str
    trace_id: str
    original_description: str
    anonymized_description: str
    entities_found: List[Dict]
    detetive_report: Optional[str] = None
    acusacao: Optional[str] = None
    defesa: Optional[str] = None
    sentenca_rigorosa: Optional[str] = None
    sentenca_garantista: Optional[str] = None
    sentenca_equilibrada: Optional[str] = None
    ata_final: Optional[str] = None
    custos_estimados: Dict = field(default_factory=dict)
    watermark: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CaseProcessor:
    """
    Processador de casos jurídicos.
    Garante: anonimização → processamento → watermarking → output seguro.
    """

    DISCLAIMER = """
╔══════════════════════════════════════════════════════════════════════╗
║  ⚠️  AVISO LEGAL — DOCUMENTO DE SIMULAÇÃO EDUCATIVA                ║
║                                                                      ║
║  Este documento foi gerado por inteligência artificial e NÃO       ║
║  constitui parecer jurídico, decisão judicial ou documento         ║
║  oficial de qualquer natureza.                                       ║
║                                                                      ║
║  Para questões jurídicas reais, consulte um Advogado inscrito      ║
║  na Ordem dos Advogados de Portugal.                                 ║
║                                                                      ║
║  Hash de verificação: {hash}                                         ║
║  Gerado em: {timestamp}                                              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()
        self.brain = get_brain()

    def process(self, case_description: str) -> CaseResult:
        """
        Processa um caso completo.

        Fluxo:
        1. Anonimização RGPD
        2. Instrução (Detetive)
        3. Alegações (Acusação + Defesa)
        4. Sentenças (3 perfis)
        5. Ata final + Watermarking
        """
        # Iniciar caso
        trace_id = self.logger.start_case(case_description)
        case_id = f"case_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        self.logger.info(f"Iniciando processamento do caso {case_id}")

        # 1. ANONIMIZAÇÃO
        self.logger.set_agent("anonimizador")
        anonymized_text, entities = anonymize_text(case_description)

        self.logger.log_anonymization(
            entities_found=len(entities),
            entity_types=list(set(e.label for e in entities)),
        )

        self.logger.info(f"Anonimização: {len(entities)} entidades mascaradas")

        # 2. INSTRUÇÃO — Detetive
        self.logger.set_agent("detetive")
        detetive_report = self._run_detetive(anonymized_text)

        # 3. ALEGAÇÕES
        self.logger.set_agent("acusacao")
        acusacao = self._run_acusacao(anonymized_text, detetive_report)

        self.logger.set_agent("defesa")
        defesa = self._run_defesa(anonymized_text, detetive_report, acusacao)

        # 4. SENTENÇAS (3 perfis)
        self.logger.set_agent("juiz_rigoroso")
        sentenca_rigorosa = self._run_juiz(anonymized_text, detetive_report, acusacao, defesa, "rigoroso")

        self.logger.set_agent("juiz_garantista")
        sentenca_garantista = self._run_juiz(anonymized_text, detetive_report, acusacao, defesa, "garantista")

        self.logger.set_agent("juiz_equilibrado")
        sentenca_equilibrada = self._run_juiz(anonymized_text, detetive_report, acusacao, defesa, "equilibrado")

        # 5. ATA FINAL
        self.logger.set_agent("escrivao")
        ata = self._generate_ata(
            case_id, trace_id, anonymized_text, detetive_report,
            acusacao, defesa, sentenca_rigorosa, sentenca_garantista, sentenca_equilibrada
        )

        # 6. WATERMARKING
        if self.config.watermark_atas:
            ata = self._add_watermark(ata, case_id, trace_id)

        # 7. DISCLAIMER
        if self.config.disclaimer_obrigatorio:
            ata = self.DISCLAIMER.format(
                hash=self._generate_hash(ata),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ) + "\n\n" + ata

        # Guardar
        if self.config.guardar_atas:
            self._save_ata(ata, case_id)

        result = CaseResult(
            case_id=case_id,
            trace_id=trace_id,
            original_description=case_description,
            anonymized_description=anonymized_text,
            entities_found=[{"text": e.text, "type": e.label, "score": e.score} for e in entities],
            detetive_report=detetive_report,
            acusacao=acusacao,
            defesa=defesa,
            sentenca_rigorosa=sentenca_rigorosa,
            sentenca_garantista=sentenca_garantista,
            sentenca_equilibrada=sentenca_equilibrada,
            ata_final=ata,
        )

        self.logger.info(f"Caso {case_id} processado com sucesso")
        return result

    def _run_detetive(self, case_text: str) -> str:
        """Executa agente Detetive — Instrução factual."""
        system_prompt = """És o Detetive de um Tribunal de Simulação Jurídica Portuguesa.
O teu papel é analisar os factos apresentados, identificar provas necessárias,
e avaliar a força probatória de cada elemento.

Deves:
1. Listar os factos provados e não provados
2. Identificar provas necessárias (testemunhal, documental, pericial)
3. Calcular um "Termómetro de Evidência" (🔴 Fraca / 🟡 Média / 🟢 Forte) para cada facto
4. Sugerir diligências probatórias adicionais

Responde em português europeu, com linguagem técnica mas clara."""

        messages = [{"role": "user", "content": f"Caso a analisar:\n\n{case_text}"}]

        response = self.brain.call(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=3000,
        )

        self.logger.log_agent_action("detetive", "instrucao_completa", {
            "tokens_input": response.tokens_input,
            "tokens_output": response.tokens_output,
        })

        return response.content

    def _run_acusacao(self, case_text: str, detetive_report: str) -> str:
        """Executa agente Acusação."""
        system_prompt = """És o Advogado do Ministério Público num Tribunal Português.
O teu papel é construir a tese de culpa com base nos factos provados.

Deves:
1. Enunciar os factos que consideras provados
2. Qualificar juridicamente os factos (artigos do Código Penal/Civil aplicáveis)
3. Argumentar porque a prova é suficiente para condenação
4. Requerer a aplicação de pena/consequência adequada

Cita SEMPRE os artigos específicos. Se não tiveres a certeza, indica "[verificar artigo]".
Responde em português europeu."""

        messages = [{
            "role": "user",
            "content": f"Caso:\n{case_text}\n\nRelatório do Detetive:\n{detetive_report}"
        }]

        response = self.brain.call(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=3000,
        )

        self.logger.log_agent_action("acusacao", "alegacoes_completas", {
            "tokens_input": response.tokens_input,
            "tokens_output": response.tokens_output,
        })

        return response.content

    def _run_defesa(self, case_text: str, detetive_report: str, acusacao: str) -> str:
        """Executa agente Defesa."""
        system_prompt = """És o Patrono da Defesa num Tribunal Português.
O teu papel é garantir o contraditório e os direitos fundamentais do arguido.

Deves:
1. Contestar os factos não provados ou duvidosos
2. Invocar o princípio in dubio pro reo
3. Identificar violações processuais ou de direitos fundamentais
4. Propor tese alternativa ou atenuantes
5. Invocar jurisprudência favorável quando aplicável

Responde em português europeu."""

        messages = [{
            "role": "user",
            "content": f"Caso:\n{case_text}\n\nRelatório do Detetive:\n{detetive_report}\n\nAlegações da Acusação:\n{acusacao}"
        }]

        response = self.brain.call(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=3000,
        )

        self.logger.log_agent_action("defesa", "alegacoes_completas", {
            "tokens_input": response.tokens_input,
            "tokens_output": response.tokens_output,
        })

        return response.content

    def _run_juiz(self, case_text: str, detetive_report: str, acusacao: str, defesa: str, perfil: str) -> str:
        """Executa juiz com perfil específico."""
        perfis = {
            "rigoroso": "És um Juiz de perfil RIGOROSO. Aplicas estritamente a lei, dás pouca margem à dúvida razoável, e tendes para a condenação quando há indícios suficientes.",
            "garantista": "És um Juiz de perfil GARANTISTA. Priorizas os direitos fundamentais, aplicação rigorosa do in dubio pro reo, e só condenas com prova além de dúvida razoável.",
            "equilibrado": "És um Juiz de perfil EQUILIBRADO. Consideras todos os elementos probatórios, jurisprudência e princípios gerais do direito para uma decisão justa e ponderada.",
        }

        system_prompt = f"""{perfis[perfil]}

Deves:
1. Analisar os factos provados e não provados
2. Avaliar as alegações da acusação e defesa
3. Aplicar a lei e jurisprudência relevante
4. Proferir sentença fundamentada
5. Indicar custas processuais estimadas

A sentença deve ter estrutura formal: cabeçalho, factos provados, fundamentação de direito, dispositivo.
Responde em português europeu."""

        messages = [{
            "role": "user",
            "content": f"Caso:\n{case_text}\n\nRelatório do Detetive:\n{detetive_report}\n\nAcusação:\n{acusacao}\n\nDefesa:\n{defesa}"
        }]

        response = self.brain.call(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=4000,
        )

        self.logger.log_agent_action(f"juiz_{perfil}", "sentenca_proferida", {
            "tokens_input": response.tokens_input,
            "tokens_output": response.tokens_output,
        })

        return response.content

    def _generate_ata(self, case_id: str, trace_id: str, case_text: str,
                      detetive: str, acusacao: str, defesa: str,
                      rigorosa: str, garantista: str, equilibrada: str) -> str:
        """Gera ata final completa."""
        system_prompt = """És o Escrivão do Tribunal. Redige a Ata Oficial do processo.

A ata deve conter:
1. Cabeçalho com identificação do processo
2. Sumário dos factos
3. Síntese das alegações
4. As 3 sentenças (Rigorosa, Garantista, Equilibrada)
5. Tradução para linguagem vulgar de cada sentença
6. Estimativa de custas processuais
7. Considerações finais

Responde em português europeu, formato formal."""

        messages = [{
            "role": "user",
            "content": f"""Processo: {case_id}
Trace: {trace_id}

Caso:\n{case_text}

RELATÓRIO DO DETETIVE:
{detetive}

ALEGAÇÕES DA ACUSAÇÃO:
{acusacao}

ALEGAÇÕES DA DEFESA:
{defesa}

SENTENÇA RIGOROSA:
{rigorosa}

SENTENÇA GARANTISTA:
{garantista}

SENTENÇA EQUILIBRADA:
{equilibrada}
"""
        }]

        response = self.brain.call(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=5000,
        )

        self.logger.log_agent_action("escrivao", "ata_gerada", {
            "tokens_input": response.tokens_input,
            "tokens_output": response.tokens_output,
        })

        return response.content

    def _add_watermark(self, text: str, case_id: str, trace_id: str) -> str:
        """Adiciona watermark criptográfico para provar origem de simulação."""
        watermark_data = f"SIMULACAO_TRIBUNAL_IA|{case_id}|{trace_id}|{datetime.now(timezone.utc).isoformat()}"
        hash_watermark = hashlib.sha256(watermark_data.encode()).hexdigest()[:16]

        watermark = f"""
<!-- WATERMARK: {hash_watermark} -->
<!-- ORIGEM: Tribunal_IA_Portugal | ID: {case_id} | TRACE: {trace_id} -->
<!-- ESTE DOCUMENTO É UMA SIMULAÇÃO EDUCATIVA -->
"""
        return text + watermark

    def _generate_hash(self, text: str) -> str:
        """Gera hash de verificação do documento."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def _save_ata(self, ata: str, case_id: str):
        """Guarda ata em ficheiro."""
        filepath = self.config.pasta_atas / f"{case_id}.txt"
        filepath.write_text(ata, encoding="utf-8")
        self.logger.info(f"Ata guardada em {filepath}")


def process_case(case_description: str) -> CaseResult:
    """Função de conveniência."""
    processor = CaseProcessor()
    return processor.process(case_description)
