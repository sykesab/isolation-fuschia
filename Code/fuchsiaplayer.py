import isolation
import random


class FuchsiaPlayer(isolation.Player):

    def __init__(self, name, token):
        """
        Initialize this player
        :param name: This player's name
        :param token: This player's token
        """
        super().__init__(name, token)
        if token is isolation.Board.RED_TOKEN:
            self._opponent = isolation.Board.BLUE_TOKEN
        else:
            self._opponent = isolation.Board.RED_TOKEN

    def take_turn(self, board):
        """
        Make a move on the isolation board
        :param board: an Board object
        :return: Return a Move object
        """

        print("\n{} taking turn: ".format(self._name), end='')

        h_value = self._h(board)

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

    def _h(self, board):
        distance_to_middle = self._get_distance_to_middle(board)

        opponent_moves = board.neighbor_tiles(board.token_location(self._opponent))
        our_moves = board.neighbor_tiles(board.token_location(self._token))

        num_opponent_moves = len(opponent_moves)
        num_our_moves = len(our_moves)

        h_value = distance_to_middle + (num_opponent_moves - num_our_moves)
        return h_value

    def _get_distance_to_middle(self, board):
        middle_spaces = [19, 20, 27, 28]

        current_location = board.token_location(self._token)

        min_distance = board.distance_between(current_location, middle_spaces[0])
        closest_middle_space = middle_spaces[0]
        distance_to_closest = 0

        for mid in middle_spaces:
            distance_to_middle = board.distance_between(current_location, mid)
            if distance_to_middle < min_distance:
                closest_middle_space = mid
                min_distance = distance_to_middle
        return min_distance


if __name__ == '__main__':
    # Create a match
    isolation.Board.set_dimensions(6, 8)
    match = isolation.Match(FuchsiaPlayer('Blue', isolation.Board.BLUE_TOKEN),
                            FuchsiaPlayer('Red', isolation.Board.RED_TOKEN))
    match.start_play()

    # # Play 100 more matches
    # for i in range(100):
    #     match = isolation.Match(RandomPlayer('Blue', isolation.Board.BLUE_TOKEN),
    #                             RandomPlayer('Red', isolation.Board.RED_TOKEN))
    #     print(match.start_play())
    #     print('*' * 40)

