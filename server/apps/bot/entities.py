from dataclasses import dataclass

__all__ = (
    'User',
)


@dataclass
class User:
    id: str
    username: str
    first_name: str = ''
    last_name: str = ''
    language_code: str = ''
