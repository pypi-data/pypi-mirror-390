
import unittest
from animalchess.chess.board import AnimalChessBoard, PlayerPossession
from animalchess.chess.player import Player
from animalchess.chess.utils import AnimalType, AnimalChessBoardMap, SquareType


class TestPlayerPossession(unittest.TestCase):
    def setUp(self):
        self.player = Player("Test Player")

    def test_initialize_pieces_player0(self):
        possession = PlayerPossession(self.player, 0)
        
        # Check that all pieces are initialized for player 0
        self.assertIsNotNone(possession.get_piece(AnimalType.LION).position)
        self.assertEqual(possession.get_piece(AnimalType.LION).position, (0, 0))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.TIGER).position)
        self.assertEqual(possession.get_piece(AnimalType.TIGER).position, (0, 6))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.DOG).position)
        self.assertEqual(possession.get_piece(AnimalType.DOG).position, (1, 1))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.CAT).position)
        self.assertEqual(possession.get_piece(AnimalType.CAT).position, (1, 5))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.RAT).position)
        self.assertEqual(possession.get_piece(AnimalType.RAT).position, (2, 0))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.LEOPARD).position)
        self.assertEqual(possession.get_piece(AnimalType.LEOPARD).position, (2, 2))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.WOLF).position)
        self.assertEqual(possession.get_piece(AnimalType.WOLF).position, (2, 4))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.ELEPHANT).position)
        self.assertEqual(possession.get_piece(AnimalType.ELEPHANT).position, (2, 6))

    def test_initialize_pieces_player1(self):
        possession = PlayerPossession(self.player, 1)
        
        # Check that all pieces are initialized for player 1
        self.assertIsNotNone(possession.get_piece(AnimalType.LION).position)
        self.assertEqual(possession.get_piece(AnimalType.LION).position, (8, 6))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.TIGER).position)
        self.assertEqual(possession.get_piece(AnimalType.TIGER).position, (8, 0))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.DOG).position)
        self.assertEqual(possession.get_piece(AnimalType.DOG).position, (7, 5))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.CAT).position)
        self.assertEqual(possession.get_piece(AnimalType.CAT).position, (7, 1))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.RAT).position)
        self.assertEqual(possession.get_piece(AnimalType.RAT).position, (6, 6))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.LEOPARD).position)
        self.assertEqual(possession.get_piece(AnimalType.LEOPARD).position, (6, 4))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.WOLF).position)
        self.assertEqual(possession.get_piece(AnimalType.WOLF).position, (6, 2))
        
        self.assertIsNotNone(possession.get_piece(AnimalType.ELEPHANT).position)
        self.assertEqual(possession.get_piece(AnimalType.ELEPHANT).position, (6, 0))

    def test_invalid_player_id(self):
        with self.assertRaises(ValueError):
            PlayerPossession(self.player, 2)

    def test_iterate_living_pieces(self):
        possession = PlayerPossession(self.player, 0)
        
        # Initially all pieces should be alive
        living_pieces = list(possession.iterate_living_pieces())
        self.assertEqual(len(living_pieces), 8)
        
        # Kill one piece and check
        rat_piece = possession.get_piece(AnimalType.RAT).piece
        rat_piece.die()
        
        living_pieces = list(possession.iterate_living_pieces())
        self.assertEqual(len(living_pieces), 7)


