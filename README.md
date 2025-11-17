# 🎮 Pokemon Data Agent

Um assistente inteligente especializado em Pokémon, construído com OpenAI e FastAPI. Consulte dados de 251 Pokémon das gerações 1 e 2, compare estatísticas, monte times estratégicos e explore cadeias evolutivas.

## ✨ Funcionalidades

- 🤖 **Agente Conversacional**: Converse naturalmente sobre Pokémon em português
- 📊 **Consultas SQL Inteligentes**: Acesse um banco de dados completo com informações detalhadas
- ⚔️ **Comparação de Pokémon**: Compare estatísticas entre diferentes Pokémon
- 🎯 **Montagem de Times**: Sugestões estratégicas com análise de cobertura de tipos
- 🔄 **Cadeias Evolutivas**: Explore todas as evoluções e seus métodos
- 🌐 **API REST**: Endpoints prontos para integração

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.10+
- Chave de API da OpenAI

### Instalação

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd pokemon-data-agent
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite .env e adicione sua chave da OpenAI
OPENAI_API_KEY=sua-chave-aqui
```

5. Execute a ingestão de dados (primeira vez):
```bash
python -m app.ingest --limit 251
```

Isso baixará dados de 251 Pokémon da PokéAPI (leva ~5-10 minutos).

### Executar o Servidor

```bash
# Servidor principal (porta 7777)
python pokemon_os.py

# Ou usando uvicorn
uvicorn pokemon_os:app --reload --port 7777
```

Acesse a documentação interativa em: http://localhost:7777/docs

## 📖 Como Usar

### API REST

#### Criar uma sessão de chat

```bash
curl -X POST "http://localhost:7777/v1/agents/pokemon_expert/sessions" \
  -H "Content-Type: application/json" \
  -d '{"message": "Quem é mais rápido, Pikachu ou Raichu?"}'
```

#### Continuar uma conversa

```bash
curl -X POST "http://localhost:7777/v1/agents/pokemon_expert/sessions/{session_id}" \
  -H "Content-Type: application/json" \
  -d '{"message": "E qual tem mais ataque?"}'
```

### Exemplos de Perguntas

```
"Quem é mais rápido, Jolteon ou Aerodactyl?"
"Mostre-me a cadeia evolutiva do Eevee"
"Monte uma equipe equilibrada da primeira geração"
"Qual Pokémon tem a maior defesa?"
"Compare Charizard e Blastoise"
"Sugira um time ofensivo"
"Quais são os Pokémon do tipo dragão?"
```

## 🛠️ Ferramentas Disponíveis

O agente possui acesso a 5 ferramentas especializadas:

1. **query_pokemon_database**: Consultas SQL complexas no banco de dados
2. **compare_two_pokemon**: Comparação detalhada entre dois Pokémon
3. **suggest_pokemon_team**: Sugestão de times com análise estratégica
4. **get_evolution_chain**: Informações sobre cadeias evolutivas
5. **analyze_type_coverage**: Análise de fraquezas e resistências de tipos

## 📁 Estrutura do Projeto

```
pokemon-data-agent/
├── app/
│   ├── agent.py          # Lógica do agente (Agno SDK)
│   ├── api.py            # API alternativa
│   ├── db.py             # Gerenciamento do banco de dados
│   ├── ingest.py         # Ingestão de dados da PokéAPI
│   ├── schemas.sql       # Schema do banco de dados
│   └── tools/            # Ferramentas do agente
│       ├── sql_tool.py
│       ├── compare.py
│       ├── team.py
│       └── evolution.py
├── cache/                # Cache de respostas da API
├── tests/                # Testes automatizados
├── pokemon_os.py         # Servidor principal (OpenAI)
├── requirements.txt      # Dependências Python
├── setup.py              # Script de setup automatizado
└── Makefile              # Comandos úteis
```

## 🧪 Testes

Execute os testes automatizados:

```bash
pytest tests/ -v
```

## 📊 Banco de Dados

O projeto usa SQLite com as seguintes tabelas:

- **pokemon**: Informações básicas (id, nome, altura, peso)
- **species**: Dados da espécie (geração, cor, habitat)
- **pokemon_type**: Tipos de cada Pokémon
- **pokemon_stat**: Estatísticas base (HP, Attack, Defense, etc.)
- **evolution_chain**: Cadeias evolutivas completas

## 🔧 Comandos Make

```bash
make install    # Instalar dependências
make ingest     # Ingerir dados da PokéAPI
make run        # Iniciar servidor
make test       # Executar testes
make clean      # Limpar cache e banco de dados
```

## 🌐 Endpoints da API

### Principais

- `GET /health` - Verificação de saúde
- `GET /config` - Configuração do agente
- `POST /v1/agents/pokemon_expert/sessions` - Criar sessão
- `GET /v1/agents/pokemon_expert/sessions` - Listar sessões
- `GET /v1/agents/pokemon_expert/sessions/{id}` - Obter sessão
- `DELETE /v1/agents/pokemon_expert/sessions/{id}` - Deletar sessão

Documentação completa: http://localhost:7777/docs

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

## 📝 Licença

Este projeto é open source e está disponível sob a licença MIT.

## 🙏 Agradecimentos

- [PokéAPI](https://pokeapi.co/) - Fonte de dados dos Pokémon
- [OpenAI](https://openai.com/) - Modelo de linguagem GPT-4
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Agno](https://github.com/agno-agi/agno) - SDK para agentes



