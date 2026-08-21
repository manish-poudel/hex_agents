from dataclasses import dataclass
from uuid import UUID


@dataclass
class AuthContext:
    id: UUID
    access_token: str


@dataclass
class RuntimeContext:
    auth_context: list[AuthContext]

    def get_auth_context(self, id: str) -> AuthContext:
        for auth in self.auth_context:
            if auth.id == id:
                return auth

        raise ValueError(f"No auth context found for integration {id}")
