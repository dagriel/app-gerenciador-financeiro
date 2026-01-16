"""Domain ports (interfaces).

This package contains `Protocol` definitions that the application layer can depend on,
while infrastructure provides implementations (e.g., SQLAlchemy repositories).

The goal is to:
- keep use-cases/services free from SQLAlchemy imports and `Session` usage
- enable fast unit tests using fakes/in-memory repositories
"""
