from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuthContext:
    id: str
    access_token: str


@dataclass
class RuntimeContext:
    auth_context: list[AuthContext]
    cache: dict[str, Any] = field(default_factory=dict)

    def get_auth_context(self, id: str) -> AuthContext:
        for auth in self.auth_context:
            if auth.id == id:
                return auth

        raise ValueError(f"No auth context found for integration '{id}'")

    def get_cache(self, key: str) -> Any:
        return self.cache.get(key)

    def set_cache(self, key: str, value: Any) -> None:
        self.cache[key] = value

    def clear_cache(self, key: str | None = None) -> None:
        if key is None:
            self.cache.clear()
        else:
            self.cache.pop(key, None)
