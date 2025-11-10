# Lacrei Models

Pacote centralizado para os modelos de domínio (`models.py`) do ecossistema Lacrei.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 Objetivo

Centralizar todos os modelos do Django utilizados pelas aplicações Lacrei, permitindo:

- **Modularidade:** Desacoplar a camada de dados da lógica de aplicação.
- **Reuso:** Serviços diferentes podem consumir os mesmos modelos de forma consistente.
- **Governança e Consistência:** Ponto único de verdade para estrutura de dados.

É uma dependência interna, destinada a ser usada por aplicações como `lacrei-api`.

---

## ⚙️ Uso

Adicione como dependência usando Poetry:

```bash
poetry add lacrei-models
```

Importe os modelos no código:

```python
from lacrei_models.address.models import Address
from lacrei_models.lacreiid.models import User
from lacrei_models.appointments.models import Appointment
from lacrei_models.lacreisaude.models import Professional
from lacrei_models.notification.models import Notification
from lacrei_models.payment.models import Payment
from lacrei_models.sync.models import GoogleAccount
```

---

## 🛠️ Desenvolvimento

Clone o repositório e instale as dependências:

```bash
git clone git@github.com:Lacrei/lacrei-models.git
cd lacrei-models
make install
poetry shell
```

**Comandos principais:**

```bash
make test      # Rodar testes
make format    # Formatar código
make lint      # Verificar estilo e erros
make quality   # Rodar todas as verificações
```

---

## 🚀 Publicação

Atualize a versão no `pyproject.toml`, commit e tagueie:

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.2.6"
git tag v0.2.6
git push origin v0.2.6
make publish
```
