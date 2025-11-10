# Exemplos de APIs com banco de dados 

* **01_app_without_design_patterns**: exemplo de código que salva um item no banco de dados sem padrão. 
* **02_app_without_dto**: exemplo de código que salva um item no banco de dados, que utiliza o padrão DTO.
* **03_app_mvc**: exemplo de código que salva um item no banco de dados, usando o padrão MVC.
* **04_app_mvc_relation**: exemplo de código que salva um item com relacionamento no banco de dados, usando o padrão MVC.

## Explicando o código 03_APP_MVC

API de exemplo para gerenciar **Heróis** usando **FastAPI**, **SQLModel** (SQLAlchemy + Pydantic), e o padrão **MVC com Repository**:

* **Controller (Router)** → recebe HTTP
* **Service** → regras de negócio
* **Repository** → acesso ao banco
* **Model (SQLModel)** → entidades e DTOs
* **Database** → criação do engine e sessão

---

## ✨ Principais recursos

* Estrutura limpa em camadas (**Controller → Service → Repository → DB**)
* **SQLModel** (tipagem forte + ORM)
* Injeção de dependência com `Depends`
* Tratamento de erros HTTP padronizado
* Pronto para trocar **SQLite** por **PostgreSQL**

---

## 📂 Estrutura do projeto

```

├─ app/
│  ├─ main.py                  # inicialização da app e rotas
│  ├─ database.py              # engine, sessão e inicialização do schema
│  ├─ models.py                # SQLModel: entidades e schemas (Create/Update/Public)
│  ├─ controllers/
│  │  └─ heroes.py             # Controller (Router) da feature "heroes"
│  ├─ services/
│  │  └─ hero_service.py       # Regras de negócio
│  └─ repositories/
│     └─ hero_repository.py    # Acesso ao banco (CRUD)
└─ requirements.txt
```

---

## 🧰 Stack & Requisitos

* Python 3.10+
* FastAPI
* SQLModel
* Uvicorn

`requirements.txt`:

```
fastapi==0.114.2
uvicorn[standard]==0.30.6
SQLModel==0.0.22
```

> Para PostgreSQL, adicione também: `psycopg[binary]==3.*`

---

## ⚙️ Configuração & Execução

1. Crie o ambiente e instale dependências:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. (Opcional) Defina o banco via variável de ambiente:

* **SQLite (padrão)** – já funciona sem configurar nada.
* **PostgreSQL**:

  ```bash
  export DATABASE_URL="postgresql+psycopg://app:app@localhost:5432/appdb"
  ```

3. Rode a aplicação:

```bash
uvicorn app.main:app --reload
```

4. Acesse:

* Healthcheck: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧱 Modelos (resumo)

* `Hero` (tabela): `id`, `name`, `secret_name?`, `age?`
* `HeroCreate` (entrada POST)
* `HeroUpdate` (entrada PATCH, campos opcionais)
* `HeroPublic` (saída nas respostas)

---

## 🔌 Endpoints (Heroes)

Base path: `/heroes`

| Método | Rota         | Body         | Resposta           | Descrição                   |
| ------ | ------------ | ------------ | ------------------ | --------------------------- |
| POST   | `/`          | `HeroCreate` | `HeroPublic`       | Cria um herói               |
| GET    | `/`          | —            | `List[HeroPublic]` | Lista heróis (offset/limit) |
| GET    | `/{hero_id}` | —            | `HeroPublic`       | Busca por ID                |
| PATCH  | `/{hero_id}` | `HeroUpdate` | `HeroPublic`       | Atualiza campos parciais    |
| DELETE | `/{hero_id}` | —            | `204 No Content`   | Remove herói                |

---

## 🧪 Exemplos (cURL)

Criar:

```bash
curl -X POST http://127.0.0.1:8000/heroes/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada","secret_name":"The Enchantress","age":28}'
```

Listar:

```bash
curl "http://127.0.0.1:8000/heroes/?offset=0&limit=100"
```

Buscar por ID:

```bash
curl http://127.0.0.1:8000/heroes/1
```

Atualizar (parcial):

```bash
curl -X PATCH http://127.0.0.1:8000/heroes/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada Lovelace"}'
```

Remover:

```bash
curl -X DELETE http://127.0.0.1:8000/heroes/1 -i
```

---

## 🧠 Como as camadas se conectam

```
HTTP (FastAPI)
   ↓
Controller (app/controllers/heroes.py)
   ↓
Service (app/services/hero_service.py)
   ↓
Repository (app/repositories/hero_repository.py)
   ↓
DB Session (app/database.py) + SQLModel (app/models.py)
```

* **Controller**: lida com requisições/respostas e validações de query/path; injeta dependências com `Depends`.
* **Service**: regras de negócio (ex.: checar nome duplicado).
* **Repository**: SQL puro via SQLModel/SQLAlchemy (CRUD).
* **Database**: engine, sessão e criação de schema.

## Reference:
[Documento Fast API](https://fastapi.tiangolo.com/) : Documentação do FAST API. 