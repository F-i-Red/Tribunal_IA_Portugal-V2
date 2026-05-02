# 🏛️ Tribunal IA Portugal — V2

Simulador judicial de alta fidelidade para o sistema jurídico português.

> ⚠️ **Fins exclusivamente educativos e de simulação. Não constitui parecer jurídico.**

---

## O que há de novo na V2

### Fase de Instrução Interativa *(novidade principal)*
Após descrever o caso, o **Juiz de Instrução** (IA) analisa automaticamente o que falta e faz-lhe perguntas concretas:
- Que factos estão em falta
- Que provas são necessárias
- Que testemunhas existem
- Circunstâncias relevantes para a qualificação jurídica

Pode responder a cada questão, apresentar documentos/provas em texto, saltar questões (N/A) ou terminar a instrução antecipadamente. **Todas as respostas são integradas no relatório do Detetive e nas sentenças.**

### Detecção automática de instância judicial
O sistema identifica automaticamente o tipo de tribunal mais adequado com base no caso descrito (Tribunal de Comarca, Instrução Criminal, Trabalho, Administrativo, etc.).

### Melhorias adicionais
- Anonimização melhorada (moradas, cidades, tribunais, contextos informais)
- Sentença com estrutura formal completa (factos provados, fundamentação, dispositivo, tradução)
- Ata com comparação das 3 sentenças e estimativa de custas
- Aviso legal obrigatório antes de iniciar

---

## Instalação

```bash
# 1. Clonar
git clone https://github.com/F-i-Red/Tribunal_IA_Portugal-V2
cd Tribunal_IA_Portugal-V2

# 2. Ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# 3. Dependências
pip install -r requirements.txt

# 4. Configurar chave API
cp .env.example .env
# Editar .env com a sua OPENROUTER_API_KEY
```

## Uso

```bash
# Modo interativo completo (recomendado)
python main.py

# Processar ficheiro (sem fase interativa)
python main.py --file caso.txt

# Texto inline com instrução
python main.py --text "descrição do caso"

# Apenas anonimizar (testar RGPD)
python main.py -a --text "O arguido João Silva, NIF 123456789..."
```

---

## Fluxo do Sistema

```
Utilizador descreve o caso
        │
        ▼
┌──────────────────────┐
│  1. Anonimização     │  ← RGPD: NIF, telefone, nomes, moradas
│     (automática)     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  2. Juiz de Instrução│  ← IA analisa o caso e gera perguntas
│  faz perguntas       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  3. Utilizador       │  ← Responde, apresenta provas, salta
│  responde            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  4. Detetive         │  ← Integra respostas + analisa factos
│  (instrução factual) │
└──────────┬───────────┘
           │
        ┌──┴──┐
        ▼     ▼
   Acusação  Defesa
        └──┬──┘
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
Rigoroso Garantista Equilibrado
    └──────┼──────┘
           │
           ▼
┌──────────────────────┐
│  Ata Final           │  ← Inclui comparação das 3 sentenças
│  + Watermark         │
└──────────────────────┘
```

---

## Instâncias Judiciais Detectadas

| Tipo de Tribunal | Matéria |
|---|---|
| Tribunal Judicial de Comarca | Cível e penal geral |
| Tribunal de Instrução Criminal | Crimes mais graves |
| Tribunal Central de Instrução Criminal | Grande criminalidade |
| Tribunal do Trabalho | Relações laborais |
| Tribunal Administrativo | Atos administrativos |
| Tribunal de Família e Menores | Divórcio, menores |
| Tribunal de Comércio | Insolvência, empresas |

---

## Estrutura do Projeto

```
tribunal_ia/
├── main.py                      # Ponto de entrada
├── src/
│   ├── pipeline/
│   │   └── case_processor.py    # Orquestração + fase instrução
│   └── utils/
│       ├── anonymizer.py        # Anonimização RGPD
│       ├── brain.py             # Cliente API (retry + circuit breaker)
│       ├── config.py            # Configuração validada
│       └── logger.py            # Logging estruturado JSON
├── tests/
│   └── test_anonymizer.py
├── data/leis/                   # Leis e jurisprudência (local)
├── output_atas/                 # Atas geradas
├── .env.example
└── requirements.txt
```


---

## Configuração do Modelo

Edita o ficheiro `.env` e escolhe o modelo:

```
# Gratuito — funciona mas qualidade limitada nas sentenças
MODELO=openrouter/auto

# Recomendado — barato (~0.01€/caso) e boa qualidade
MODELO=claude-haiku-4-5-20251001

# Melhor qualidade
MODELO=claude-sonnet-4-6
```

O modelo `claude-haiku-4-5-20251001` é o ponto de equilíbrio ideal: segue as instruções correctamente, gera sentenças juridicamente estruturadas, e custa menos de 1 cêntimo por caso completo.

---

## Verificar se está tudo correcto

Antes de processar o primeiro caso, corre:

```bash
python verificar.py
```

Isto verifica: dependências instaladas, ficheiro `.env` presente, chave API válida, e modelo acessível. Se algo estiver errado, diz exactamente o quê e como corrigir.

---

## Resolução de Problemas

| Erro | Causa | Solução |
|---|---|---|
| `Circuit breaker aberto` | Muitas falhas de API seguidas | Espera 30s e tenta de novo; corre `python verificar.py` |
| `401 Unauthorized` | Chave API inválida | Verifica `OPENROUTER_API_KEY` no `.env` |
| `402 Payment Required` | Sem créditos | Adiciona créditos em openrouter.ai |
| `400 Bad Request` | Nome do modelo errado | Verifica `MODELO=` no `.env` |
| Sentenças são conselhos, não decisões | Modelo gratuito/fraco | Muda para `claude-haiku-4-5-20251001` |

---

## Aviso Legal

Este sistema é uma **simulação educativa**. As sentenças geradas são ficcionais e não têm qualquer valor jurídico. Para situações reais, consulte sempre um Advogado inscrito na Ordem dos Advogados de Portugal.
