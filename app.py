"""
Tribunal IA Portugal — Interface Web (Fase 3)
Corre com: streamlit run app.py
"""

import time
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Tribunal IA Portugal",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #0f1117; }

/* Texto geral mais claro */
.stApp, .stApp p, .stApp div, .stApp span, .stApp label {
    color: #e8eaf0 !important;
}
.stMarkdown p, .stMarkdown li, .stMarkdown div {
    color: #e8eaf0 !important;
}

/* Banner */
.banner {
    background: linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%);
    border: 1px solid #4a5568;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
}
.banner h1 { color: #ffffff; font-size: 2rem; margin: 0; }
.banner p  { color: #c8d0e0; margin: 0.5rem 0 0; }

/* Caixa de cada agente */
.agente-header {
    border-left: 4px solid #4299e1;
    background: #1e2540;
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 1rem;
    margin: 1rem 0 0.3rem 0;
}
.agente-nome {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* Texto de streaming */
.stream-text {
    background: #141826;
    border-radius: 0 0 8px 8px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #dde3f0 !important;
    white-space: pre-wrap;
    font-family: 'Segoe UI', sans-serif;
    max-height: 450px;
    overflow-y: auto;
    border-left: 4px solid #2d3748;
}

/* Cartões dos três juízes */
.juiz-card {
    background: #1a2035;
    border-radius: 10px;
    padding: 1.2rem;
    min-height: 200px;
}
.juiz-titulo {
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
}
.juiz-desc {
    color: #b0bcd4 !important;
    font-size: 0.78rem;
    margin-bottom: 0.8rem;
}
.dispositivo {
    background: #2d3748;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-top: 0.8rem;
    font-weight: 600;
    font-size: 0.88rem;
    color: #f0f4ff !important;
    line-height: 1.5;
}

/* Questão de instrução */
.questao-box {
    background: #1e2535;
    border: 1px solid #3a4560;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    color: #dde3f0 !important;
}
.questao-critica { border-color: #fc8181 !important; }

/* Aviso legal */
.aviso-legal {
    background: #1e2230;
    border: 1px solid #f6e05e;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    color: #f6e05e !important;
    font-size: 0.88rem;
    margin-bottom: 1.2rem;
}
.aviso-legal a { color: #f6e05e; }

/* Ata */
.ata-section {
    background: #141826;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-size: 0.85rem;
    line-height: 1.7;
    color: #dde3f0 !important;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    max-height: 600px;
    overflow-y: auto;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0d1020 !important;
}
section[data-testid="stSidebar"] * {
    color: #dde3f0 !important;
}

/* Inputs */
.stTextArea textarea, .stTextInput input {
    background-color: #1e2535 !important;
    color: #f0f4ff !important;
    border-color: #3a4560 !important;
}
.stTextArea label, .stTextInput label {
    color: #b0bcd4 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #b0bcd4 !important;
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
}

/* Expander */
.streamlit-expanderHeader {
    color: #dde3f0 !important;
    background: #1e2535 !important;
}

/* Métricas */
[data-testid="stMetric"] {
    background: #1a2035;
    border-radius: 8px;
    padding: 0.8rem;
}
[data-testid="stMetricLabel"] { color: #b0bcd4 !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; }

/* Barra de progresso */
.stProgress > div > div {
    background-color: #4299e1 !important;
}

/* Selects e botões */
.stSelectbox select { color: #f0f4ff !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "fase": "inicio",
        "caso_texto": "",
        "instancia_codigo": None,
        "perguntas": [],
        "respostas": {},
        "materiais": [],
        "resultado": None,
        "_intro_instrucao": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


def carregar_config():
    try:
        import src.utils.config as cfg_mod
        cfg_mod._config = None
        from src.utils.config import get_config, ConfigError
        return get_config(), None
    except Exception as e:
        return None, str(e)


CORES = {
    "detetive":          "#63b3ed",
    "acusacao":          "#fc8181",
    "defesa":            "#68d391",
    "juiz_rigoroso":     "#fc8181",
    "juiz_garantista":   "#68d391",
    "juiz_equilibrado":  "#f6e05e",
    "instrucao":         "#f6e05e",
    "escrivao":          "#a0aec0",
}
EMOJIS = {
    "detetive":          "🔍",
    "acusacao":          "⚔️",
    "defesa":            "🛡️",
    "juiz_rigoroso":     "⚖️",
    "juiz_garantista":   "🕊️",
    "juiz_equilibrado":  "🔮",
    "instrucao":         "📋",
    "escrivao":          "📝",
}
NOMES = {
    "detetive":          "Detetive de Instrução",
    "acusacao":          "Ministério Público — Acusação",
    "defesa":            "Defensor — Alegações de Defesa",
    "juiz_rigoroso":     "Juiz — Perfil Rigoroso",
    "juiz_garantista":   "Juiz — Perfil Garantista",
    "juiz_equilibrado":  "Juiz — Perfil Equilibrado",
    "instrucao":         "Juiz de Instrução",
    "escrivao":          "Escrivão",
}

def cor(nome):   return CORES.get(nome, "#cbd5e0")
def emoji(nome): return EMOJIS.get(nome, "🏛️")
def nome_ag(n):  return NOMES.get(n, n.upper())


def extrair_dispositivo(texto: str) -> str:
    import re
    m = re.search(
        r"(?:==\s*6\.\s*DISPOSITIVO\s*==|##\s*6\.\s*DISPOSITIVO|"
        r"\*\*6\.\s*DISPOSITIVO\*\*)\s*\n+(.*?)(?:\n==|\n##|\n\*\*|\Z)",
        texto, re.IGNORECASE | re.DOTALL
    )
    if m:
        return m.group(1).strip()[:500]
    m = re.search(
        r"(?:O Tribunal DECIDE[:\s]+|CONDENA|ABSOLVE|PRONUNCIA|NÃO\s+PRONUNCIA|"
        r"JULGA\s+PROCEDENTE|JULGA\s+IMPROCEDENTE)[^.]*\.",
        texto, re.IGNORECASE
    )
    if m:
        return m.group(0).strip()
    return texto.strip()[:300] + "..."


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuração")
    cfg, err_cfg = carregar_config()

    if cfg:
        st.success("✅ API conectada")
        modelo = cfg.modelo
        gratuito = modelo.endswith(":free") or "free" in modelo
        st.markdown(f"**Modelo activo:**")
        st.code(modelo, language=None)
        if gratuito:
            st.warning("🟢 Modelo gratuito")
        else:
            st.success("💛 Modelo pago")
        st.caption("Para mudar: edita `.env` → linha `MODELO=`")
        with st.expander("Ver modelos disponíveis"):
            modelos = [
                ("🟢", "openrouter/free", "auto gratuito"),
                ("🟢", "deepseek/deepseek-chat-v3-0324:free", "DeepSeek gratuito"),
                ("🟢", "meta-llama/llama-4-maverick:free", "Llama 4 gratuito"),
                ("🟢", "mistralai/mistral-small-3.1-24b-instruct:free", "Mistral gratuito"),
                ("💛", "anthropic/claude-haiku-4-5", "~0.01€/caso"),
                ("💛", "google/gemini-2.0-flash-001", "~0.01€/caso"),
                ("🔴", "anthropic/claude-sonnet-4.6", "~0.05€/caso"),
            ]
            for icon, m, desc in modelos:
                st.markdown(f"`{icon} {m}`  \n_{desc}_")
    else:
        st.error(f"❌ {err_cfg}")

    st.markdown("---")
    try:
        from src.rag import MotorRAG
        rag_s = MotorRAG(Path("."))
        n_s = rag_s.indexar()
        stats_s = rag_s.estatisticas()
        st.markdown("### 📚 Base RAG")
        col1, col2 = st.columns(2)
        col1.metric("Fragmentos", n_s)
        col2.metric("Fontes", len(stats_s["fontes"]))
    except Exception:
        pass

    st.markdown("---")
    if st.button("🔄 Novo caso", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ── BANNER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="banner">
    <h1>🏛️ TRIBUNAL IA PORTUGAL 🇵🇹</h1>
    <p>Simulador judicial de alta fidelidade — Fins exclusivamente educativos e de simulação</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# FASE: INÍCIO
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.fase == "inicio":
    st.markdown("""
<div class="aviso-legal">
⚠️ <strong>AVISO LEGAL OBRIGATÓRIO</strong><br><br>
Este simulador gera decisões judiciais fictícias por inteligência artificial.<br>
<strong>NÃO constitui parecer jurídico, decisão judicial ou documento oficial de qualquer natureza.</strong><br><br>
Para situações reais, consulte sempre um Advogado inscrito na<br>
Ordem dos Advogados de Portugal: <a href="https://www.oa.pt">www.oa.pt</a>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ Aceito as condições — Iniciar", use_container_width=True, type="primary"):
            st.session_state.fase = "caso"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# FASE: DESCRIÇÃO DO CASO
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.fase == "caso":
    st.markdown("## 📝 Descrição do Caso")
    st.markdown("Descreve o caso com o máximo de detalhe. Não precisas de usar termos jurídicos — usa linguagem comum.")

    caso = st.text_area(
        "Descreve o caso:",
        height=280,
        placeholder="Ex: Sou o João e o meu vizinho faz barulho todas as noites...",
        value=st.session_state.caso_texto,
        label_visibility="collapsed",
    )

    col1, col2, col3 = st.columns([2, 2, 1])
    with col3:
        avancar = st.button("Avançar →", use_container_width=True, type="primary",
                            disabled=len(caso.strip()) < 30)
    with col1:
        if len(caso.strip()) < 30:
            st.info("Escreve pelo menos 30 caracteres.")
        else:
            st.success(f"✅ {len(caso.strip())} caracteres")

    if avancar and len(caso.strip()) >= 30:
        st.session_state.caso_texto = caso
        st.session_state.fase = "tribunal"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# FASE: SELECÇÃO DO TRIBUNAL
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.fase == "tribunal":
    from src.pipeline.instancias import INSTANCIAS, detectar_instancia_por_keywords

    st.markdown("## 🏛️ Selecção do Tribunal")

    codigo_auto = detectar_instancia_por_keywords(st.session_state.caso_texto)
    inst_auto = INSTANCIAS[codigo_auto]

    st.markdown("### 🤖 Sugestão automática")
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{inst_auto.nome}**")
            st.markdown(f"Matéria: **{inst_auto.materia}** · Diploma: `{inst_auto.diploma_principal}`")
            st.markdown(f"_{inst_auto.descricao}_")
        with col2:
            if st.button("✅ Usar este", use_container_width=True, type="primary"):
                st.session_state.instancia_codigo = codigo_auto
                st.session_state.fase = "instrucao"
                st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Ou escolhe manualmente:")

    grupos = {
        "⚖️ Penal": ["TIC", "TCCR", "TCIC"],
        "📋 Cível": ["TC_CIVEL"],
        "👨‍👩‍👧 Família": ["TFM"],
        "💼 Trabalho": ["TRAB"],
        "🏛️ Administrativo": ["TAF"],
        "🏢 Comercial": ["TCOM"],
        "🔼 Recursos": ["TR", "STJ"],
        "📜 Constitucional": ["TC"],
    }
    for grupo, codigos in grupos.items():
        with st.expander(grupo):
            for codigo in codigos:
                inst = INSTANCIAS[codigo]
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{inst.nome}** — _{inst.materia}_")
                with c2:
                    if st.button("Escolher", key=f"t_{codigo}"):
                        st.session_state.instancia_codigo = codigo
                        st.session_state.fase = "instrucao"
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# FASE: INSTRUÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.fase == "instrucao":
    from src.pipeline.instancias import INSTANCIAS
    from src.pipeline.case_processor import CaseProcessor

    inst = INSTANCIAS[st.session_state.instancia_codigo]
    st.markdown(f"## 🔍 Fase de Instrução — {inst.nome}")
    st.markdown(f"O **{inst.termo_mp}** e o **Juiz de Instrução** analisam o caso e solicitam esclarecimentos.")

    if not st.session_state.perguntas:
        with st.spinner("⏳ A analisar o caso e preparar questões..."):
            processor = CaseProcessor()
            resultado = processor.gerar_perguntas_instrucao(
                st.session_state.caso_texto,
                st.session_state.instancia_codigo
            )
            st.session_state.perguntas = resultado.get("perguntas", [])
            st.session_state._intro_instrucao = resultado.get("introducao", "")
        st.rerun()

    if st.session_state._intro_instrucao:
        st.markdown(f"""
<div class="agente-header" style="border-color:{cor('instrucao')}">
    <div class="agente-nome" style="color:{cor('instrucao')}">{emoji('instrucao')} Juiz de Instrução</div>
</div>
<div class="stream-text">{st.session_state._intro_instrucao}</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    perguntas = st.session_state.perguntas

    for i, p in enumerate(perguntas, 1):
        critica = p.get("importancia") == "critica"
        cor_borda = "#fc8181" if critica else "#3a4560"
        badge = "⚠️ CRÍTICA" if critica else "ℹ️ RELEVANTE"
        st.markdown(f"""
<div class="questao-box" style="border-color:{cor_borda}">
    <span style="font-size:0.72rem;color:#9ab0d0">{badge} — {p['categoria']}</span><br>
    <span style="color:#f0f4ff;font-weight:500">❓ {i}/{len(perguntas)} — {p['texto']}</span>
</div>
""", unsafe_allow_html=True)

        resp_atual = st.session_state.respostas.get(p["id"], {}).get("resposta", "")
        if resp_atual == "Sem resposta":
            resp_atual = ""

        resp = st.text_area(
            f"Resposta à questão {i}",
            key=f"r_{p['id']}",
            height=80,
            placeholder="A tua resposta (deixa em branco para saltar)...",
            value=resp_atual,
            label_visibility="collapsed",
        )
        if resp.strip():
            st.session_state.respostas[p["id"]] = {
                "pergunta": p["texto"],
                "resposta": resp.strip(),
                "categoria": p["categoria"],
            }

        if p.get("aceita_documentos") and resp.strip():
            doc = st.text_input(
                f"Documento/prova para questão {i} (opcional)",
                key=f"d_{p['id']}",
                placeholder="Descreve o documento ou prova...",
                label_visibility="collapsed",
            )
            if doc.strip():
                already = any(m["questao_id"] == p["id"] for m in st.session_state.materiais)
                if not already:
                    st.session_state.materiais.append({"questao_id": p["id"], "descricao": doc.strip()})

        st.markdown("")

    respondidas = sum(1 for r in st.session_state.respostas.values()
                      if r.get("resposta") and r["resposta"] != "Sem resposta")
    st.markdown(f"**{respondidas}/{len(perguntas)}** questões respondidas")
    st.markdown("---")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("⏭️ Saltar instrução", use_container_width=True):
            st.session_state.fase = "processamento"
            st.rerun()
    with col2:
        if st.button("⚖️ Avançar para julgamento →", use_container_width=True, type="primary"):
            st.session_state.fase = "processamento"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# FASE: PROCESSAMENTO COM STREAMING REAL
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.fase == "processamento":
    from src.pipeline.instancias import INSTANCIAS
    from src.utils import get_brain, anonymize_text
    from src.rag import MotorRAG

    inst = INSTANCIAS[st.session_state.instancia_codigo]
    st.markdown(f"## ⚖️ A processar — {inst.nome}")
    st.markdown("Os intervenientes vão apresentando as suas peças à medida que as redigem.")
    st.markdown("---")

    brain = get_brain()
    rag = MotorRAG(Path("."))
    rag.indexar()

    dados_instrucao = {
        "respostas": st.session_state.respostas,
        "materiais": st.session_state.materiais,
    }

    # Anonimizar
    status = st.empty()
    status.markdown("🔒 **A anonimizar dados sensíveis...**")
    anon_text, entities = anonymize_text(st.session_state.caso_texto)

    def fmt_instrucao(dados):
        if not dados or not dados.get("respostas"):
            return ""
        linhas = ["\n\n═══ ESCLARECIMENTOS DA INSTRUÇÃO ═══\n"]
        for item in dados["respostas"].values():
            if item.get("resposta") and item["resposta"] != "Sem resposta":
                linhas.append(f"[{item['categoria']}] {item['pergunta']}")
                linhas.append(f"→ {item['resposta']}\n")
        linhas.append("═══════════════════════════════════\n")
        return "\n".join(linhas)

    ctx_instrucao = fmt_instrucao(dados_instrucao)

    # ── Função de streaming com placeholder FORA do with ──────────────────────
    def stream_agente(nome: str, system_prompt: str, user_content: str) -> str:
        """
        Mostra cabeçalho do agente e faz streaming do texto token a token.
        O placeholder é criado no scope principal para que o Streamlit
        consiga actualizá-lo durante o loop de streaming.
        """
        c = cor(nome)
        # Cabeçalho fixo
        st.markdown(f"""
<div class="agente-header" style="border-color:{c}">
    <div class="agente-nome" style="color:{c}">{emoji(nome)} {nome_ag(nome)}</div>
</div>
""", unsafe_allow_html=True)

        # Placeholder para o texto — criado NO scope principal
        placeholder = st.empty()
        placeholder.markdown(
            '<div class="stream-text" style="color:#9ab0d0;font-style:italic">A redigir...</div>',
            unsafe_allow_html=True,
        )

        texto = ""
        try:
            for chunk in brain.stream(
                messages=[{"role": "user", "content": user_content}],
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=2000,
            ):
                texto += chunk
                # Actualizar em tempo real — funciona porque placeholder está no scope certo
                placeholder.markdown(
                    f'<div class="stream-text">{texto}</div>',
                    unsafe_allow_html=True,
                )
        except Exception as e:
            texto = f"[Erro: {e}]"
            placeholder.error(texto)

        if not texto.strip():
            texto = f"[{nome}: resposta vazia — tenta outro modelo no .env]"
            placeholder.warning(texto)

        return texto

    # ── RAG context ───────────────────────────────────────────────────────────
    frags = rag.pesquisar(anon_text, n_resultados=4)
    ctx_rag = rag.formatar_contexto(frags, max_chars=1800) if frags else ""

    status.markdown("✅ Anonimização concluída. A iniciar os agentes...")

    # ── DETETIVE ──────────────────────────────────────────────────────────────
    sp_det = f"""És o Detetive de Instrução do {inst.nome}, Portugal.
Diploma: {inst.diploma_principal}

Produz RELATÓRIO DE INSTRUÇÃO FACTUAL com estas secções obrigatórias:
== FACTOS ALEGADOS ==
== FACTOS PROVADOS == (cada facto com 🔴 Fraca / 🟡 Média / 🟢 Forte evidência)
== FACTOS NÃO PROVADOS ==
== PROVAS DISPONÍVEIS == (testemunhal, documental, pericial)
== DILIGÊNCIAS RECOMENDADAS ==
== PRAZOS DE PRESCRIÇÃO ==

Português europeu, linguagem técnica e factual."""

    detetive = stream_agente(
        "detetive", sp_det,
        f"CASO:\n{anon_text}{ctx_instrucao}\n\n{ctx_rag}"
    )

    # ── ACUSAÇÃO ──────────────────────────────────────────────────────────────
    frags_lei = rag.pesquisar(anon_text, n_resultados=3, tipo_filtro="lei")
    ctx_lei = rag.formatar_contexto(frags_lei, max_chars=1200) if frags_lei else ""

    sp_ac = f"""És o {inst.termo_mp} do {inst.nome}, Portugal.
Diploma: {inst.diploma_principal}

Rediges as ALEGAÇÕES DA ACUSAÇÃO com:
== FACTOS IMPUTADOS AO {inst.termo_acusado.upper()} ==
== QUALIFICAÇÃO JURÍDICA == (artigos concretos; se incerto: [art.?])
== FUNDAMENTAÇÃO PROBATÓRIA ==
== PEDIDO ==

Português europeu, linguagem jurídica formal."""

    acusacao = stream_agente(
        "acusacao", sp_ac,
        f"CASO:\n{anon_text}\n\nINSTRUÇÃO:\n{detetive}\n\n{ctx_lei}"
    )

    # ── DEFESA ────────────────────────────────────────────────────────────────
    sp_def = f"""És o {inst.termo_defesa} da Defesa no {inst.nome}, Portugal.
Diploma: {inst.diploma_principal}

Rediges as ALEGAÇÕES DA DEFESA com:
== CONTESTAÇÃO DOS FACTOS ==
== DIREITOS FUNDAMENTAIS E GARANTIAS PROCESSUAIS == (CRP, CEDH, {inst.diploma_principal})
== TESE ALTERNATIVA ==
== IN DUBIO PRO REO ==
== PEDIDO ==

Português europeu, linguagem jurídica formal."""

    defesa = stream_agente(
        "defesa", sp_def,
        f"CASO:\n{anon_text}\n\nINSTRUÇÃO:\n{detetive[:800]}\n\nACUSAÇÃO:\n{acusacao[:1000]}"
    )

    # ── TRÊS JUÍZES ───────────────────────────────────────────────────────────
    perfis = [
        ("juiz_rigoroso",    "RIGOROSO",    "Aplicas estritamente a lei. Tende para a condenação perante indícios razoáveis."),
        ("juiz_garantista",  "GARANTISTA",  "Só condenas com prova sólida além de dúvida razoável. In dubio pro reo é máxima."),
        ("juiz_equilibrado", "EQUILIBRADO", "Ponderado e proporcional. Decisão justa e bem fundamentada."),
    ]
    sentencas = {}
    ctx_juiz = (f"CASO:\n{anon_text[:1000]}\n\n"
                f"INSTRUÇÃO:\n{detetive[:600]}\n\n"
                f"ACUSAÇÃO:\n{acusacao[:500]}\n\n"
                f"DEFESA:\n{defesa[:500]}")

    for nome_j, perfil, desc in perfis:
        sp_j = f"""FUNÇÃO: Juiz {perfil} — {inst.nome} — Portugal
PERFIL: {desc}
DIPLOMA: {inst.diploma_principal}
PARTES: {inst.termo_acusado} | {inst.termo_vitima}

Escreve um {inst.termo_decisao} judicial formal com EXACTAMENTE estas 8 secções.
NÃO escrevas conselhos nem texto na primeira pessoa. APENAS decisão judicial.

== 1. RELATÓRIO ==
[Identifica partes e sintetiza processo em 3-5 frases]
== 2. FACTOS PROVADOS ==
[Lista numerada]
== 3. FACTOS NÃO PROVADOS ==
[Lista]
== 4. MOTIVAÇÃO DA DECISÃO DE FACTO ==
[Análise crítica das provas]
== 5. FUNDAMENTAÇÃO JURÍDICA ==
[Artigos do {inst.diploma_principal}]
== 6. DISPOSITIVO ==
[Começa OBRIGATORIAMENTE com: "O Tribunal DECIDE:" seguido de CONDENA/ABSOLVE/PRONUNCIA/NÃO PRONUNCIA + pena/sanção]
== 7. CUSTAS ==
[Estimativa]
== 8. NOTA ACESSÍVEL ==
[3-4 frases em linguagem comum explicando a decisão para qualquer cidadão]"""

        sentencas[nome_j] = stream_agente(nome_j, sp_j, ctx_juiz)

    # Guardar resultado
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    meses = ["janeiro","fevereiro","março","abril","maio","junho",
             "julho","agosto","setembro","outubro","novembro","dezembro"]
    data_pt = f"{now.day} de {meses[now.month-1]} de {now.year}, {now.strftime('%H:%M')} UTC"
    case_id = f"case_{now.strftime('%Y%m%d_%H%M%S')}"

    st.session_state.resultado = {
        "case_id": case_id,
        "data": data_pt,
        "inst": inst,
        "anon_text": anon_text,
        "entities": entities,
        "detetive": detetive,
        "acusacao": acusacao,
        "defesa": defesa,
        "sentencas": sentencas,
        "dados_instrucao": dados_instrucao,
        "rag_fontes": [f.fonte for f in frags],
    }

    status.markdown("✅ **Processamento concluído!**")
    time.sleep(0.8)
    st.session_state.fase = "resultado"
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# FASE: RESULTADO
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.fase == "resultado":
    from src.rag import ValidadorCitacoes
    import hashlib

    r = st.session_state.resultado
    inst = r["inst"]

    st.markdown(f"## ✅ Processo concluído — `{r['case_id']}`")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tribunal", inst.nome_curto)
    col2.metric("Entidades protegidas", len(r["entities"]))
    col3.metric("Fontes RAG", len(set(r["rag_fontes"])))
    col4.metric("Data", r["data"].split(",")[0])

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚖️ Três Sentenças",
        "🔍 Instrução + Peças",
        "📄 Ata Completa",
        "✅ Validação RAG",
        "🔒 Anonimização",
    ])

    # ── TAB 1: TRÊS SENTENÇAS ─────────────────────────────────────────────────
    with tab1:
        st.markdown("### Os três perfis de decisão — mesmo caso, perspectivas diferentes")
        st.markdown(
            "A divergência reflecte a tensão entre **segurança jurídica** (Rigoroso), "
            "**garantias processuais** (Garantista) e **proporcionalidade** (Equilibrado)."
        )
        st.markdown("")

        c_r, c_g, c_e = st.columns(3)
        perfis_display = [
            ("juiz_rigoroso",    c_r, "#fc8181", "⚖️ Perfil Rigoroso",    "Aplica estritamente a lei. Tende para condenação."),
            ("juiz_garantista",  c_g, "#68d391", "🕊️ Perfil Garantista",  "Prioriza direitos fundamentais. Exige prova sólida."),
            ("juiz_equilibrado", c_e, "#f6e05e", "🔮 Perfil Equilibrado", "Ponderado e proporcional."),
        ]
        for nome_j, col, c, titulo, desc in perfis_display:
            texto = r["sentencas"].get(nome_j, "")
            dispositivo = extrair_dispositivo(texto)
            with col:
                st.markdown(f"""
<div class="juiz-card" style="border-top:4px solid {c}">
    <div class="juiz-titulo" style="color:{c}">{titulo}</div>
    <div class="juiz-desc">{desc}</div>
    <div class="dispositivo">{dispositivo}</div>
</div>
""", unsafe_allow_html=True)
                st.markdown("")
                with st.expander("Ver sentença completa"):
                    st.markdown(
                        f'<div class="ata-section">{texto}</div>',
                        unsafe_allow_html=True
                    )

    # ── TAB 2: INSTRUÇÃO + PEÇAS ──────────────────────────────────────────────
    with tab2:
        for nome, texto, etiqueta in [
            ("detetive", r["detetive"], "🔍 Relatório de Instrução Factual"),
            ("acusacao", r["acusacao"], "⚔️ Alegações da Acusação"),
            ("defesa",   r["defesa"],   "🛡️ Alegações da Defesa"),
        ]:
            c = cor(nome)
            with st.expander(etiqueta, expanded=(nome == "detetive")):
                st.markdown(
                    f'<div style="color:{c};font-weight:700;margin-bottom:0.5rem">'
                    f'{emoji(nome)} {nome_ag(nome)}</div>'
                    f'<div class="ata-section">{texto}</div>',
                    unsafe_allow_html=True
                )

        if r["dados_instrucao"] and r["dados_instrucao"].get("respostas"):
            st.markdown("---")
            st.markdown("### 📋 Esclarecimentos prestados na instrução")
            for item in r["dados_instrucao"]["respostas"].values():
                if item.get("resposta") and item["resposta"] != "Sem resposta":
                    st.markdown(f"**[{item['categoria']}]** {item['pergunta']}")
                    st.markdown(f"→ _{item['resposta']}_")
                    st.markdown("")

    # ── TAB 3: ATA COMPLETA ───────────────────────────────────────────────────
    with tab3:
        meses = ["janeiro","fevereiro","março","abril","maio","junho",
                 "julho","agosto","setembro","outubro","novembro","dezembro"]
        ata_linhas = [
            f"{'═'*70}",
            f"ATA DE SIMULAÇÃO JUDICIAL — TRIBUNAL IA PORTUGAL",
            f"{'═'*70}",
            f"",
            f"PROCESSO Nº : {r['case_id']}",
            f"TRIBUNAL    : {inst.nome}",
            f"MATÉRIA     : {inst.materia}",
            f"DIPLOMA     : {inst.diploma_principal}",
            f"DATA        : {r['data']}",
            f"ESTADO      : SIMULAÇÃO EDUCATIVA — SEM VALOR JURÍDICO",
            f"",
            f"{'═'*70}",
            f"SECÇÃO I — CASO (ANONIMIZADO — RGPD)",
            f"{'═'*70}",
            r["anon_text"],
            f"",
            f"{'═'*70}",
            f"SECÇÃO II — RELATÓRIO DE INSTRUÇÃO (DETETIVE)",
            f"{'═'*70}",
            r["detetive"],
            f"",
            f"{'═'*70}",
            f"SECÇÃO III — ALEGAÇÕES DA ACUSAÇÃO",
            f"{'═'*70}",
            r["acusacao"],
            f"",
            f"{'═'*70}",
            f"SECÇÃO IV — ALEGAÇÕES DA DEFESA",
            f"{'═'*70}",
            r["defesa"],
            f"",
            f"{'═'*70}",
            f"SECÇÃO V — SENTENÇA: PERFIL RIGOROSO",
            f"{'═'*70}",
            r["sentencas"].get("juiz_rigoroso", ""),
            f"",
            f"{'═'*70}",
            f"SECÇÃO VI — SENTENÇA: PERFIL GARANTISTA",
            f"{'═'*70}",
            r["sentencas"].get("juiz_garantista", ""),
            f"",
            f"{'═'*70}",
            f"SECÇÃO VII — SENTENÇA: PERFIL EQUILIBRADO",
            f"{'═'*70}",
            r["sentencas"].get("juiz_equilibrado", ""),
            f"",
            f"{'─'*70}",
            f"WATERMARK — SIMULAÇÃO TRIBUNAL IA PORTUGAL",
            f"Hash: {hashlib.sha256(r['case_id'].encode()).hexdigest()[:16]}",
            f"ID: {r['case_id']}",
            f"DOCUMENTO DE SIMULAÇÃO EDUCATIVA SEM VALOR JURÍDICO",
            f"{'─'*70}",
        ]
        ata_texto = "\n".join(ata_linhas)

        st.download_button(
            "⬇️ Descarregar Ata (.txt)",
            data=ata_texto.encode("utf-8"),
            file_name=f"{r['case_id']}.txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.markdown(
            f'<div class="ata-section">{ata_texto[:10000]}'
            f'{"..." if len(ata_texto) > 10000 else ""}</div>',
            unsafe_allow_html=True
        )

    # ── TAB 4: VALIDAÇÃO RAG ──────────────────────────────────────────────────
    with tab4:
        st.markdown("### Validação de citações jurídicas")
        texto_total = " ".join([r["acusacao"], r["defesa"]] + list(r["sentencas"].values()))
        val = ValidadorCitacoes(Path("data/leis"))
        _, problemas = val.validar_texto(texto_total)

        if not problemas:
            st.success("✅ Todas as citações verificadas nos ficheiros locais.")
        else:
            st.warning(f"⚠️ {len(problemas)} citação(ões) não verificada(s):")
            for p in problemas:
                st.markdown(f"• `{p['artigo']}` — {p['mensagem']}")
            st.info("Citações não verificadas podem ser correctas mas ausentes dos ficheiros locais.")

        st.markdown("---")
        st.markdown("### Fontes RAG consultadas")
        for f in set(r["rag_fontes"]):
            st.markdown(f"• {f}")

    # ── TAB 5: ANONIMIZAÇÃO ───────────────────────────────────────────────────
    with tab5:
        st.markdown("### Entidades protegidas (RGPD)")
        tipos = {}
        for e in r["entities"]:
            tipos[e.label] = tipos.get(e.label, 0) + 1
        for tipo, count in sorted(tipos.items()):
            st.markdown(f"• **{tipo}**: {count} ocorrência(s)")

        st.markdown("---")
        st.markdown("### Texto enviado à API (anonimizado)")
        st.text_area(
            "Texto anonimizado",
            value=r["anon_text"],
            height=200,
            disabled=True,
            label_visibility="collapsed",
        )

    # Botão novo caso
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Processar novo caso", use_container_width=True, type="primary"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
