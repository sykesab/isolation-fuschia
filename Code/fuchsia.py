import isolation
import randomplayer
import math
import copy
import itertools


class Node:
    def __init__(self, board, move, token, is_max=True):
        """

        :param board: a Board object
        :param move: a Move to be made by the opponent first to get to this node
        :param token: the Player token that is currently moving
        :param is_max: True if this row is a Max row
        """
        self._board = copy.deepcopy(board)
        self._token = token
        self._move = move
        self._is_max = is_max
        if token is isolation.Board.RED_TOKEN:
            self._opponent = isolation.Board.BLUE_TOKEN
        else:
            self._opponent = isolation.Board.RED_TOKEN

        if move:
            self._board.make_move(self._opponent, move)


        token = self._token # if is_max else self._opponent
        neighbors = self._board.neighbor_tiles(self._board.token_location(token))
        current_location = self._board.token_location(token)
        push_out_squares = self._board.push_outable_square_ids()
        push_out_squares.add(current_location)
        self._available = [isolation.Move(idm, idt) for idm, idt
                          in itertools.product(neighbors, push_out_squares) if idm != idt]


        # self._last_move = last_move
        self.allchildren = None

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

    def move(self):
        return self._move

    def children(self):
        if self.allchildren is None:
            # neighbors = self._board.neighbor_tiles(self._board.token_location(self._token))
            # current_location = self._board.token_location(self._token)
            # push_out_squares = self._board.push_outable_square_ids()
            # push_out_squares.add(current_location)
            # self._available = [isolation.Move(idm, idt) for idm, idt
            #                   in itertools.product(neighbors, push_out_squares) if idm != idt]

            self.allchildren = [
                Node(self._board,
                     selected_move,
                     self._opponent,
                     is_max=not self._is_max)
                for selected_move in self._available]

        return self.allchildren

    def evaluate(self):
        distance_to_middle, closest_middle_space = self._get_distance_to_middle(self._board)
        opponent_moves = self._board.neighbor_tiles(self._board.token_location(self._opponent))
        our_moves = self._board.neighbor_tiles(self._board.token_location(self._token))

        num_opponent_moves = len(opponent_moves)
        num_our_moves = len(our_moves)

        h_value = (num_our_moves - num_opponent_moves)# - distance_to_middle
        return h_value

    def _get_distance_to_middle(self, board):
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


    def __str__(self):
        return f'Node {self._is_max},\n{self._board.square_id_map()}\n\n{self._board}\n{self._token}, {self._opponent}\n' +\
               f'{self._move}\navailable:\n' + '\n'.join(str(move) for move in self._available)


