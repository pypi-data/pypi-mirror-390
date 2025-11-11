
from typing import Literal, Generator, Optional
from dataclasses import dataclass
from itertools import product
import warnings

import numpy as np
from loguru import logger

from .utils import Piece, AnimalType, AnimalChessBoardMap, SquareType
from .utils import BOARD_HEIGHT, BOARD_WIDTH
from .player import Player
from .pieces import RatPiece, CatPiece, DogPiece, LeopardPiece, WolfPiece, TigerPiece, LionPiece, ElephantPiece


@dataclass
class PieceInformation:
    piece: Piece
    position: Optional[tuple[int, int]]


class PlayerPossession:
    def __init__(self, player: Player, id: Literal[0, 1], reset: bool = True):
        self._player = player
        self._pieces = {}
        self._winned = False
        if reset:
            self.initialize_pieces(id)

    def initialize_pieces(self, id: Literal[0, 1]) -> None:
        if id == 0:
            self._pieces = {
                AnimalType.LION: PieceInformation(LionPiece(self.player), (0, 0)),
                AnimalType.TIGER: PieceInformation(TigerPiece(self.player), (0, 6)),
                AnimalType.DOG: PieceInformation(DogPiece(self.player), (1, 1)),
                AnimalType.CAT: PieceInformation(CatPiece(self.player), (1, 5)),
                AnimalType.RAT: PieceInformation(RatPiece(self.player), (2, 0)),
                AnimalType.LEOPARD: PieceInformation(LeopardPiece(self.player), (2, 2)),
                AnimalType.WOLF: PieceInformation(WolfPiece(self.player), (2, 4)),
                AnimalType.ELEPHANT: PieceInformation(ElephantPiece(self.player), (2, 6))
            }
        elif id == 1:
            self._pieces = {
                AnimalType.LION: PieceInformation(LionPiece(self.player), (8, 6)),
                AnimalType.TIGER: PieceInformation(TigerPiece(self.player), (8, 0)),
                AnimalType.DOG: PieceInformation(DogPiece(self.player), (7, 5)),
                AnimalType.CAT: PieceInformation(CatPiece(self.player), (7, 1)),
                AnimalType.RAT: PieceInformation(RatPiece(self.player), (6, 6)),
                AnimalType.LEOPARD: PieceInformation(LeopardPiece(self.player), (6, 4)),
                AnimalType.WOLF: PieceInformation(WolfPiece(self.player), (6, 2)),
                AnimalType.ELEPHANT: PieceInformation(ElephantPiece(self.player), (6, 0))
            }
        else:
            raise ValueError("Player ID must be 0 or 1!")

    def set_piece_info(self, animal_type: AnimalType, position: tuple[int, int]):
        match animal_type:
            case AnimalType.RAT:
                piece = RatPiece(self.player)
            case AnimalType.CAT:
                piece = CatPiece(self.player)
            case AnimalType.DOG:
                piece = DogPiece(self.player)
            case AnimalType.LEOPARD:
                piece = LeopardPiece(self.player)
            case AnimalType.WOLF:
                piece = WolfPiece(self.player)
            case AnimalType.TIGER:
                piece = TigerPiece(self.player)
            case AnimalType.LION:
                piece = LionPiece(self.player)
            case AnimalType.ELEPHANT:
                piece = ElephantPiece(self.player)
        self._pieces[animal_type] = PieceInformation(piece, position)

    def get_piece(self, animal: AnimalType) -> PieceInformation:
        return self._pieces[animal]

    def iterate_living_pieces(self) -> Generator[PieceInformation, None, None]:
        for animal_piece_info in self._pieces.values():
            if not animal_piece_info.piece.dead:
                yield animal_piece_info

    @property
    def player(self) -> Player:
        return self._player

    @property
    def winned(self) -> bool:
        return self._winned

    @winned.setter
    def winned(self, win: bool) -> None:
        self._winned = win


