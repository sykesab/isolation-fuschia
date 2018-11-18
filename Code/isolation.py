"""
This module defines an Isolation game board class and an
abstract player class.

Add:
    Board.squares_in_radius(square_id, d) --> a set of square id's for squares a distance of d moves away (on ANY board)
    Board.distance(square_id1, square_id2) --> min number of moves to get from square 1 to square 2
    Board.direction(square_id1, square_id2) --> (delta x, delta y
"""
from dataclasses import dataclass
import math
import sys


@dataclass(frozen=True)
class Move:
    """
    A Move object represents a move on a board: a square
    for a token to move to and a square to punch out.
    """
    to_square_id: int
    pushout_square_id: int

    def __str__(self):
        return 'Move to {}, punch {}.'.format(self.to_square_id, self.pushout_square_id)


class IllegalMove(Exception):
    """
    An invalid move is attempted on a board
    """
    pass


class IllegalPushOut(Exception):
    """
    An invalid push out is attempted on a board
    """
    pass


class Board:
    """
    A Isolation game board is an M-by-N grid of squares.
    Each square is tiled or "pushed out."

    Use the class method set_dimensions() to establish the
    number of rows and columns in any Board instance.
    """

    # If the characters below cause a problem, use these
    # as an alternative
    # RED_TOKEN = 'R'
    # BLUE_TOKEN = 'B'
    # TILE = '#'
    # HOLE = ' '

    RED_TOKEN = '\u265F'
    BLUE_TOKEN = '\u2659'
    TILE = '_'  # '\u25a1'
    HOLE = '#'  # '\u25a0'

    M = None
    N = None
    NEIGHBOR_SETS = ()
    START_SPACE_IDS = {}

    @classmethod
    def set_dimensions(cls, m, n):
        """
        Construct the neighbor sets (NEIGHBOR_SETS) data structure for
        an M-by-N board.

        This class method must be invoked to set the dimensions before
        an instance is created.
        :return: None
        """
        cls.M = m
        cls.N = n

        # Determine where the tokens start. Note: no player may
        # punch a start square, but may move to one
        blue_start_square_id = (m // 2) * n
        red_start_square_id = ((m - 1) // 2) * n + (n - 1)
        cls.START_SPACE_IDS = (blue_start_square_id, red_start_square_id)

        # Create a structure that provides a lookup table for the
        # squares adjacent to a given square.
        # Squares on a board are numbered in row-major order.
        #
        # First, create a list of lists that give the neighbor square id's
        # for each square. This is done to pre-compute neighbor_tiles.
        neighbor_ids = [list() for i in range(m * n)]

        # Left id's
        for col in range(1, n):
            for row in range(m):
                neighbor_ids[row * n + col].append(row * n + col - 1)
        # Right id's
        for col in range(n - 1):
            for row in range(m):
                neighbor_ids[row * n + col].append(row * n + col + 1)
        # Top id's
        for col in range(n):
            for row in range(1, m):
                neighbor_ids[row * n + col].append(row * n + col - n)
        # Bottom id's
        for col in range(n):
            for row in range(m - 1):
                neighbor_ids[row * n + col].append(row * n + col + n)
        # Top-Left id's
        for col in range(1, n):
            for row in range(1, m):
                neighbor_ids[row * n + col].append(row * n + col - n - 1)
        # Top-Right id's
        for col in range(n - 1):
            for row in range(1, m):
                neighbor_ids[row * n + col].append(row * n + col - n + 1)
        # Bottom-Left id's
        for col in range(1, n):
            for row in range(m - 1):
                neighbor_ids[row * n + col].append(row * n + col + n - 1)
        # Bottom-Right id's
        for col in range(n - 1):
            for row in range(m - 1):
                neighbor_ids[row * n + col].append(row * n + col + n + 1)

        # Create a tuple of frozen sets such that the value at index i
        # provides the neighbor squares of square having ID i
        cls.NEIGHBOR_SETS = tuple(frozenset(lst) for lst in neighbor_ids)

        cls.BOUNDARY_SQUARE_IDS = frozenset(id for id in range(m * n)
                                            if id < n or id >= (m - 1) * n or
                                            id % n in (0, n - 1))

        cls.CORNER_SQUARE_IDS = frozenset((0, n - 1, (m - 1) * n, m * n - 1))

        # Compute the Chebyshev values
        cls.CHEBYSHEV = {}

        def compute_chebyshevs(id):
            """
            Compute the neighbors of id a Chebyshev distance of radius away
            :param id: a square id
            :return: a frozenset
            """
            cls.CHEBYSHEV[(id, 0)] = frozenset({id})
            cls.CHEBYSHEV[(id, 1)] = Board.NEIGHBOR_SETS[id]
            radius = 1
            while id < max(Board.M, Board.N) and cls.CHEBYSHEV[(id, radius)]:
                # Compute the squares at the next radius
                squares = cls.CHEBYSHEV[(id, radius)]
                surrounding_squares = set()
                for square_id in squares:
                    surrounding_squares.update(Board.NEIGHBOR_SETS[square_id])
                radius += 1
                for r in range(radius):
                    # print('surrounding_squares:', surrounding_squares)
                    # print('Removing', cls.CHEBYSHEV[(id, r)])
                    surrounding_squares.difference_update(cls.CHEBYSHEV[(id, r)])
                cls.CHEBYSHEV[(id, radius)] = frozenset(surrounding_squares)

        for square_id in range(cls.M * cls.N):
            compute_chebyshevs(square_id)

    def __init__(self):
        """
        Initialize a board
        """
        assert Board.M is not None, "Invoke Board.set_dimensions()"
        m = Board.M
        n = Board.N

        # Initialize board state
        self._moves = []
        self._start_squares = Board.START_SPACE_IDS
        self._tiled_squares = set(id for id in range(m * n))
        # self._tiled_squares = set(id for id in range(m * n) if id not in self._start_squares)
        self._untiled_squares = set()
        # Put the blue token on the left side of the board
        self._token_locations = {Board.RED_TOKEN: Board.START_SPACE_IDS[1],
                                 Board.BLUE_TOKEN: Board.START_SPACE_IDS[0]}

    def moves(self):
        """
        get the moves made so far
        :return: list of Move objects
        """
        return self._moves

    @classmethod
    def start_squares(cls):
        """
        Get the ids of the two squares that tokens start on--that is,
        squares that can be occupied, but not pushed out
        :return: a tuple containing two square ids
        """
        return cls.START_SPACE_IDS

    @classmethod
    def boundary_squares(cls):
        """
        Return a frozenset of boundary square IDs
        :return: a frozenset
        """
        return cls.BOUNDARY_SQUARE_IDS

    @classmethod
    def corner_squares(cls):
        """
        Get a set of corner square IDs
        :return: frozenset
        """
        return cls.CORNER_SQUARE_IDS

    @classmethod
    def squares_at_radius(cls, square_id, radius):
        """
        Get the square id's for squares a Chebyshev a given distance
        from a given square
        :param square_id: an int value in range(Board.M * Board.N)
        :param radius: an int value k where 0 <= k < max(Board.M, Board.N)
               that is the distance
        :return: a set of square IDs
        """
        return cls.CHEBYSHEV.get((square_id, radius), frozenset())

    @classmethod
    def direction(cls, square_id1, square_id2):
        """
        Return the direction of square_id2 from square_id1
        as a dy, dx pair
        :param square_id1: a square id
        :param square_id2: a square id
        :return: a tuple (dx, dy), where -N < dx < N and
                 -M < dy < M. A positive value of dx
                 indicates that square 2 is below square 2.
                 A positive value of dy indicates that square 2
                 is to the right of square 1.
        """
        dx = abs(square_id2 % cls.N - square_id1 % cls.N)
        dy = abs(square_id2 // cls.N - square_id1 // cls.N)

    @classmethod
    def distance_between(cls, square_id1, square_id2):
        """
        Get the Chebyshev distance from one square to another
        :param square_id1: a square id
        :param square_id2: a square id
        :return: a non-negative int
        """
        dx = abs(square_id1 % cls.N - square_id2 % cls.N)
        dy = abs(square_id1 // cls.N - square_id2 // cls.N)
        return min(dx, dy)

    def make_move(self, token, move):
        """
        Move the token and push out a tile
        :param token: One of BLUE_TOKEN or RED_TOKEN
        :param move: a Move instance
        :return: None
        :exception: IllegalMove, IllegalPushOut
        """
        token_square_id = self.token_location(token)
        to_square_id = move.to_square_id
        push_square_id = move.pushout_square_id

        # Check the move
        if to_square_id not in self.NEIGHBOR_SETS[token_square_id]:
            raise IllegalMove('Square {} is not a legal move from {}'.format(to_square_id,
                                                                             token_square_id))

        if to_square_id in self._untiled_squares:
            raise IllegalMove('Square {} is already pushed out'.format(to_square_id))

        if push_square_id in self._untiled_squares:
            raise IllegalPushOut('Square {} is already pushed out'.format(push_square_id))

        if push_square_id == to_square_id:
            raise IllegalPushOut('Square {} will be occupied'.format(push_square_id))

        if push_square_id in self._token_locations.values() and \
           push_square_id != token_square_id:
            raise IllegalPushOut('Square {} is occupied'.format(push_square_id))

        # if push_square_id in self._start_squares:
        #     raise IllegalPushOut('Square {} cannot be pushed out'.format(push_square_id))

        self._moves.append(move)

        # Move the token
        self._token_locations[token] = to_square_id

        # Push out a square
        self._tiled_squares.remove(push_square_id)
        self._untiled_squares.add(push_square_id)

    def token_location(self, token):
        """
        Return the square_id of a token's location
        :param token: a token in Board.TOKENS
        :return: a square_id
        """
        return self._token_locations[token]

    def is_pushed_out(self, square_id):
        """
        Return True if the square with square_id is pushed out,
        False if not
        :param square_id: a square id
        :return: Boolean value
        """
        return square_id in self._untiled_squares

    def neighbors(self, square_id):
        """
        Get all of the the neighbors of a square
        :param square_id: int square id
        :return: a frozenset containing ids of neighboring squares
        """
        return self.NEIGHBOR_SETS[square_id]

    def neighbor_tiles(self, square_id):
        """
        Return a set of id's of the up-to eight neighbor
        squares that are unoccupied squares that have a tile
        :param square_id: a number in range(m * n)
        :return: a set of square ids
        """
        return {id for id in Board.NEIGHBOR_SETS[square_id]
                if id in self._tiled_squares and id not in self._token_locations.values()}

    def tile_square_ids(self):
        """
        Return a set containing the ids of all squares with tiles, including
        those that are occupied, but not the start squares
        :return: a set of square IDs
        """
        return set(self._tiled_squares)

    def pushed_out_square_ids(self):
        """
        Return a set containing all of the ids of all spaces for which tiles
        have been pushed out
        :return: a set of square IDs
        """
        return set(self._untiled_squares)

    def push_outable_square_ids(self):
        """
        Return a set of the tiles that can be pushed out--
        that is, unoccupied, tiled squares
        :return: a set of square IDs
        """
        tiled = set(self._tiled_squares)
        tiled.discard(self._token_locations[Board.BLUE_TOKEN])
        tiled.discard(self._token_locations[Board.RED_TOKEN])
        return tiled

    def square_id_map(self):
        """
        Return a string that shows square ids on the board
        :return: str
        """
        # Compute the minimum width for square numbers
        id_width = math.ceil(math.log10(self.M * self.N))
        id_format = '{{:{:d}d}}'.format(id_width + 1)

        # This can be improved, but use brute force
        id_list = [id_format.format(id) for id in range(self.M * self.N)]
        return '\n'.join('|' + ''.join(id_list[i:i + self.N]) + '|' for i in range(0, self.M * self.N, self.N))

    def __str__(self):
        """
        :return: str
        """

        def symbol(square_id):
            if square_id == self._token_locations[Board.BLUE_TOKEN]:
                return Board.BLUE_TOKEN
            elif square_id == self._token_locations[Board.RED_TOKEN]:
                return Board.RED_TOKEN
            elif square_id in self._tiled_squares or square_id in self._start_squares:
                return Board.TILE
            else:
                assert square_id in self._untiled_squares, \
                    '{} not in {}'.format(square_id, self._untiled_squares)
                return Board.HOLE

        board = [symbol(id) for id in range(self.M * self.N)]
        return '\n'.join('|' + ''.join(board[i:i + self.N]) + '|' for i in range(0, self.M * self.N, self.N))


class Player:
    """
    This is an abstract class that represents a player
    """

    def __init__(self, name, token):
        """
        Initialize a player to participate in play
        as the token
        :param name: a string giving a player's name
        :param token: a token in Board.TOKENS
        """
        self._name = name
        self._token = token

    def name(self):
        """
        Get this player's name
        :return: str
        """
        return self._name

    def token(self):
        """
        Get this player's token
        :return: Board.RED_TOKEN or Board.BLUE_TOKEN
        """
        return self._token

    def take_turn(self, board):
        """
        Make a move on the Isolation board
        :param board: a Board object
        :return: a Move object
        """
        # Each subclass must implement this method
        raise NotImplementedError


class Match:
    """
    A match controls play of a game. It lets players know
    when their turn happens and makes sure a player does
    not take too long to take a turn.

    NOTE: The time limit enforcement is not yet available.
    """

    def __init__(self, blue_player, red_player):
        """
        Initialize a game with two players. The board has
        m rows and n columns. The Blue Player moves first.
        :param blue_player: a Player object
        :param red_player: a Player object

        """
        self._board = Board()

        self._blue_player = blue_player
        self._red_player = red_player

        self._winner = None

    def start_play(self):
        """
        Play the game until the game ends
        :return: winning player
        """
        try:
            print('Begin play!')
            print(self._board.square_id_map())
            print()
            player = self._blue_player
            player_square_id = self._board.token_location(player.token())
            while self._board.neighbor_tiles(player_square_id):
                print(self._board)

                # This player has a move
                move = player.take_turn(self._board)
                self._board.make_move(player.token(), move)

                # Next player
                player = self._red_player if player is self._blue_player else self._blue_player
                player_square_id = self._board.token_location(player.token())

                # print(self.script())

            # We have a winner!
            self ._winner = self._red_player if player is self._blue_player else self._blue_player
            print(self._board)
            moves = self._board.moves()
            print(len(moves), 'moves.')
            print('Congratulations,', self._winner.name())

            print(self.script())
        except Exception as e:
            print("OOPS!")
            print(self._board.square_id_map())
            print(self._board)
            print(e)
            print(self.script())
            sys.exit(1)

    def moves(self):
        """
        Return the moves made in this match
        :return: a list of Move objects
        """
        return list(self._board.moves())

    def script(self):
        """
        A string defining a list containing all moves so far
        :return: a string that when eval'd gives a list of Move objects
        """
        return '[\n    {}\n]'.format(',\n    '.join(repr(move) for move in self.moves()))

    def winner(self):
        """
        Return th match winner if the game is over
        :return: the player who won or None
        """
        return self._winner


def main():

    # TODO
    # This code needs some cleaning up!

    m, n = [int(s) for s in input("Enter m and n separated by a square: ").split()]
    Board.set_dimensions(m, n)
    board = Board()
    print(board)
    print('ID map:')
    print(board.square_id_map())
    print('Boundary squares:', board.boundary_squares())
    print('Corner squares:', board.corner_squares())

    print('Neighbors')
    for id, neighbors in enumerate(board.NEIGHBOR_SETS):
        print('{:3d}: {}'.format(id, neighbors))

    sq_id = Board.START_SPACE_IDS[0]
    move = Move(sq_id - n, sq_id)
    print(move)
    board.make_move(Board.BLUE_TOKEN, move)
    print(board)
    print()

    # Check some illegal moves
    try:
        # Move to self-occupied space
        move = Move(sq_id - n, 1)
        board.make_move(Board.BLUE_TOKEN, move)
        assert False
    except IllegalMove as e:
        print("Good!", e)
    try:
        # Move to opponent-occupied space
        move = Move(11, 1)
        board.make_move(Board.BLUE_TOKEN, move)
        assert False
    except IllegalMove as e:
        print("Good!", e)
    try:
        # Move to already-punched space
        move = Move(0, 1)
        board.make_move(Board.BLUE_TOKEN, move)
        assert False
    except IllegalMove as e:
        print("Good!", e)
    try:
        # Move to non-neighboring space
        move = Move(18, 1)
        board.make_move(Board.BLUE_TOKEN, move)
        assert False
    except IllegalMove as e:
        print("Good!", e)

    try:
        # Push out an already-pushed-out square
        print(board)
        move = Move(12, 0)
        board.make_move(Board.BLUE_TOKEN, move)
        assert False
    except IllegalPushOut as e:
        print("Good!", e)
    try:
        # Push out an occupied square
        move = Move(12, 11)
        board.make_move(Board.BLUE_TOKEN, move)
        assert False
    except IllegalPushOut as e:
        print("Good!", e)
    try:
        # Push out the square just moved TO
        move = Move(12, 12)
        board.make_move(Board.BLUE_TOKEN, move)
        assert False
    except IllegalPushOut as e:
        print("Good!", e)

    ref = Match(Player('Blue player', Board.BLUE_TOKEN),
                Player('Red player', Board.RED_TOKEN))


if __name__ == '__main__':
    main()
