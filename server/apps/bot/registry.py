from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from telegram.ext import Dispatcher

__all__ = (
    'Registry',
    'registry'
)


class Registry:
    def __init__(self):
        self.storage: List['Dispatcher'] = []
        self.cache: Dict[str, 'Dispatcher'] = {}

    def __iter__(self):
        for entry in self.storage:
            yield entry

    def get_descriptor(self, token: str):
        if token not in self.cache:
            self.cache[token] = next((x for x in self if x.bot.token == token), None)

            if self.cache[token] is None:
                del self.cache[token]
                return None

        return self.cache[token]

    def register(self, item: 'Dispatcher'):
        return self.add_entry(item)

    def add_entry(self, item: 'Dispatcher'):
        self.storage.append(item)

        return item


registry = Registry()
