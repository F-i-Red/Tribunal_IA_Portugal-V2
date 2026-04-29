# Changelog — Tribunal IA Portugal

## v1.0.1 — Correção de Anonimização (Final)

### Problemas identificados no teste real
- ❌ Datas genéricas ("15 de março de 2024") eram detetadas como DATA_NASCIMENTO sem contexto
- ❌ Moradas não eram detetadas ("Rua das Flores nº 45, 3º Esq., 1200-150 Lisboa")
- ❌ Cidades isoladas ("Lisboa") não eram anonimizadas
- ❌ "Avenida da Liberdade" não era detetada como localização
- ❌ Falsos positivos: "foi visto por duas testemunhas" e "tem antecedentes criminais por furto" como PESSOA
- ❌ "912345678" (telemóvel) detetado como NIF em vez de TELEFONE
- ❌ "Maria Conceição Lopes" e "Pedro Miguel Ribeiro" não detetados como PESSOA
- ❌ Pseudónimos inconsistentes para o mesmo nome

### Correções aplicadas (v5)
- ✅ DATA_NASCIMENTO agora requer contexto explícito: "nascido em", "data de nascimento"
- ✅ Nova categoria MORADA para endereços completos (Rua, Avenida, etc.)
- ✅ Deteção de cidades conhecidas de Portugal (lista de 30+ cidades)
- ✅ Regex melhorada para tribunais
- ✅ CÓDIGO_POSTAL detetado separadamente
- ✅ Validação mais rigorosa de nomes:
  - Máximo 5 palavras
  - Rejeita numerais ("uma", "duas", "um", "dois")
  - Rejeita palavras estruturais no início ("foi", "tem", "visto")
  - Rejeita frases com verbos/preposições no meio
- ✅ TELEFONE detetado antes de NIF (ordem de prioridade corrige 912345678)
- ✅ Novo padrão ", e Nome" para listas de testemunhas
- ✅ Novo padrão ": Nome" para nomes após dois pontos
- ✅ Pseudónimos determinísticos por hash SHA-256

### Resultado do teste final
```
Input: Caso real com múltiplas entidades

Output (15 entidades corretamente anonimizadas):
  ✅ PESSOA: Manuel Ferreira Santos, Maria Conceição Lopes, Pedro Miguel Ribeiro, Ana Beatriz Costa
  ✅ MORADA: Rua das Flores, Avenida da Liberdade, Rua Augusta
  ✅ LOCAL: Lisboa (x2), Tribunal Judicial da Comarca de Lisboa
  ✅ NIF: 123456789
  ✅ EMAIL: ana.costa@advogados.pt
  ✅ TELEFONE: 912345678
  ✅ PROCESSO: 1234/23.0001
  ✅ CODIGO_POSTAL: 1200-150
  ❌ DATA_NASCIMENTO: 0 (correto — "15 de março de 2024" não é data de nascimento)
  ❌ Falsos positivos: 0
```

### Próximos passos
- Fase 2: RAG com vector store para validação de citações