class TestAnimalChessBoard(unittest.TestCase):
    def setUp(self):
        self.player0 = Player("Player 0")
        self.player1 = Player("Player 1")
        self.board = AnimalChessBoard(self.player0, self.player1)

    def test_initialize_board(self):
        # Check that the board is initialized with pieces in correct positions
        board_array = self.board.get_board_array()
        
        # Player 0 pieces
        self.assertIn("Player 0", board_array[0, 0])  # Lion
        self.assertIn("Player 0", board_array[0, 6])  # Tiger
        self.assertIn("Player 0", board_array[2, 0])  # Rat
        
        # Player 1 pieces
        self.assertIn("Player 1", board_array[8, 6])  # Lion
        self.assertIn("Player 1", board_array[8, 0])  # Tiger
        self.assertIn("Player 1", board_array[6, 6])  # Rat

    def test_simple_move(self):
        # Move player 0's rat from (2, 0) to (2, 1)
        success = self.board.move_piece(0, AnimalType.RAT, (2, 1))
        self.assertTrue(success)
        
        # Verify the move
        board_array = self.board.get_board_array()
        self.assertEqual(board_array[2, 0], "")  # Original position empty
        self.assertIn("Player 0", board_array[2, 1])  # New position has rat

    def test_invalid_move_out_of_bounds(self):
        # Try to move rat to an invalid position
        success = self.board.move_piece(0, AnimalType.RAT, (-1, 0))
        self.assertFalse(success)
        
        success = self.board.move_piece(0, AnimalType.RAT, (2, -1))
        self.assertFalse(success)
        
        success = self.board.move_piece(0, AnimalType.RAT, (9, 0))
        self.assertFalse(success)
        
        success = self.board.move_piece(0, AnimalType.RAT, (2, 7))
        self.assertFalse(success)

    def test_invalid_move_too_far(self):
        # Try to move rat more than one square
        success = self.board.move_piece(0, AnimalType.RAT, (2, 2))
        self.assertFalse(success)

    def test_move_to_occupied_square_same_player(self):
        # Try to move rat to position occupied by another piece of same player
        # Player 0's rat is at (2, 0), try to move to (1, 1) where dog is
        success = self.board.move_piece(0, AnimalType.RAT, (1, 1))
        self.assertFalse(success)

    def test_basic_eating(self):
        # Create a custom board for eating tests
        player0_possession = PlayerPossession(self.player0, 0, reset=False)
        player1_possession = PlayerPossession(self.player1, 1, reset=False)
        player0_possession.set_piece_info(AnimalType.CAT, (2, 6))
        player1_possession.set_piece_info(AnimalType.RAT, (6, 6))
        board = AnimalChessBoard(
            self.player0,
            self.player1,
            initial_players_possessions=[player0_possession, player1_possession]
        )
        
        # Move player 0's cat to a position where it can eat player 1's rat
        # First, move player 1's rat away to make space
        moved = board.move_piece(1, AnimalType.RAT, (5, 6))  # Move rat from (6,6) to (5,6)
        self.assertTrue(moved)
        
        # Move player 0's cat to (3, 6)
        moved = board.move_piece(0, AnimalType.CAT, (3, 6))
        self.assertTrue(moved)
        
        # Move player 1's rat to (4, 6) so cat can eat it
        moved = board.move_piece(1, AnimalType.RAT, (4, 6))
        self.assertTrue(moved)
        
        # Now cat should be able to eat rat
        success = board.move_piece(0, AnimalType.CAT, (4, 6))
        self.assertTrue(success)
        
        # Verify rat is dead
        rat_piece_info = board._players_possessions[1].get_piece(AnimalType.RAT)
        self.assertTrue(rat_piece_info.piece.dead)
        self.assertIsNone(rat_piece_info.position)

    def test_rat_eating_elephant(self):
        # Create a custom board for rat eating elephant test
        player0_possession = PlayerPossession(self.player0, 0, reset=False)
        player1_possession = PlayerPossession(self.player1, 1, reset=False)
        player0_possession.set_piece_info(AnimalType.ELEPHANT, (2, 6))
        player1_possession.set_piece_info(AnimalType.RAT, (6, 6))
        board = AnimalChessBoard(
            self.player0,
            self.player1,
            initial_players_possessions=[player0_possession, player1_possession]
        )
        
        # Move player 0's elephant to (3, 6)
        moved = board.move_piece(0, AnimalType.ELEPHANT, (3, 6))
        self.assertTrue(moved)
        
        # Move player 1's rat to (5, 6)
        moved = board.move_piece(1, AnimalType.RAT, (5, 6))
        self.assertTrue(moved)

        # Move player 0's elephant to (4, 6)
        moved = board.move_piece(0, AnimalType.ELEPHANT, (4, 6))
        self.assertTrue(moved)
        
        # Rat should be able to eat elephant
        success = board.move_piece(1, AnimalType.RAT, (4, 6))
        self.assertTrue(success)
        
        # Verify elephant is dead
        elephant_piece_info = board._players_possessions[0].get_piece(AnimalType.ELEPHANT)
        self.assertTrue(elephant_piece_info.piece.dead)
        self.assertIsNone(elephant_piece_info.position)

    def test_elephant_cannot_eat_rat(self):
        # Create a custom board for elephant trying to eat rat
        player0_possession = PlayerPossession(self.player0, 0, reset=False)
        player1_possession = PlayerPossession(self.player1, 1, reset=False)
        player0_possession.set_piece_info(AnimalType.RAT, (2, 0))
        player1_possession.set_piece_info(AnimalType.ELEPHANT, (6, 0))
        board = AnimalChessBoard(
            self.player0,
            self.player1,
            initial_players_possessions=[player0_possession, player1_possession]
        )
        
        # Move player 0's rat to (3, 0)
        board.move_piece(0, AnimalType.RAT, (3, 0))
        
        # Move player 1's elephant to (5, 0)
        board.move_piece(1, AnimalType.ELEPHANT, (5, 0))

        # Move player 0's rat to (4, 0)
        board.move_piece(0, AnimalType.RAT, (4, 0))
        
        # Elephant should not be able to eat rat
        success = board.move_piece(1, AnimalType.ELEPHANT, (4, 0))
        self.assertFalse(success)

    def test_pieces_in_between(self):
        # Test that pieces cannot jump over other pieces in normal moves
        board = AnimalChessBoard(self.player0, self.player1)
        
        # Try to move player 0's tiger from (0, 6) to (0, 4) - should fail because cat is in between
        success = board.move_piece(0, AnimalType.TIGER, (0, 4))
        self.assertFalse(success)

    def test_river_jumping(self):
        # Test that tiger can jump over river (fail (blocked) and successful jump)
        player0_possession = PlayerPossession(self.player0, 0, reset=False)
        player1_possession = PlayerPossession(self.player1, 1, reset=False)
        player0_possession.set_piece_info(AnimalType.RAT, (2, 0))
        player1_possession.set_piece_info(AnimalType.TIGER, (6, 0))
        board = AnimalChessBoard(
            self.player0,
            self.player1,
            initial_players_possessions=[player0_possession, player1_possession]
        )
        
        # first step by player 0
        moved = board.move_piece(0, AnimalType.RAT, (3, 0))
        self.assertTrue(moved)
        
        # first step by player 1
        moved = board.move_piece(1, AnimalType.TIGER, (6, 1))
        self.assertTrue(moved)

        # second step by player 0
        moved = board.move_piece(0, AnimalType.RAT, (3, 1))
        self.assertTrue(moved)

        # attempted jump by player 1's tiger
        moved = board.move_piece(1, AnimalType.TIGER, (3, 1))
        self.assertFalse(moved)     # it should fail

        # second step by player 1
        moved = board.move_piece(1, AnimalType.TIGER, (6, 2))
        self.assertTrue(moved)

        # third step by player 0
        moved = board.move_piece(0, AnimalType.RAT, (4, 1))
        self.assertTrue(moved)

        # third step by player 1 (jump)
        success = board.move_piece(1, AnimalType.TIGER, (2, 2))
        self.assertTrue(success)

    def test_trap_protection(self):
        # Test that pieces in their own trap cannot be eaten
        player0_possession = PlayerPossession(self.player0, 0, reset=False)
        player1_possession = PlayerPossession(self.player1, 1, reset=False)
        player0_possession.set_piece_info(AnimalType.RAT, (0, 0))
        player1_possession.set_piece_info(AnimalType.CAT, (2, 2))
        board = AnimalChessBoard(
            self.player0,
            self.player1,
            initial_players_possessions=[player0_possession, player1_possession]
        )
        boardmap = AnimalChessBoardMap()

        # Player 0's first move
        moved = board.move_piece(0, AnimalType.RAT, (0, 1))
        self.assertTrue(moved)

        # Player 1's first move
        moved = board.move_piece(1, AnimalType.CAT, (1, 2))
        self.assertTrue(moved)

        # Player 0's second move, into the trap
        moved = board.move_piece(0, AnimalType.RAT, (0, 2))
        self.assertTrue(moved)
        self.assertEqual(
            boardmap.get_square_type(*player0_possession.get_piece(AnimalType.RAT).position),
            SquareType.TRAP0
        )

        # Player 1's attempted second move, trying to eat the rat but failing
        eaten = board.move_piece(1, AnimalType.CAT, (0, 2))
        self.assertFalse(player0_possession.get_piece(AnimalType.RAT).piece.dead)
        self.assertFalse(eaten)

    def test_trap_vulnerability(self):
        # Test that pieces in opponent's trap are vulnerable
        player0_possession = PlayerPossession(self.player0, 0, reset=False)
        player1_possession = PlayerPossession(self.player1, 1, reset=False)
        player0_possession.set_piece_info(AnimalType.RAT, (0, 0))
        player1_possession.set_piece_info(AnimalType.CAT, (2, 2))
        board = AnimalChessBoard(
            self.player0,
            self.player1,
            initial_players_possessions=[player0_possession, player1_possession]
        )
        boardmap = AnimalChessBoardMap()

        # Move player 1's cat
        moved = board.move_piece(1, AnimalType.CAT, (1, 2))
        self.assertTrue(moved)

        # Move player 0's rat
        moved = board.move_piece(0, AnimalType.RAT, (0, 1))
        self.assertTrue(moved)

        # Move Player 1's cat into the trap
        moved = board.move_piece(1, AnimalType.CAT, (0, 2))
        self.assertTrue(moved)
        self.assertEqual(
            boardmap.get_square_type(*player1_possession.get_piece(AnimalType.CAT).position),
            SquareType.TRAP0
        )

        # Move player 0's rat into the trap to eat the cat
        self.assertFalse(
            player0_possession.get_piece(AnimalType.RAT).piece.can_eat(
                player1_possession.get_piece(AnimalType.CAT).piece
            )
        )    # normally the rat cannot eat the cat
        eaten = board.move_piece(0, AnimalType.RAT, (0, 2))
        self.assertTrue(eaten)    # yet the rat eat the cat
        self.assertTrue(player1_possession.get_piece(AnimalType.CAT).piece.dead)   # the cat is head

    def test_player0_win_condition(self):
        player0_possession = PlayerPossession(self.player0, 0, reset=False)
        player1_possession = PlayerPossession(self.player1, 1, reset=False)
        player0_possession.set_piece_info(AnimalType.RAT, (8, 2))
        player1_possession.set_piece_info(AnimalType.CAT, (2, 2))
        board = AnimalChessBoard(
            self.player0,
            self.player1,
            initial_players_possessions=[player0_possession, player1_possession]
        )
        boardmap = AnimalChessBoardMap()

        # move the rat to the cave of player 1
        moved = board.move_piece(0, AnimalType.RAT, (8, 3))
        self.assertTrue(moved)
        self.assertEqual(
            boardmap.get_square_type(*player0_possession.get_piece(AnimalType.RAT).position),
            SquareType.CAVE1
        )

        # Player 0 should have won
        self.assertTrue(board._players_possessions[0].winned)

    def test_player1_win_condition(self):
        player0_possession = PlayerPossession(self.player0, 0, reset=False)
        player1_possession = PlayerPossession(self.player1, 1, reset=False)
        player0_possession.set_piece_info(AnimalType.RAT, (8, 2))
        player1_possession.set_piece_info(AnimalType.CAT, (1, 3))
        board = AnimalChessBoard(
            self.player0,
            self.player1,
            initial_players_possessions=[player0_possession, player1_possession]
        )
        boardmap = AnimalChessBoardMap()

        # move the cat to the cave of player 0
        moved = board.move_piece(1, AnimalType.CAT, (0, 3))
        self.assertTrue(moved)
        self.assertEqual(
            boardmap.get_square_type(*player1_possession.get_piece(AnimalType.CAT).position),
            SquareType.CAVE0
        )

        # Player 1 should have won
        self.assertTrue(board._players_possessions[1].winned)

    def test_move_dead_piece(self):
        # Test that dead pieces cannot be moved
        board = AnimalChessBoard(self.player0, self.player1)
        
        # Kill player 0's rat
        rat_piece_info = board._players_possessions[0].get_piece(AnimalType.RAT)
        rat_piece_info.piece.die()
        
        # Try to move the dead rat. should fail
        success = board.move_piece(0, AnimalType.RAT, (2, 1))
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()