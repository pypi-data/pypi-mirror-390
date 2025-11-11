
from typing import Self
import traceback

from .utils import SquareType, Piece, AnimalType


class RatPiece(Piece):
    def _animal_type(self) -> AnimalType:
        return AnimalType.RAT

    def _livable_in_square_types(self) -> set[SquareType]:
        return {SquareType.LAND, SquareType.TRAP0, SquareType.TRAP1, SquareType.WATER}

    def is_valid_move(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> bool:
        try:
            self._verify_position_move_within_range(initial_position, final_position)
        except ValueError:
            traceback.print_exc()
            return False
        try:
            self._verify_initial_positions_livable(initial_position)
        except ValueError:
            traceback.print_exc()
            return False

        destination_square_type = self._map.get_square_type(*final_position)
        if not (self.livable(destination_square_type) or destination_square_type in {SquareType.CAVE0,
                                                                                     SquareType.CAVE1}):
            return False

        if initial_position == final_position:
            return False

        if initial_position[0] == final_position[0]:
            return abs(initial_position[1] - final_position[1]) == 1
        elif initial_position[1] == final_position[1]:
            return abs(initial_position[0] - final_position[0]) == 1
        else:
            return False

    def can_eat(self, other: Self) -> bool:
        if (self.player is not other.player) and (other.animal_type == AnimalType.ELEPHANT):
            return True
        else:
            return super().can_eat(other)


class CatPiece(Piece):
    def _animal_type(self) -> AnimalType:
        return AnimalType.CAT

    def _livable_in_square_types(self) -> set[SquareType]:
        return {SquareType.LAND, SquareType.TRAP0, SquareType.TRAP1}

    def is_valid_move(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> bool:
        self._verify_position_move_within_range(initial_position, final_position)
        self._verify_initial_positions_livable(initial_position)

        destination_square_type = self._map.get_square_type(*final_position)
        if not (self.livable(destination_square_type) or destination_square_type in {SquareType.CAVE0, SquareType.CAVE1}):
            return False

        if initial_position == final_position:
            return False

        if initial_position[0] == final_position[0]:
            return abs(initial_position[1] - final_position[1]) == 1
        elif initial_position[1] == final_position[1]:
            return abs(initial_position[0] - final_position[0]) == 1
        else:
            return False


class DogPiece(Piece):
    def _animal_type(self) -> AnimalType:
        return AnimalType.DOG

    def _livable_in_square_types(self) -> set[SquareType]:
        return {SquareType.LAND, SquareType.TRAP0, SquareType.TRAP1}

    def is_valid_move(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> bool:
        self._verify_position_move_within_range(initial_position, final_position)
        self._verify_initial_positions_livable(initial_position)

        destination_square_type = self._map.get_square_type(*final_position)
        if not (self.livable(destination_square_type) or destination_square_type in {SquareType.CAVE0,
                                                                                     SquareType.CAVE1}):
            return False

        if initial_position == final_position:
            return False

        if initial_position[0] == final_position[0]:
            return abs(initial_position[1] - final_position[1]) == 1
        elif initial_position[1] == final_position[1]:
            return abs(initial_position[0] - final_position[0]) == 1
        else:
            return False


class WolfPiece(Piece):
    def _animal_type(self) -> AnimalType:
        return AnimalType.WOLF

    def _livable_in_square_types(self) -> set[SquareType]:
        return {SquareType.LAND, SquareType.TRAP0, SquareType.TRAP1}

    def is_valid_move(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> bool:
        self._verify_position_move_within_range(initial_position, final_position)
        self._verify_initial_positions_livable(initial_position)

        destination_square_type = self._map.get_square_type(*final_position)
        if not (self.livable(destination_square_type) or destination_square_type in {SquareType.CAVE0,
                                                                                     SquareType.CAVE1}):
            return False

        if initial_position == final_position:
            return False

        if initial_position[0] == final_position[0]:
            return abs(initial_position[1] - final_position[1]) == 1
        elif initial_position[1] == final_position[1]:
            return abs(initial_position[0] - final_position[0]) == 1
        else:
            return False


class LeopardPiece(Piece):
    def _animal_type(self) -> AnimalType:
        return AnimalType.LEOPARD

    def _livable_in_square_types(self) -> set[SquareType]:
        return {SquareType.LAND, SquareType.TRAP0, SquareType.TRAP1}

    def is_valid_move(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> bool:
        self._verify_position_move_within_range(initial_position, final_position)
        self._verify_initial_positions_livable(initial_position)

        destination_square_type = self._map.get_square_type(*final_position)
        if not (self.livable(destination_square_type) or destination_square_type in {SquareType.CAVE0,
                                                                                     SquareType.CAVE1}):
            return False

        if initial_position == final_position:
            return False

        if initial_position[0] == final_position[0]:
            return abs(initial_position[1] - final_position[1]) == 1
        elif initial_position[1] == final_position[1]:
            return abs(initial_position[0] - final_position[0]) == 1
        else:
            return False


river_jumping_movement_set = {
    ((3, 0), (3, 3)),
    ((4, 0), (4, 3)),
    ((5, 0), (5, 3)),
    ((3, 3), (3, 6)),
    ((4, 3), (4, 6)),
    ((5, 3), (5, 6)),
    ((3, 3), (3, 0)),
    ((4, 3), (4, 0)),
    ((5, 3), (5, 0)),
    ((3, 6), (3, 3)),
    ((4, 6), (4, 3)),
    ((5, 6), (5, 3)),
    ((2, 1), (6, 1)),
    ((2, 2), (6, 2)),
    ((2, 4), (6, 4)),
    ((2, 5), (6, 5)),
    ((6, 1), (2, 1)),
    ((6, 2), (2, 2)),
    ((6, 4), (2, 4)),
    ((6, 5), (2, 5))
}


class TigerPiece(Piece):
    def _animal_type(self) -> AnimalType:
        return AnimalType.TIGER

    def _livable_in_square_types(self) -> set[SquareType]:
        return {SquareType.LAND, SquareType.TRAP0, SquareType.TRAP1}

    def is_valid_move(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> bool:
        self._verify_position_move_within_range(initial_position, final_position)
        self._verify_initial_positions_livable(initial_position)

        destination_square_type = self._map.get_square_type(*final_position)
        if not (self.livable(destination_square_type) or destination_square_type in {SquareType.CAVE0,
                                                                                     SquareType.CAVE1}):
            return False

        if initial_position == final_position:
            return False

        if (initial_position, final_position) in river_jumping_movement_set: # consider river jumping
            return True
        elif initial_position[0] == final_position[0]:
            return abs(initial_position[1] - final_position[1]) == 1
        elif initial_position[1] == final_position[1]:
            return abs(initial_position[0] - final_position[0]) == 1
        else:
            return False


class LionPiece(Piece):
    def _animal_type(self) -> AnimalType:
        return AnimalType.LION

    def _livable_in_square_types(self) -> set[SquareType]:
        return {SquareType.LAND, SquareType.TRAP0, SquareType.TRAP1}

    def is_valid_move(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> bool:
        self._verify_position_move_within_range(initial_position, final_position)
        self._verify_initial_positions_livable(initial_position)

        destination_square_type = self._map.get_square_type(*final_position)
        if not (self.livable(destination_square_type) or destination_square_type in {SquareType.CAVE0,
                                                                                     SquareType.CAVE1}):
            return False

        if initial_position == final_position:
            return False

        if (initial_position, final_position) in river_jumping_movement_set: # consider river jumping
            return True
        elif initial_position[0] == final_position[0]:
            return abs(initial_position[1] - final_position[1]) == 1
        elif initial_position[1] == final_position[1]:
            return abs(initial_position[0] - final_position[0]) == 1
        else:
            return False


class ElephantPiece(Piece):
    def _animal_type(self) -> AnimalType:
        return AnimalType.ELEPHANT

    def _livable_in_square_types(self) -> set[SquareType]:
        return {SquareType.LAND, SquareType.TRAP0, SquareType.TRAP1}

    def is_valid_move(
            self,
            initial_position: tuple[int, int],
            final_position: tuple[int, int]
    ) -> bool:
        self._verify_position_move_within_range(initial_position, final_position)
        self._verify_initial_positions_livable(initial_position)

        destination_square_type = self._map.get_square_type(*final_position)
        if not (self.livable(destination_square_type) or destination_square_type in {SquareType.CAVE0,
                                                                                     SquareType.CAVE1}):
            return False

        if initial_position == final_position:
            return False

        if initial_position[0] == final_position[0]:
            return abs(initial_position[1] - final_position[1]) == 1
        elif initial_position[1] == final_position[1]:
            return abs(initial_position[0] - final_position[0]) == 1
        else:
            return False

    def can_eat(self, other: Self) -> bool:
        return (self.player is not other.player) and (other.animal_type != AnimalType.RAT)