class PlayerAgent(isolation.Player):

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

        print("\n{} taking turn: \n".format(self._name), end='')

        tiles_remaining = len(board.push_outable_square_ids())

        if tiles_remaining >= 15:
            return self.early_game_strategy(board)
        else:
            n = Node(board, None, self._token)

            score, best_node = self.minimax_alpha_beta(n, -math.inf, math.inf)

            # When minimax returns n, if n was the initial node passed in, then the NoneType error occurs
            # because there is no move to get to that node.
            #
            # It will return n when n is a leaf node or the depth has been reached.
            # The only time it will be None is if it is a leaf node.
            if best_node is None:
                return self.early_game_strategy(board)
            else:
                move = best_node.move()
                print(f'{self._name} {move}')
                return move

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

        move_to_make = self.move_towards_middle_early_strat(board)
        punch_out_tile = self.punch_out_early_strat(board, move_to_make)
        return isolation.Move(move_to_make, punch_out_tile)

    def move_towards_middle_early_strat(self, board):
        min_distance_to_middle, closest_middle_space = self.get_distance_to_middle(board)
        our_moves = list(board.neighbor_tiles(board.token_location(self._token)))
        opponent_moves = list(board.neighbor_tiles(board.token_location(self._opponent)))
        # x = our_moves[0]
        # possible_moves = isolation.Board.neighbor_tiles(x)
        best_moves = our_moves[0]
        best_move = len(board.neighbor_tiles(our_moves[0])) - len(opponent_moves)
        # best_move = 0

        for move in our_moves:
            distance_to_the_middle = board.distance_between(move, closest_middle_space)
            possible_move = len(board.neighbor_tiles(move)) - len(opponent_moves) - (.5 * distance_to_the_middle)

            if possible_move >= best_move:
                if move not in board.pushed_out_square_ids():
                    # if len(list_of_prev_moves) > 0 and move != list_of_prev_moves[-1]:
                    best_move = possible_move
                    best_moves = move

        return best_moves

    def punch_out_early_strat(self, board, move_to_tile):
        min_distance_to_middle, closest_middle_space = self.get_distance_to_middle(board)
        opponent_moves = list(board.neighbor_tiles(board.token_location(self._opponent)))
        our_moves = list(board.neighbor_tiles(board.token_location(self._token)))
        best_move = len(board.neighbor_tiles(opponent_moves[0])) - len(our_moves) + min_distance_to_middle
        punch_out = opponent_moves[0]

        for move in opponent_moves:
            possible_move = len(board.neighbor_tiles(move)) - len(our_moves) + min_distance_to_middle
            if possible_move >= best_move:
                if move != move_to_tile and not board.is_pushed_out(move):
                    best_move = possible_move
                    punch_out = move

        return punch_out

    def minimax_alpha_beta(self, n, a, b, depth=0):
        """
        Return a pair (best_score, best_node) where best_score is
        min or max and best_node is the node associated with that score
        :param n:
        :param a:
        :param b:
        :param depth:
        :return:
        """

        # print(' * ' * depth, f'a={a}, b={b}\n', n)
        best_node = n

        if n.is_leaf() or depth > 2:
            if n.move() is None:
                pass
            return n.evaluate(), n
        elif n.is_max():
            for child_node in n.children():
                score, path = self.minimax_alpha_beta(child_node, a, b, depth + 1)
                if score >= b:
                    return score, None   # Quit searching
                if score > a:
                    a = score
                    best_node = child_node

            if best_node.move() is None:
                pass
            return a, best_node
        else:
            for child_node in n.children():
                score, path = self.minimax_alpha_beta(child_node, a, b, depth + 1)
                if score <= a:
                    return score, None
                if score < b:
                    b = score
                    best_node = child_node

            if best_node.move() is None:
                pass
            return b, best_node

    def board_is_end_state(self, board):
        self_location = board.token_location(self._token)
        opponent_location = board.token_location(self._opponent)

        self_neighbor_tiles = board.neighbor_tiles(self_location)
        opponent_neighbor_tiles = board.neighbor_tiles(opponent_location)

        return len(self_neighbor_tiles) == 0 or len(opponent_neighbor_tiles) == 0

    def is_max_node(self):
        return self._token is isolation.Board.BLUE_TOKEN


if __name__ == '__main__':
    # # Create a match
    isolation.Board.set_dimensions(6, 8)
    board = isolation.Board()
    # board.set_state(16, 20, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,14, 15, 24, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45,46, 47])
    # board.set_state(13, 9, [0, 4, 5, 6, 8, 12, 18, 19, 21, 23, 24, 25, 26, 28, 30, 32, 33, 34, 35, 36, 41, 42, 43, 44])
    match = isolation.Match(PlayerAgent('Blue', isolation.Board.BLUE_TOKEN),
                            randomplayer.RandomPlayer('Red', isolation.Board.RED_TOKEN),
                            board)
    match.start_play()

    # # Play 100 more matches
    # for i in range(100):
    #     match = isolation.Match(PlayerAgent('Blue', isolation.Board.BLUE_TOKEN),
    #                             randomplayer.RandomPlayer('Red', isolation.Board.RED_TOKEN),
    #                             isolation.Board())
    #     print(match.start_play())
    #     print('*' * 40)
