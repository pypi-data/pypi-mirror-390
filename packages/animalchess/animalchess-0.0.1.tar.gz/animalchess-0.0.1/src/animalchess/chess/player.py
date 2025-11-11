
from dataclasses import dataclass
from typing import Self


@dataclass
class Player:
    name: str

    def __eq__(self, other: Self) -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)
