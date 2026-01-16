"""Repository layer (data access).

This package centralizes common persistence operations to avoid duplicated
SQLAlchemy queries across routers/services.

Repositories are intentionally thin: they do not commit/rollback; transaction
boundaries are handled by the Unit of Work / dependencies.
"""
