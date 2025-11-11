
import unittest
from animalchess.chess.pieces import (
    RatPiece, CatPiece, DogPiece, LeopardPiece, 
    WolfPiece, TigerPiece, LionPiece, ElephantPiece
)
from animalchess.chess.utils import AnimalChessBoardMap, SquareType
from animalchess.chess.player import Player


class TestPieces(unittest.TestCase):
    def setUp(self):
        self.player = Player("Test Player")
        self.board_map = AnimalChessBoardMap()

    def test_rat_piece(self):
        rat = RatPiece(self.player)
        
        # Test animal type
        self.assertEqual(rat.animal_type.name, "RAT")
        
        # Test livable square types (includes water)
        self.assertTrue(rat.livable(SquareType.LAND))
        self.assertTrue(rat.livable(SquareType.TRAP0))
        self.assertTrue(rat.livable(SquareType.TRAP1))
        self.assertTrue(rat.livable(SquareType.WATER))  # Rat can live in water
        self.assertFalse(rat.livable(SquareType.CAVE0))
        
        # Test valid moves (one square in any direction)
        self.assertTrue(rat.is_valid_move((1, 1), (1, 2)))  # Right
        self.assertTrue(rat.is_valid_move((1, 1), (1, 0)))  # Left
        self.assertTrue(rat.is_valid_move((1, 1), (0, 1)))  # Up
        self.assertTrue(rat.is_valid_move((1, 1), (2, 1)))  # Down
        self.assertFalse(rat.is_valid_move((1, 1), (1, 3)))  # Too far
        self.assertFalse(rat.is_valid_move((1, 1), (2, 2)))  # Diagonal
        
        # Test can eat (rat can eat elephant)
        elephant = ElephantPiece(Player("Other Player"))
        self.assertTrue(rat.can_eat(elephant))

    def test_cat_piece(self):
        cat = CatPiece(self.player)
        
        # Test animal type
        self.assertEqual(cat.animal_type.name, "CAT")
        
        # Test livable square types (excludes water)
        self.assertTrue(cat.livable(SquareType.LAND))
        self.assertTrue(cat.livable(SquareType.TRAP0))
        self.assertTrue(cat.livable(SquareType.TRAP1))
        self.assertFalse(cat.livable(SquareType.WATER))
        self.assertFalse(cat.livable(SquareType.CAVE0))
        
        # Test valid moves (one square in any direction)
        self.assertTrue(cat.is_valid_move((1, 1), (1, 2)))  # Right
        self.assertTrue(cat.is_valid_move((1, 1), (1, 0)))  # Left
        self.assertTrue(cat.is_valid_move((1, 1), (0, 1)))  # Up
        self.assertTrue(cat.is_valid_move((1, 1), (2, 1)))  # Down
        self.assertFalse(cat.is_valid_move((1, 1), (1, 3)))  # Too far
        self.assertFalse(cat.is_valid_move((1, 1), (2, 2)))  # Diagonal

    def test_dog_piece(self):
        dog = DogPiece(self.player)
        
        # Test animal type
        self.assertEqual(dog.animal_type.name, "DOG")
        
        # Test valid moves (one square in any direction)
        self.assertTrue(dog.is_valid_move((1, 1), (1, 2)))  # Right
        self.assertTrue(dog.is_valid_move((1, 1), (1, 0)))  # Left
        self.assertTrue(dog.is_valid_move((1, 1), (0, 1)))  # Up
        self.assertTrue(dog.is_valid_move((1, 1), (2, 1)))  # Down
        self.assertFalse(dog.is_valid_move((1, 1), (1, 3)))  # Too far
        self.assertFalse(dog.is_valid_move((1, 1), (2, 2)))  # Diagonal

    def test_wolf_piece(self):
        wolf = WolfPiece(self.player)
        
        # Test animal type
        self.assertEqual(wolf.animal_type.name, "WOLF")
        
        # Test valid moves (one square in any direction)
        self.assertTrue(wolf.is_valid_move((1, 1), (1, 2)))  # Right
        self.assertTrue(wolf.is_valid_move((1, 1), (1, 0)))  # Left
        self.assertTrue(wolf.is_valid_move((1, 1), (0, 1)))  # Up
        self.assertTrue(wolf.is_valid_move((1, 1), (2, 1)))  # Down
        self.assertFalse(wolf.is_valid_move((1, 1), (1, 3)))  # Too far
        self.assertFalse(wolf.is_valid_move((1, 1), (2, 2)))  # Diagonal

    def test_leopard_piece(self):
        leopard = LeopardPiece(self.player)
        
        # Test animal type
        self.assertEqual(leopard.animal_type.name, "LEOPARD")
        
        # Test valid moves (one square in any direction)
        self.assertTrue(leopard.is_valid_move((1, 1), (1, 2)))  # Right
        self.assertTrue(leopard.is_valid_move((1, 1), (1, 0)))  # Left
        self.assertTrue(leopard.is_valid_move((1, 1), (0, 1)))  # Up
        self.assertTrue(leopard.is_valid_move((1, 1), (2, 1)))  # Down
        self.assertFalse(leopard.is_valid_move((1, 1), (1, 3)))  # Too far
        self.assertFalse(leopard.is_valid_move((1, 1), (2, 2)))  # Diagonal

    def test_tiger_piece(self):
        tiger = TigerPiece(self.player)
        
        # Test animal type
        self.assertEqual(tiger.animal_type.name, "TIGER")
        
        # Test valid moves (one square in any direction)
        self.assertTrue(tiger.is_valid_move((1, 1), (1, 2)))  # Right
        self.assertTrue(tiger.is_valid_move((1, 1), (1, 0)))  # Left
        self.assertTrue(tiger.is_valid_move((1, 1), (0, 1)))  # Up
        self.assertTrue(tiger.is_valid_move((1, 1), (2, 1)))  # Down
        self.assertFalse(tiger.is_valid_move((1, 1), (1, 3)))  # Too far
        self.assertFalse(tiger.is_valid_move((1, 1), (2, 2)))  # Diagonal
        
        # Test river jumping moves
        # Horizontal jumps
        self.assertTrue(tiger.is_valid_move((3, 0), (3, 3)))  # Jump right
        self.assertTrue(tiger.is_valid_move((3, 6), (3, 3)))  # Jump left
        self.assertTrue(tiger.is_valid_move((4, 0), (4, 3)))  # Jump right
        self.assertTrue(tiger.is_valid_move((4, 6), (4, 3)))  # Jump left
        self.assertTrue(tiger.is_valid_move((5, 0), (5, 3)))  # Jump right
        self.assertTrue(tiger.is_valid_move((5, 6), (5, 3)))  # Jump left
        
        # Vertical jumps
        self.assertTrue(tiger.is_valid_move((2, 1), (6, 1)))  # Jump down
        self.assertTrue(tiger.is_valid_move((6, 1), (2, 1)))  # Jump up
        self.assertTrue(tiger.is_valid_move((2, 2), (6, 2)))  # Jump down
        self.assertTrue(tiger.is_valid_move((6, 2), (2, 2)))  # Jump up
        self.assertTrue(tiger.is_valid_move((2, 4), (6, 4)))  # Jump down
        self.assertTrue(tiger.is_valid_move((6, 4), (2, 4)))  # Jump up
        self.assertTrue(tiger.is_valid_move((2, 5), (6, 5)))  # Jump down
        self.assertTrue(tiger.is_valid_move((6, 5), (2, 5)))  # Jump up

    def test_lion_piece(self):
        lion = LionPiece(self.player)
        
        # Test animal type
        self.assertEqual(lion.animal_type.name, "LION")
        
        # Test valid moves (one square in any direction)
        self.assertTrue(lion.is_valid_move((1, 1), (1, 2)))  # Right
        self.assertTrue(lion.is_valid_move((1, 1), (1, 0)))  # Left
        self.assertTrue(lion.is_valid_move((1, 1), (0, 1)))  # Up
        self.assertTrue(lion.is_valid_move((1, 1), (2, 1)))  # Down
        self.assertFalse(lion.is_valid_move((1, 1), (1, 3)))  # Too far
        self.assertFalse(lion.is_valid_move((1, 1), (2, 2)))  # Diagonal
        
        # Test river jumping moves (same as tiger)
        # Horizontal jumps
        self.assertTrue(lion.is_valid_move((3, 0), (3, 3)))  # Jump right
        self.assertTrue(lion.is_valid_move((3, 6), (3, 3)))  # Jump left
        self.assertTrue(lion.is_valid_move((4, 0), (4, 3)))  # Jump right
        self.assertTrue(lion.is_valid_move((4, 6), (4, 3)))  # Jump left
        self.assertTrue(lion.is_valid_move((5, 0), (5, 3)))  # Jump right
        self.assertTrue(lion.is_valid_move((5, 6), (5, 3)))  # Jump left
        
        # Vertical jumps
        self.assertTrue(lion.is_valid_move((2, 1), (6, 1)))  # Jump down
        self.assertTrue(lion.is_valid_move((6, 1), (2, 1)))  # Jump up
        self.assertTrue(lion.is_valid_move((2, 2), (6, 2)))  # Jump down
        self.assertTrue(lion.is_valid_move((6, 2), (2, 2)))  # Jump up
        self.assertTrue(lion.is_valid_move((2, 4), (6, 4)))  # Jump down
        self.assertTrue(lion.is_valid_move((6, 4), (2, 4)))  # Jump up
        self.assertTrue(lion.is_valid_move((2, 5), (6, 5)))  # Jump down
        self.assertTrue(lion.is_valid_move((6, 5), (2, 5)))  # Jump up

    def test_elephant_piece(self):
        elephant = ElephantPiece(self.player)
        
        # Test animal type
        self.assertEqual(elephant.animal_type.name, "ELEPHANT")
        
        # Test valid moves (one square in any direction)
        self.assertTrue(elephant.is_valid_move((1, 1), (1, 2)))  # Right
        self.assertTrue(elephant.is_valid_move((1, 1), (1, 0)))  # Left
        self.assertTrue(elephant.is_valid_move((1, 1), (0, 1)))  # Up
        self.assertTrue(elephant.is_valid_move((1, 1), (2, 1)))  # Down
        self.assertFalse(elephant.is_valid_move((1, 1), (1, 3)))  # Too far
        self.assertFalse(elephant.is_valid_move((1, 1), (2, 2)))  # Diagonal


if __name__ == '__main__':
    unittest.main()