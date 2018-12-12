import isolation
import randomplayer
import random
import math
import copy
import itertools


class Node:
    def __init__(self, board, token, available, is_max=True, last_move=None):
        self._board = board
        self._token = token

        if token is isolation.Board.RED_TOKEN:
            self._opponent = isolation.Board.BLUE_TOKEN
        else:
            self._opponent = isolation.Board.RED_TOKEN

        self._available = available
        self._is_max = is_max
        self._last_move = last_move
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

    def children(self):
        if self.allchildren is None:
            #neighbors = self._board.neighbor_tiles(self._board.token_location(self._token))
            #current_location = self._board.token_location(self._token)
            #push_out_squares = self._board.push_outable_square_ids()
            #push_out_squares.add(current_location)
            #self._available = [isolation.Move(idm, idt) for idm, idt
            #                   in itertools.product(neighbors, push_out_squares) if idm != idt]

            self.allchildren = [
                Node(self._board,
                     self._opponent,
                     [e for e in self._available if e is not selected_move],
                     is_max=not self._is_max,
                     last_move=selected_move)
                for selected_move in self._available]

        return self.allchildren

    def evaluate(self):
        distance_to_middle, closest_mid = self._get_distance_to_middle(self._board)

        opponent_moves = self._board.neighbor_tiles(self._board.token_location(self._opponent))
        our_moves = self._board.neighbor_tiles(self._board.token_location(self._token))

        num_opponent_moves = len(opponent_moves)
        num_our_moves = len(our_moves)

        h_value = distance_to_middle + (num_opponent_moves - num_our_moves)
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

        print("\n{} taking turn: \n".format(self._name), end='')

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

        #push_out_space_id = random.choice(list(tiled_spaces))

        # print('    Moving to', to_space_id, 'and pushing out', push_out_space_id)

        neighbors = board.neighbor_tiles(board.token_location(self._token))
        current_location = board.token_location(self._token)
        push_out_squares = board.push_outable_square_ids()
        push_out_squares.add(current_location)
        available = [isolation.Move(idm, idt) for idm, idt
                           in itertools.product(neighbors, push_out_squares) if idm != idt]

        n = Node(board, self._token, available)

        score, move = self.minimax_alpha_beta(n, -math.inf, math.inf)
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

        move_to_make = self.move_towards_middle_early_strat(board)
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