class AnimalChessBoard:
    def __init__(
            self,
            player0: Player,
            player1: Player,
            initial_players_possessions: Optional[list[PlayerPossession]] = None
    ):
        self._map = AnimalChessBoardMap()
        self._player0 = player0
        self._player1 = player1
        if initial_players_possessions is None:
            self._players_possessions = [
                PlayerPossession(self._player0, 0),
                PlayerPossession(self._player1, 1)
            ]
        else:
            assert len(initial_players_possessions) == 2
            self._players_possessions = initial_players_possessions
        self._initialize_board()

    def _initialize_board(self) -> None:
        self._board = np.empty((BOARD_HEIGHT, BOARD_WIDTH), dtype=object)
        for possession in self._players_possessions:
            for animal_piece_info in possession.iterate_living_pieces():
                self._board[*animal_piece_info.position] = animal_piece_info.piece

    def _any_pieces_in_between(
        self,
        initial_position: tuple[int, int],
        destination_position: tuple[int, int]
    ) -> bool:
        if initial_position[0] == destination_position[0]:
            x = initial_position[0]
            step = 1 if destination_position[1] > initial_position[1] else -1
            for y in range(initial_position[1]+step, destination_position[1], step):
                if self._board[x, y] is not None and isinstance(self._board[x, y], Piece):
                    return True
        elif initial_position[1] == destination_position[1]:
            y = initial_position[1]
            step = 1 if destination_position[1] > initial_position[1] else -1
            for x in range(initial_position[0]+step, destination_position[0], step):
                if self._board[x, y] is not None and isinstance(self._board[x, y], Piece):
                    return True
        else:
            warnings.warn("Cannot check as it is not horizontal or vertical.")
        return False

    def _simply_move(
            self,
            player_id: Literal[0, 1],
            animal: AnimalType,
            destination: tuple[int, int]
    ) -> None:
        piece_info = self._players_possessions[player_id].get_piece(animal)
        initial_position = piece_info.position
        self._board[*initial_position] = None
        piece_info.position = destination
        self._board[*destination] = piece_info.piece
                
    def move_piece(
            self,
            player_id: Literal[0, 1],
            animal: AnimalType,
            destination: tuple[int, int]
    ) -> bool:   # success: True; failed: False
        piece_info = self._players_possessions[player_id].get_piece(animal)
        piece = piece_info.piece
        if piece.dead:
            logger.info(f"Player {self._players_possessions[player_id].player.name}: {piece.animal_type.name} is dead")
            return False

        initial_position = piece_info.position
        if not piece.is_valid_move(initial_position, destination):
            logger.info("Not a valid move.")
            return False

        if self._any_pieces_in_between(initial_position, destination):
            logger.info("There are pieces in between.")
            return False

        if self._board[*destination] is not None and isinstance(self._board[*destination], Piece):
            destination_piece = self._board[*destination]
            destination_squaretype = self._map.get_square_type(*destination)

            if destination_squaretype == (SquareType.TRAP0 if player_id==0 else SquareType.TRAP1):
                if destination_piece.player is (self._player1 if player_id==0 else self._player0):
                    # can eat because the piece is in our own trap
                    logger.info(f"{piece.animal_type.name} is eating {destination_piece.animal_type.name} in a trap!")
                    destination_piece.die()
                    destination_piece_info = self._players_possessions[1 if player_id==0 else 0].get_piece(destination_piece.animal_type)
                    destination_piece_info.position = None

                    # simply move
                    self._simply_move(player_id, animal, destination)
                    return True
            elif piece.can_eat(destination_piece) and destination_squaretype not in {SquareType.TRAP0, SquareType.TRAP1}:
                # eat
                logger.info(f"{piece.animal_type.name} is eating {destination_piece.animal_type.name}!")
                destination_piece.die()
                destination_piece_info = self._players_possessions[1 if player_id==0 else 0].get_piece(destination_piece.animal_type)
                destination_piece_info.position = None

                # simply move
                self._simply_move(player_id, animal, destination)
                return True
            else:
                logger.info(f"{piece.animal_type.name} cannot eat {destination_piece.animal_type.name}!")
                return False

        # determine if this player wins
        if self._map.get_square_type(*destination) in {SquareType.CAVE0, SquareType.CAVE1}:
            if (player_id == 0 and self._map.get_square_type(*destination) == SquareType.CAVE1) or (player_id == 1 and self._map.get_square_type(*destination) == SquareType.CAVE0):
                logger.info(f"{self._players_possessions[player_id].player.name} has won!")
                self._players_possessions[player_id].winned = True

        # simple move
        self._simply_move(player_id, animal, destination)
        return True

    def get_board_array(self) -> np.ndarray:
        printboard = np.empty((BOARD_HEIGHT, BOARD_WIDTH), dtype=object)
        for i, j in product(range(BOARD_HEIGHT), range(BOARD_WIDTH)):
            if self._board[i, j] is not None:
                piece = self._board[i, j]
                printboard[i, j] = f"{piece.player.name}: {piece.animal_type.name}"
            else:
                printboard[i, j] = ""
        return printboard
