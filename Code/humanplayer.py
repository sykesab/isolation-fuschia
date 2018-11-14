import isolation


class HumanPlayer(isolation.Player):
    """
    A human player prompts for each move. If a script is supplied
    upon initialization, then the moves in the script are used
    before a prompt is issued.

    There is currently no checking for invalid inputse
    """

    def __init__(self, name, token, script=[]):
        """
        Initialize a new instance
        :param name: this player's name
        :param token: a
        :param script: a list of Move objects
        """
        super().__init__(name, token)
        self._script = script
        self._script_index = 0

    def take_turn(self, board):
        """
        Make a move on the isolation board
        :param board: an Board object
        :return: Return a Move object
        """

        if self._script_index < len(self._script):
            # Use the next move in the script
            move = self._script[self._script_index]
            self._script_index += 1
        else:
            # Prompt for a move. No validation is done.
            print('Your turn, {}:'.format(self._name))
            print(board)
            space_id = board.token_location(self.token())
            print('Current location:', space_id)
            move_to_spaces = board.neighbor_tiles(space_id)
            to_space_id = int(input('Moves {}: '.format(move_to_spaces)))
            push_out_space_ids = board.tile_square_ids()
            push_out_space_ids.add(space_id)
            push_out_space_ids.discard(to_space_id)
            push_out_space_id = int(input('Tiles {}: '.format(push_out_space_ids)))
            move = isolation.Move(to_space_id, push_out_space_id)

        return move


if __name__ == '__main__':
    # Create a match
    isolation.Board.set_dimensions(4, 6)
    ref = isolation.Match(HumanPlayer('Blue', isolation.Board.BLUE_TOKEN),
                          HumanPlayer('Red', isolation.Board.RED_TOKEN))
    ref.start_play()
