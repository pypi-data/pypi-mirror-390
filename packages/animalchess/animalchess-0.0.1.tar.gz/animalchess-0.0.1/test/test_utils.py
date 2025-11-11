
import unittest
from animalchess.chess.utils import AnimalChessBoardMap, SquareType, Piece, AnimalType
from animalchess.chess.player import Player


class TestAnimalChessBoardMap(unittest.TestCase):
    def setUp(self):
        self.board_map = AnimalChessBoardMap()

    def test_singleton(self):
        board_map2 = AnimalChessBoardMap()
        self.assertIs(self.board_map, board_map2)

    def test_get_square_type(self):
        # Test land squares
        self.assertEqual(self.board_map.get_square_type(0, 0), SquareType.LAND)
        self.assertEqual(self.board_map.get_square_type(1, 1), SquareType.LAND)
        
        # Test water squares
        self.assertEqual(self.board_map.get_square_type(3, 1), SquareType.WATER)
        self.assertEqual(self.board_map.get_square_type(4, 2), SquareType.WATER)
        
        # Test trap squares
        self.assertEqual(self.board_map.get_square_type(0, 2), SquareType.TRAP0)
        self.assertEqual(self.board_map.get_square_type(8, 2), SquareType.TRAP1)
        
        # Test cave squares
        self.assertEqual(self.board_map.get_square_type(0, 3), SquareType.CAVE0)
        self.assertEqual(self.board_map.get_square_type(8, 3), SquareType.CAVE1)

    def test_invalid_square_position(self):
        with self.assertRaises(ValueError):
            self.board_map.get_square_type(-1, 0)
        with self.assertRaises(ValueError):
            self.board_map.get_square_type(0, -1)
        with self.assertRaises(ValueError):
            self.board_map.get_square_type(9, 0)
        with self.assertRaises(ValueError):
            self.board_map.get_square_type(0, 7)


class MockPiece(Piece):
    def _animal_type(self):
        return AnimalType.RAT
    
    def _livable_in_square_types(self):
        return {SquareType.LAND, SquareType.TRAP0, SquareType.TRAP1}
    
    def is_valid_move(self, initial_position, final_position):
        return True


class TestPiece(unittest.TestCase):
    def setUp(self):
        self.player1 = Player("Player 1")
        self.player2 = Player("Player 2")
        self.piece1 = MockPiece(self.player1)
        self.piece2 = MockPiece(self.player2)

    def test_animal_type(self):
        self.assertEqual(self.piece1.animal_type, AnimalType.RAT)

    def test_player(self):
        self.assertEqual(self.piece1.player, self.player1)

    def test_dead_property(self):
        self.assertFalse(self.piece1.dead)
        self.piece1.die()
        self.assertTrue(self.piece1.dead)

    def test_comparison_operators(self):
        # Create pieces with different animal types
        cat_piece = MockPiece(self.player1)
        cat_piece._animal_type = lambda: AnimalType.CAT
        
        dog_piece = MockPiece(self.player1)
        dog_piece._animal_type = lambda: AnimalType.DOG
        
        # Test equality
        self.assertTrue(self.piece1 == self.piece1)
        self.assertFalse(self.piece1 == cat_piece)
        
        # Test greater than
        self.assertTrue(cat_piece > self.piece1)
        self.assertTrue(dog_piece > cat_piece)
        
        # Test less than
        self.assertTrue(self.piece1 < cat_piece)
        self.assertTrue(cat_piece < dog_piece)
        
        # Test greater than or equal
        self.assertTrue(cat_piece >= self.piece1)
        self.assertTrue(cat_piece >= cat_piece)
        
        # Test less than or equal
        self.assertTrue(self.piece1 <= cat_piece)
        self.assertTrue(cat_piece <= cat_piece)

    def test_can_eat(self):
        # Same player pieces cannot eat each other
        piece1_copy = MockPiece(self.player1)
        self.assertFalse(self.piece1.can_eat(piece1_copy))
        
        # Different player, same rank - can eat
        piece2_copy = MockPiece(self.player2)
        piece2_copy._animal_type = lambda: AnimalType.RAT
        self.assertTrue(self.piece1.can_eat(piece2_copy))
        
        # Different player, higher rank - can eat
        cat_piece = MockPiece(self.player2)
        cat_piece._animal_type = lambda: AnimalType.CAT
        self.assertTrue(cat_piece.can_eat(self.piece1))
        
        # Different player, lower rank - cannot eat
        elephant_piece = MockPiece(self.player2)
        elephant_piece._animal_type = lambda: AnimalType.ELEPHANT
        self.assertFalse(self.piece1.can_eat(elephant_piece))

    def test_livable(self):
        self.assertTrue(self.piece1.livable(SquareType.LAND))
        self.assertTrue(self.piece1.livable(SquareType.TRAP0))
        self.assertTrue(self.piece1.livable(SquareType.TRAP1))
        self.assertFalse(self.piece1.livable(SquareType.WATER))  # Not in livable set
        self.assertFalse(self.piece1.livable(SquareType.CAVE0))  # Not in livable set

    def test_verify_position_move_within_range(self):
        # Valid positions
        self.piece1._verify_position_move_within_range((0, 0), (1, 1))
        
        # Invalid initial position
        with self.assertRaises(ValueError):
            self.piece1._verify_position_move_within_range((-1, 0), (1, 1))
        with self.assertRaises(ValueError):
            self.piece1._verify_position_move_within_range((0, -1), (1, 1))
        with self.assertRaises(ValueError):
            self.piece1._verify_position_move_within_range((9, 0), (1, 1))
        with self.assertRaises(ValueError):
            self.piece1._verify_position_move_within_range((0, 7), (1, 1))
            
        # Invalid final position
        with self.assertRaises(ValueError):
            self.piece1._verify_position_move_within_range((0, 0), (-1, 0))
        with self.assertRaises(ValueError):
            self.piece1._verify_position_move_within_range((0, 0), (0, -1))
        with self.assertRaises(ValueError):
            self.piece1._verify_position_move_within_range((0, 0), (9, 0))
        with self.assertRaises(ValueError):
            self.piece1._verify_position_move_within_range((0, 0), (0, 7))

    def test_verify_initial_positions_livable(self):
        board_map = AnimalChessBoardMap()
        
        # Valid initial position (land)
        self.piece1._verify_initial_positions_livable((0, 0))
        
        # Invalid initial position (water for this piece type)
        with self.assertRaises(ValueError):
            self.piece1._verify_initial_positions_livable((3, 1))


if __name__ == '__main__':
    unittest.main()