"""
Anonimização de entidades sensíveis em textos jurídicos portugueses.
Conformidade com RGPD — mascarar dados antes de enviar para APIs de terceiros.
"""

import hashlib
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class Entity:
    """Entidade identificada no texto."""
    text: str
    start: int
    end: int
    label: str
    score: float


class PortugueseLegalAnonymizer:
    """
    Anonimizador para português jurídico.
    Usa regex especializadas + heurísticas para o domínio legal.
    """

    # Padrões regex para entidades estruturadas
    PATTERNS = {
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "IBAN": re.compile(r"\bPT\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{1}\b"),
        "CC": re.compile(r"\b\d{8}\s*[A-Za-z]{2}\d?\b"),
        "CODIGO_POSTAL": re.compile(r"\b\d{4}-\d{3}\b"),
        "TELEFONE": re.compile(r"\b(?:\+351\s*)?(?:9[1236]\d{7}|2\d{8})\b"),
        "NIF": re.compile(r"\b[1235689]\d{8}\b"),
        "NISS": re.compile(r"\b\d{11}\b"),
        "PROCESSO": re.compile(r"\b\d{3,4}/?\d{2}\.?\d{4}\b"),
    }

    # Cidades portuguesas comuns para deteção
    CIDADES_PT = {
        "lisboa", "porto", "braga", "coimbra", "faro", "aveiro", "guarda", "leiria",
        "viseu", "bragança", "castelo branco", "evora", "beja", "portalegre", "setubal",
        "santarem", "viana do castelo", "vila real", "funchal", "ponta delgada",
        "amadora", "almada", "oeiras", "sintra", "cascais", "loures", "odivelas",
        "vila nova de gaia", "matosinhos", "maia", "gondomar", "portimao", "tavira",
    }

    NAME_PREFIXES = [
        r"arguid[oa]\s+",
        r"r[eé]u\s+",
        r"autor[ea]?\s+",
        r"testemunha\s+",
        r"sr\.?\s+",
        r"sra\.?\s+",
        r"exmo\.?\s+s\.?\s+",
        r"exma\.?\s+s\.?\s+",
        r"doutor[ea]?\s+",
        r"engenheir[oa]?\s+",
        r"senhor[ea]?\s+",
        r"dr\.?\s+",
        r"dra\.?\s+",
        r"professor[ea]?\s+",
        r"advogad[oa]?\s+",
        r"juiz[ea]?\s+",
        r"magistrad[oa]?\s+",
    ]

    BIRTH_CONTEXTS = [
        r"nascid[oa]\s+(?:em|a)\s+",
        r"data\s+de\s+nascimento\s*(?::|de|em)?\s+",
        r"n\.?\s*asc\.?\s*(?::|de|em)?\s+",
        r"nascimento\s*(?::|de|em)?\s+",
    ]

    def __init__(self, salt: str = "tribunal_ia_2024"):
        self.salt = salt
        self._entity_map: Dict[str, str] = {}
        self._next_id: Dict[str, int] = {}

    def _get_pseudonym(self, entity_type: str, original: str) -> str:
        """Gera pseudónimo consistente para uma entidade."""
        key = f"{self.salt}:{entity_type}:{original.lower().strip()}"
        hash_val = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        entity_num = (hash_val % 10000) + 1

        pseudonyms = {
            "PESSOA": f"[PESSOA_{entity_num:04d}]",
            "LOCAL": f"[LOCAL_{entity_num:04d}]",
            "ORGANIZACAO": f"[ENTIDADE_{entity_num:04d}]",
            "MORADA": f"[MORADA_{entity_num:04d}]",
            "NIF": "[NIF_REMOVIDO]",
            "CC": "[CC_REMOVIDO]",
            "NISS": "[NISS_REMOVIDO]",
            "TELEFONE": "[TELEFONE_REMOVIDO]",
            "EMAIL": "[EMAIL_REMOVIDO]",
            "DATA_NASCIMENTO": "[DATA_NASC_REMOVIDA]",
            "PROCESSO": f"[PROCESSO_{entity_num:04d}]",
            "IBAN": "[IBAN_REMOVIDO]",
            "CODIGO_POSTAL": "[CP_REMOVIDO]",
        }

        return pseudonyms.get(entity_type, f"[{entity_type}_{entity_num:04d}]")

    def _find_names(self, text: str) -> List[Entity]:
        """Encontra nomes próprios usando padrões contextuais e heurísticas."""
        entities = []

        # Padrão 1: prefixo + nome próprio (1-5 palavras capitalizadas)
        for prefix in self.NAME_PREFIXES:
            pattern = re.compile(
                f"({prefix})"
                f"([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+"
                f"(?:\\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+){{0,4}})",
                re.IGNORECASE
            )

            for match in pattern.finditer(text):
                name = match.group(2)
                start = match.start(2)
                end = match.end(2)

                if self._is_valid_name(name):
                    entities.append(Entity(name, start, end, "PESSOA", 0.90))

        # Padrão 2: nomes próprios em contexto de testemunhas/vítimas
        context_patterns = [
            r"(?:visto|ouvido|identificado|nomead[oa])\s+(?:por|como)\s+([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+){1,3})",
            r"(?:representad[oa]\s+por|assistido\s+por)\s+([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+){1,3})",
            r":\s+([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+){1,3})",
            r",\s+e\s+([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+){1,3})",
        ]

        for ctx_pat in context_patterns:
            pattern = re.compile(ctx_pat, re.IGNORECASE)
            for match in pattern.finditer(text):
                name = match.group(1)
                start = match.start(1)
                end = match.end(1)
                if self._is_valid_name(name):
                    # Verificar se já não foi detetado
                    if not any(e.start <= start < e.end or e.start < end <= e.end for e in entities):
                        entities.append(Entity(name, start, end, "PESSOA", 0.80))

        # Ordenar por posição
        entities.sort(key=lambda e: e.start)

        # Remover overlaps e duplicados
        filtered = []
        seen = set()
        last_end = -1
        for ent in entities:
            key = (ent.start, ent.end)
            if key not in seen and ent.start >= last_end:
                seen.add(key)
                filtered.append(ent)
                last_end = ent.end

        return filtered

    def _is_valid_name(self, name: str) -> bool:
        """Valida se um nome é plausível."""
        if len(name) < 4:
            return False

        words = name.split()

        if len(words) > 5:
            return False

        # Rejeitar se começa com palavras estruturais
        structure_words = {"em", "na", "no", "de", "do", "da", "dos", "das", "para", "por", 
                          "foi", "tem", "são", "era", "está", "fica", "ficou",
                          "visto", "ouvido", "identificado", "nomeado", "duas", "dois",
                          "uma", "um", "três", "quatro", "cinco"}
        first_word_lower = words[0].lower() if words else ""
        if first_word_lower in structure_words:
            return False

        # Rejeitar se é numeral
        if first_word_lower in {"uma", "um", "duas", "dois", "três", "quatro", "cinco", 
                                "seis", "sete", "oito", "nove", "dez"}:
            return False

        # Rejeitar se é apenas uma palavra comum
        common_single = {"tribunal", "juiz", "advogado", "procurador", "ministerio", "publico",
                        "direito", "lei", "codigo", "artigo", "alinea", "numero", "processo",
                        "autos", "parte", "partes", "sentenca", "acordao", "despacho",
                        "requerente", "requerido", "apelante", "apelado", "recorrente", "recorrido",
                        "relator", "presidente", "vogal", "escrivao", "chefe", "secretario",
                        "nacional", "republica", "portuguesa", "europeu", "uniao", "estado",
                        "comarca", "distrito", "concelho", "freguesia"}

        if len(words) == 1 and words[0].lower() in common_single:
            return False

        # Rejeitar frases com verbos/preposições no meio
        middle_words = {"por", "em", "de", "para", "com", "sem", "sob", "sobre", "entre",
                       "foi", "tem", "são", "era", "está", "fica", "ante", "após", "até",
                       "qualificado", "criminais", "furto", "delito", "crime", "testemunhas",
                       "antecedentes"}

        for w in words[1:-1] if len(words) > 2 else []:
            if w.lower() in middle_words:
                return False

        return True

    def _find_locations(self, text: str) -> List[Entity]:
        """Encontra localizações (tribunais, moradas, cidades)."""
        entities = []

        # Padrão 1: Tribunais
        tribunal_pattern = re.compile(
            r"(Tribunal\s+(?:da\s+)?Comarca\s+de\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+"
            r"|Tribunal\s+(?:da\s+)?[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+"
            r"(?:\s+(?:de\s+)?[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+)*)",
            re.IGNORECASE
        )

        for match in tribunal_pattern.finditer(text):
            entities.append(Entity(match.group(1), match.start(), match.end(), "LOCAL", 0.95))

        # Padrão 2: Moradas completas
        morada_pattern = re.compile(
            r"((?:Rua|Avenida|Av\.?|Praça|Largo|Travessa|Estrada|Alameda|Calçada|"
            r"Beco|Ladeira|Escadinhas)\s+[^,.]{3,80}?"
            r"(?:\s*,\s*[^,.]{2,50}?){0,3}"
            r"(?:\s*,?\s*\d{4}-?\d{0,3})?"
            r"(?:\s*,?\s*[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+)?)",
            re.IGNORECASE
        )

        for match in morada_pattern.finditer(text):
            morada = match.group(1).strip()
            if len(morada.split()) >= 2:
                entities.append(Entity(morada, match.start(), match.end(), "MORADA", 0.85))

        # Padrão 3: Cidades/Localidades conhecidas de Portugal
        for cidade in self.CIDADES_PT:
            pattern = re.compile(rf"\b{cidade}\b", re.IGNORECASE)
            for match in pattern.finditer(text):
                # Verificar se já não está dentro de outra entidade
                if not any(e.start <= match.start() < e.end or e.start < match.end() <= e.end 
                          for e in entities):
                    entities.append(Entity(match.group(), match.start(), match.end(), "LOCAL", 0.85))

        return entities

    def _find_birth_dates(self, text: str) -> List[Entity]:
        """Encontra datas de nascimento (apenas com contexto explícito)."""
        entities = []

        for ctx in self.BIRTH_CONTEXTS:
            pattern = re.compile(
                f"({ctx})"
                f"(\\d{{1,2}}[/-]\\d{{1,2}}[/-]\\d{{2,4}}|"
                f"\\d{{1,2}}\\s+de\\s+(?:janeiro|fevereiro|março|abril|maio|junho|"
                f"julho|agosto|setembro|outubro|novembro|dezembro)\\s+de\\s+\\d{{4}})",
                re.IGNORECASE
            )

            for match in pattern.finditer(text):
                date_str = match.group(2)
                start = match.start(2)
                end = match.end(2)
                entities.append(Entity(date_str, start, end, "DATA_NASCIMENTO", 0.90))

        return entities

    def _find_organizations(self, text: str) -> List[Entity]:
        """Encontra organizações."""
        entities = []

        org_pattern = re.compile(
            r"(?:empresa|sociedade|firma|companhia|organização|instituição|"
            r"banco|seguradora|hospital|clínica|escola|universidade)\s+"
            r"([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+"
            r"(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+){0,3})",
            re.IGNORECASE
        )

        for match in org_pattern.finditer(text):
            org = match.group(1)
            entities.append(Entity(org, match.start(1), match.end(1), "ORGANIZACAO", 0.80))

        return entities

    def anonymize(self, text: str) -> Tuple[str, List[Entity]]:
        """Anonimiza texto jurídico."""
        all_entities: List[Entity] = []

        # 1. Encontrar entidades estruturadas
        for entity_type, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                all_entities.append(Entity(
                    match.group(),
                    match.start(),
                    match.end(),
                    entity_type,
                    0.95
                ))

        # 2. Encontrar nomes de pessoas
        all_entities.extend(self._find_names(text))

        # 3. Encontrar localizações e moradas
        all_entities.extend(self._find_locations(text))

        # 4. Encontrar datas de nascimento
        all_entities.extend(self._find_birth_dates(text))

        # 5. Encontrar organizações
        all_entities.extend(self._find_organizations(text))

        # Ordenar por posição e remover overlaps
        all_entities.sort(key=lambda e: e.start)
        filtered_entities = []
        last_end = -1
        for ent in all_entities:
            if ent.start >= last_end:
                filtered_entities.append(ent)
                last_end = ent.end

        # Aplicar substituições (de trás para frente)
        result = text
        for ent in reversed(filtered_entities):
            pseudonym = self._get_pseudonym(ent.label, ent.text)
            result = result[:ent.start] + pseudonym + result[ent.end:]

        return result, filtered_entities

    def deanonymize(self, anonymized_text: str, original_entities: List[Entity]) -> str:
        """Reverte anonimização (debugging interno)."""
        result = anonymized_text
        for ent in original_entities:
            pseudonym = self._get_pseudonym(ent.label, ent.text)
            result = result.replace(pseudonym, ent.text, 1)
        return result


def anonymize_text(text: str) -> Tuple[str, List[Entity]]:
    """Função de conveniência."""
    anonymizer = PortugueseLegalAnonymizer()
    return anonymizer.anonymize(text)
