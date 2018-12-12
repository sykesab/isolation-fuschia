import isolation
import randomplayer
import random
import math
import copy



# class Node:
#     def __init__(self, is_max, value, children):
#         self.is_max = is_max
#         self.value = value
#         self.allchildren = children
#
#     def is_leaf(self):
#         return self.allchildren is None
#
#     def children(self):
#         return self.allchildren
#
#     def evaluate(self):
#         return self.value


class Node:
    def __init__(self, board, value, children, token, opponent, is_max=True):
        self._board = board
        self._is_max = is_max
        self._value = value
        self._children = children
        self._token = token
        self._opponent = opponent

    def is_leaf(self):
        if self._is_max:
            self_location = self._board.token_location(self._token)
            self_neighbor_tiles = self._board.neighbor_tiles(self_location)
            return len(self_neighbor_tiles) == 0
        else:
            opponent_location = self._board.token_location(self._opponent)
            opponent_neighbor_tiles = self._board.neighbor_tiles(opponent_location)
            return len(opponent_neighbor_tiles) == 0

    def is_loser(self):
        if self.is_leaf():
            return self._is_max

    def is_winner(self):
        if self.is_leaf():
            return not self._is_max

    def is_max(self):
        return self._is_max

    def children(self):
        moves = set()
        neighbors = self._board.neighbor_tiles(self._board.token_location(self._token))
        for possible_move in neighbors:
            for push_outable_square in self._board.push_outable_square_ids():
                moves.add(isolation.Move(possible_move, push_outable_square))

        for move in moves:
            child_board = copy.deepcopy(self._board)
            child_board.make_move(self._token, move)

            self._children.append(Node(child_board,
                                       self.evaluate(),
                                       self._children,
                                       self._opponent,
                                       self._token,
                                       not self._is_max))

        return self._children

    def evaluate(self):
        distance_to_middle, closest_mid = self.get_distance_to_middle(self._board)

        opponent_moves = self._board.neighbor_tiles(self._board.token_location(self._opponent))
        our_moves = self._board.neighbor_tiles(self._board.token_location(self._token))

        num_opponent_moves = len(opponent_moves)
        num_our_moves = len(our_moves)

        h_value = distance_to_middle + (num_opponent_moves - num_our_moves)
        return h_value


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

        #print("\n{} taking turn: ".format(self._name), end='')

        # h_value = self._h(board)
        #
        # Collect board state info to generate a move from
        #space_id = board.token_location(self._token)
        #neighbors = board.neighbor_tiles(space_id)
        #print('possible moves:', neighbors)
        #tiled_spaces = board.push_outable_square_ids()

        # Select a square to move to and a tile to push out.
        # Once a neighbor square is chosen to move to,
        # that square can no longer be pushed out, but
        # the square vacated might be able to be pushed out
        #to_space_id = random.choice(list(neighbors))

        #tiled_spaces.discard(to_space_id)
        # if space_id not in board.start_squares():
        #     tiled_spaces.add(space_id)
        #tiled_spaces.add(space_id)
        #print('possible push outs:', tiled_spaces)

        push_out_space_id = random.choice(list(tiled_spaces))

        # print('    Moving to', to_space_id, 'and pushing out', push_out_space_id)

        #score, move = self.minmax_alpha_beta(board, -math.inf, math.inf)
        #print('   ', move)
        return self.early_game_strategy(board)

    def choose_move(self, board):
        self_location = board.token_location(self._token)
        opponent_location = board.token_location(self._opponent)

        distance_to_middle, closest_middle = self.get_distance_to_middle(board)
        dir_x, dir_y = board.direction(self_location, closest_middle)


    def _h(self, board):
        distance_to_middle, closest_mid = self.get_distance_to_middle(board)

        opponent_moves = board.neighbor_tiles(board.token_location(self._opponent))
        our_moves = board.neighbor_tiles(board.token_location(self._token))

        num_opponent_moves = len(opponent_moves)
        num_our_moves = len(our_moves)

        h_value = distance_to_middle + (num_opponent_moves - num_our_moves)
        return h_value

    def get_distance_to_middle(self, board):
        middle_spaces = [19, 20, 27, 28]

        current_location = board.token_location(self._token)

        min_distance = board.distance_between(current_location, middle_spaces[0])
        closest_middle_space = middle_spaces[0]

        for mid in middle_spaces:
            distance_to_middle = board.distance_between(current_location, mid)
            if distance_to_middle < min_distance:
                closest_middle_space = mid
                min_distance = distance_to_middle
        return min_distance, closest_middle_space

    def early_game_strategy(self, board):
        # move towards the middle of the board
        # pop the tile 2 away from

        move_to_make = self.move_towards_middle_earlystrat(board)
        punch_out_tile = self.punch_out_early_strat(board)
        return isolation.Board.make_move(self._token, isolation.Move(move_to_make, punch_out_tile))

    def move_towards_middle_early_strat(self, board):
        min_distance_to_middle, closest_middle_space = self.get_distance_to_middle(board)
        dx, dy = min_distance_to_middle
        our_moves = board.neighbor_tiles(board.token_location(self._token))
        best_move = len(isolation.Board.neighbor_tiles(our_moves[0])) - dx + dy

        for move in our_moves:
            possible_move = len(isolation.Board.neighbor_tiles(move)) - dx + dy
            if possible_move > best_move:
                best_move = possible_move

        to_square_id = best_move
        return to_square_id

    def punch_out_early_strat(self, board):
        min_distance_to_middle, closest_middle_space = self.get_distance_to_middle(board)
        dx, dy = min_distance_to_middle
        opponent_moves = board.neighbor_tiles(board.token_location(self._opponent))
        best_move = len(isolation.Board.neighbor_tiles(opponent_moves[0])) - dx + dy

        for move in opponent_moves:
            possible_move = len(isolation.Board.neighbor_tiles(move)) - dx + dy
            if possible_move > best_move:
                best_move = possible_move

        to_square_id = best_move
        return to_square_id

    def minimax_alpha_beta(self, n, a, b, depth=0):
        best = None

        if n.is_leaf():
            return n.evaluate(), None
        elif n.is_max():
            for child_node in n.children():
                score, path = self.minimax_alpha_beta(child_node, a, b, depth + 1)
                if score >= b:
                    return score, None
                if score > a:
                    a = score
                    best = path
            return a, best
        else:
            for child_node in n.children():
                score, path = self.minimax_alpha_beta(child_node, a, b, depth + 1)
                if score <= a:
                    return score, None
                if score < b:
                    b = score
                    best = path
            return b, best


        # best = None
        #
        # if self.board_is_end_state(n):
        #     return self._h(n), None
        # elif self.is_max_node():
        #     neighbors = n.neighbor_tiles(n.token_location(self._token))
        #     for possible_move in neighbors:
        #         for push_outable_square in n.push_outable_square_ids():
        #             pushed_out_squares = n.pushed_out_square_ids()
        #             pushed_out_squares.add(push_outable_square)
        #
        #             child_board = isolation.Board()
        #             child_board.set_state(possible_move, n.token_location(self._opponent), pushed_out_squares)
        #             score, path = self.minmax_alpha_beta(child_board, a, b)
        #
        #             if score >= b:
        #                 return score, None
        #             elif score > a:
        #                 a = score
        #                 best = isolation.Move(possible_move, push_outable_square)
        #             return a, best
        # else:
        #     neighbors = n.neighbor_tiles(n.token_location(self._token))
        #     for possible_move in neighbors:
        #         for push_outable_square in n.push_outable_square_ids():
        #             pushed_out_squares = n.pushed_out_square_ids()
        #             pushed_out_squares.add(push_outable_square)
        #
        #             child_board = copy.deepcopy(n)
        #             child_board.make_move(self._token, isolation.Move(possible_move, push_outable_square))
        #             score, path = self.minmax_alpha_beta(child_board, a, b)
        #
        #             if score <= a:
        #                 return score, None
        #             elif score < b:
        #                 b = score
        #                 best = isolation.Move(possible_move, push_outable_square)
        #             return b, best

    def board_is_end_state(self, board):
        self_location = board.token_location(self._token)
        opponent_location = board.token_location(self._opponent)

        self_neighbor_tiles = board.neighbor_tiles(self_location)
        opponent_neighbor_tiles = board.neighbor_tiles(opponent_location)

        return len(self_neighbor_tiles) == 0 or len(opponent_neighbor_tiles) == 0

    def is_max_node(self):
        return self._token is isolation.Board.BLUE_TOKEN


if __name__ == '__main__':
    # Create a match
    isolation.Board.set_dimensions(6, 8)
    match = isolation.Match(FuchsiaPlayer('Blue', isolation.Board.BLUE_TOKEN),
                            randomplayer.RandomPlayer('Red', isolation.Board.RED_TOKEN),
                            isolation.Board())
    match.start_play()

    # # Play 100 more matches
    # for i in range(100):
    #     match = isolation.Match(RandomPlayer('Blue', isolation.Board.BLUE_TOKEN),
    #                             RandomPlayer('Red', isolation.Board.RED_TOKEN))
    #     print(match.start_play())
    #     print('*' * 40)

