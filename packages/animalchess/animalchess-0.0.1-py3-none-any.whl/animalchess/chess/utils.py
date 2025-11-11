
from abc import ABC, abstractmethod
from enum import Enum
from typing import Self
import warnings

import numpy as np
from loguru import logger

from .player import Player


BOARD_WIDTH = 7
BOARD_HEIGHT = 9


class AnimalType(Enum):   # specify the food chain
    RAT = 1
    CAT = 2
    DOG = 3
    WOLF = 4
    LEOPARD = 5
    TIGER = 6
    LION = 7
    ELEPHANT = 8


class SquareType(Enum):
    LAND = 1
    WATER = 2
    TRAP0 = 3
    TRAP1 = 4
    CAVE0 = 5
    CAVE1 = 6


class AnimalChessBoardMap:    # this is a singleton
    def __init__(self):
        self._board = np.empty((BOARD_HEIGHT, BOARD_WIDTH), dtype=np.int8)
        self._board.fill(SquareType.LAND.value)
        self._board[0, 2] = SquareType.TRAP0.value
        self._board[0, 3] = SquareType.CAVE0.value
        self._board[0, 4] = SquareType.TRAP0.value
        self._board[1, 3] = SquareType.TRAP0.value
        self._board[8, 2] = SquareType.TRAP1.value
        self._board[8, 3] = SquareType.CAVE1.value
        self._board[8, 4] = SquareType.TRAP1.value
        self._board[7, 3] = SquareType.TRAP1.value
        for col in [1, 2, 4, 5]:
            for row in range(3, 6):
                self._board[row, col] = SquareType.WATER.value

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            logger.info("Creating new AnimalChessBoardMap instance")
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_square_type(self, row: int, col: int) -> SquareType:
        if row < 0 or row >= BOARD_HEIGHT or col < 0 or col >= BOARD_WIDTH:
            raise ValueError("Invalid square position")
        return SquareType(self._board[row, col])


class Piece(ABC):
    def __init__(self, player: Player):
        self._player = player
        self._dead = False
        self._map = AnimalChessBoardMap()

    def _verify_position_move_within_range(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> None:
        if initial_position[0] < 0 or initial_position[0] >= BOARD_HEIGHT or initial_position[1] < 0 or initial_position[1] >= BOARD_WIDTH:
            raise ValueError("Invalid initial position")
        if final_position[0] < 0 or final_position[0] >= BOARD_HEIGHT or final_position[1] < 0 or final_position[1] >= BOARD_WIDTH:
            raise ValueError("Invalid final position")

    def _verify_initial_positions_livable(
            self,
            initial_position: tuple[int, int]
    ) -> None:
        try:
            assert self.livable(self._map.get_square_type(*initial_position))
        except AssertionError:
            livable_squares_string = ", ".join(
                [animal_type.name for animal_type in self._livable_in_square_types()]
            )
            warnings.warn(f"The initial position must be {livable_squares_string}.")
            raise ValueError("The initial position is not livable.")

    @abstractmethod
    def is_valid_move(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> bool:   # does not account if the final position has another animal piece
        raise NotImplemented()

    @abstractmethod
    def _animal_type(self) -> AnimalType:
        raise NotImplemented()

    @property
    def animal_type(self) -> AnimalType:
        return self._animal_type()

    @abstractmethod
    def _livable_in_square_types(self) -> set[SquareType]:
        raise NotImplemented()    # must not include AnimalType.CAVE

    def livable(self, square_type: SquareType) -> bool:
        return square_type in self._livable_in_square_types()

    def __gt__(self, other: Self) -> bool:
        return self.animal_type.value > other.animal_type.value

    def __lt__(self, other: Self) -> bool:
        return self.animal_type.value < other.animal_type.value

    def __eq__(self, other: Self) -> bool:
        return self.animal_type.value == other.animal_type.value

    def __ge__(self, other: Self) -> bool:
        return (self > other) or (self == other)

    def __le__(self, other: Self) -> bool:
        return (self < other) or (self == other)

    def can_eat(self, other: Self) -> bool:
        return (self.player is not other.player) and (self >= other)       # rule needed to be overriden for rat and elephant

    def die(self):
        self._dead = True

    @property
    def player(self) -> Player:
        return self._player

    @property
    def dead(self) -> bool:
        return self._dead



