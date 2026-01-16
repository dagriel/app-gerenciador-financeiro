"""Domain layer.

Este pacote é o início de uma separação mais clara entre:
- Domínio (regras/VOs/invariantes)
- Aplicação (services / use-cases)
- Infra (db/models/repositories)
- Interface (api/routers)

No momento, contém Value Objects/helpers (ex.: money, validators) e evolui
conforme o projeto cresce.
"""
