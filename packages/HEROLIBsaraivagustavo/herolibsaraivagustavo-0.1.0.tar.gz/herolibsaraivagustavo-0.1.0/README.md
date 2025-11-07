# HEROLIBsaraivagustavo

![PyPI](https://img.shields.io/pypi/v/HEROLIBsaraivagustavo)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Biblioteca para gerenciamento de heróis e seus times, utilizando banco de dados com SQLModel.

## 📜 Descrição

`HEROLIBsaraivagustavo` é uma biblioteca Python que fornece uma arquitetura robusta de serviços (`Service`) e repositórios (`Repository`) para gerenciar entidades como Heróis e Times. Ela é construída com [SQLModel](https://sqlmodel.tiangolo.com/), o que permite fácil interação com o banco de dados e validação de dados em um só lugar.

Esta biblioteca foi projetada para ser facilmente integrada em qualquer aplicação Python, especialmente em APIs web (como FastAPI), fornecendo uma camada de lógica de negócios e acesso a dados limpa e reutilizável.

## ✨ Recursos

* **Modelos SQLModel:** Define modelos de banco de dados claros para `Hero` e `Team`.
* **Arquitetura em Camadas:** Separação clara de responsabilidades com:
    * **Models:** Modelos de tabela do banco de dados.
    * **DTOs:** Objetos de Transferência de Dados (`HeroCreate`, `TeamPublic`, etc.) para validação de entrada e saída.
    * **Repository:** Camada genérica de acesso a dados (CRUD) para interagir com o banco.
    * **Service:** Camada de lógica de negócios que utiliza os repositórios.
* **Gerenciamento de Sessão:** Utilitários para inicializar o banco de dados e gerenciar sessões.

## 📦 Instalação

Você pode instalar a biblioteca diretamente do PyPI:

```bash
pip install HEROLIBsaraivagustavo
```

A biblioteca requer `sqlmodel` e `typing_extensions`, que serão instalados automaticamente.

## 🚀 Uso Rápido (Quick Start)

Aqui está um exemplo básico de como usar a biblioteca para criar um herói.

```python
from sqlmodel import Session
from HeroLib.util.database import init_db, engine
from HeroLib.models.models import Hero
from HeroLib.models.dto import HeroCreate
from HeroLib.repository.repository import Repository
from HeroLib.service.service import Service

# 1. Inicialize o banco de dados (cria as tabelas)
init_db()

# 2. Instancie o Repositório e o Serviço para o modelo Hero
hero_repo = Repository(Hero)
hero_service = Service(hero_repo)

# 3. Crie os dados do novo herói usando o DTO
novo_heroi_data = HeroCreate(
    name="Saraiva",
    secret_name="gussmm",
    age=20
)

# 4. Use o serviço para criar o herói no banco
with Session(engine) as session:
    try:
        heroi_criado = hero_service.create(session, novo_heroi_data)
        
        print(f"Herói criado com sucesso!")
        print(f"ID: {heroi_criado.id}")
        print(f"Nome: {heroi_criado.name}")
        
        todos_os_herois = hero_service.list(session)
        print(f"\nTotal de heróis no banco: {len(todos_os_herois)}")
        print(todos_os_herois[0])

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
```

## 🧑‍💻 Autor

**Gustavo Saraiva Mariano**  
📧 Email: gsaraivam10@gmail.com  
💻 GitHub: [saraivagustavo](https://github.com/saraivagustavo)

## ⚖️ Licença

Este projeto é licenciado sob a Licença MIT.
