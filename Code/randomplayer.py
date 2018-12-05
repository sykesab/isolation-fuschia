"""
A random player selects moves randomly.

Last update: 25 NOV 2018
"""
import isolation
import random


class RandomPlayer(isolation.Player):
    """
    A random player selects moves at random
    """

    def __init__(self, name, token):
        """
        Initialize this player
        :param name: This player's name
        :param token: This player's token
        """
        super().__init__(name, token)

    def take_turn(self, board):
        """
        Make a move on the isolation board
        :param board: an Board object
        :return: Return a Move object
        """

        print("\n{} taking turn: ".format(self._name), end='')

        # Collect board state info to generate a move from
        space_id = board.token_location(self._token)
        neighbors = board.neighbor_tiles(space_id)
        print('possible moves:', neighbors)
        tiled_spaces = board.push_outable_square_ids()

        # Select a square to move to and a tile to push out.
        # Once a neighbor square is chosen to move to,
        # that square can no longer be pushed out, but
        # the square vacated might be able to be pushed out
        to_space_id = random.choice(list(neighbors))
        tiled_spaces.discard(to_space_id)
        # if space_id not in board.start_squares():
        #     tiled_spaces.add(space_id)
        tiled_spaces.add(space_id)
        print('possible push outs:', tiled_spaces)
        push_out_space_id = random.choice(list(tiled_spaces))

        # print('    Moving to', to_space_id, 'and pushing out', push_out_space_id)

        move = isolation.Move(to_space_id, push_out_space_id)
        print('   ', move)
        return move


if __name__ == '__main__':
    # Create a match
    isolation.Board.set_dimensions(6, 8)
    match = isolation.Match(RandomPlayer('Blue', isolation.Board.BLUE_TOKEN),
                            RandomPlayer('Red', isolation.Board.RED_TOKEN),
                            isolation.Board())
    match.start_play()

    # # Play 100 more matches
    # for i in range(100):
    #     match = isolation.Match(RandomPlayer('Blue', isolation.Board.BLUE_TOKEN),
    #                             RandomPlayer('Red', isolation.Board.RED_TOKEN))
    #     print(match.start_play())
    #     print('*' * 40)
