from dataclasses import dataclass


@dataclass
class AuthContext:
    accessor_id: str
    access_token: str