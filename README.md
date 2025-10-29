# 2025.2-PI-Service

Serviço de comunicação entre interface e ESP, construído utilizando o framework FastAPI e um banco de dados PostgreSQL.

## Pré-requisitos

Antes de começar, garanta que você tenha as seguintes ferramentas instaladas:

- [Docker](https://www.docker.com/get-started) e [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.9+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)

## Execução com Docker

Este é o método recomendado para garantir um ambiente consistente.

### 1. Clonar o Repositório

```bash
git clone git@github.com:PI1-2025-FCTE/2025.2-PI-Service.git
cd 2025.2-PI-Service
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo `.env.sample` para criar seu próprio arquivo de configuração `.env`.

```bash
cp .env.sample .env
```

Após copiar, revise o arquivo `.env` e ajuste as variáveis se necessário. Para o Docker Compose, as configurações padrão geralmente funcionam sem alterações.

### 3. Construir e Iniciar os Containers

Execute o Docker Compose para construir as imagens e iniciar os serviços em background.

```bash
docker compose up --build -d
```

A aplicação estará disponível na porta definida pela variável `APP_PORT` (padrão: http://localhost:8000).

## Configuração para Desenvolvimento Local

Este método é alternativo ao Docker e requer que você gerencie o banco de dados e o ambiente Python manualmente.

### 1. Configurar o Banco de Dados

Garanta que você tenha um servidor PostgreSQL em execução localmente ou acessível pela rede.

### 2. Configurar Variáveis de Ambiente

Copie o arquivo `.env.sample` e edite o arquivo `.env` com as credenciais do seu banco de dados local.

**Importante:** Você deve alterar POSTGRES_HOST para localhost (ou o endereço do seu servidor de banco de dados).

### 3. Criar e Ativar o Ambiente Virtual (venv)

Recomenda-se usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar o ambiente virtual
python3 -m venv .venv

# Ativar o ambiente
# No Linux/macOS:
source .venv/bin/activate

# No Windows:
.venv\Scripts\activate
```

### 4. Instalar Dependências

Com o ambiente virtual ativado, instale os pacotes Python necessários:

```bash
pip install -r requirements.txt
```

### 5. Iniciar o Servidor

Inicie o servidor de desenvolvimento (geralmente com uvicorn):

```bash
uvicorn app.main:app --reload
```

## Variáveis de Ambiente (.env)

O arquivo `.env` controla a configuração da aplicação.

| Variável            | Descrição                                                          |
| ------------------- | ------------------------------------------------------------------ |
| `FRONTEND_URL`      | URL do cliente frontend (para CORS).                               |
| `APP_PORT`          | Porta em que a API FastAPI será executada.                         |
| `DB_EXPOSE_PORT`    | Porta que o host expõe para o banco de dados.                      |
| `POSTGRES_USER`     | Nome de usuário do banco de dados.                                 |
| `POSTGRES_PASSWORD` | Senha do banco de dados.                                           |
| `POSTGRES_DB`       | Nome do banco de dados.                                            |
| `POSTGRES_HOST`     | Host do banco de dados (`db` para Docker, `localhost` para local). |
| `POSTGRES_PORT`     | Porta interna do serviço de banco de dados.                        |

## Executando Testes

Para rodar a suíte de testes automatizados, utilize o pytest.

Rodando localmente:

```bash
pytest
```

Rodando dentro do container Docker:

```bash
docker compose exec api pytest
```

## Documentação da API

Após iniciar a aplicação, a documentação da API é gerada automaticamente e pode ser acessada nos seguintes endpoints:

Swagger UI (Interativo): http://localhost:8000/docs

ReDoc (Alternativo): http://localhost:8000/redoc
