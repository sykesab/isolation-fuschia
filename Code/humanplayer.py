"""
A Human player accepts moves interactively, but can also
utilize a script

Last update: 25 NOV 2018
"""
import isolation
import csv


class HumanPlayer(isolation.Player):
    """
    A human player prompts for each move. If a script is supplied
    upon initialization, then the moves in the script are used
    before a prompt is issued.

    There is currently no checking for invalid inputs
    """

    def __init__(self, name, token, script=[]):
        """
        Initialize a new instance
        :param name: this player's name
        :param token: either RED_TOKEN or BLUE_TOKEN
        :param script: a list of Move objects or a string
                       that is a CSV file name
        """
        super().__init__(name, token)

        if type(script) is list:
            self._script = script
        else:
            with open(script) as script_file:
                reader = csv.DictReader(script_file)
                moves = [row for row in reader]
            if token is isolation.Board.BLUE_TOKEN:
                # Blue moves first
                self._script = [isolation.Move(int(row['move']), int(row['push'])) for row in moves[0::2]]
            else:
                self._script = [isolation.Move(int(row['move']), int(row['push'])) for row in moves[1::2]]

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
            print(self._token, move)
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
    isolation.Board.set_dimensions(6, 8)
    # # Create a match
    # ref = isolation.Match(HumanPlayer('Blue', isolation.Board.BLUE_TOKEN),
    #                       HumanPlayer('Red', isolation.Board.RED_TOKEN),
    #                       Board())
    # ref.start_play()

    # Create a match using a script in a file
    print()
    print('Start scripted game')
    ref = isolation.Match(HumanPlayer('Blue', isolation.Board.BLUE_TOKEN,
                                      '2018-11-25 15:52:29.435889.csv'),
                          HumanPlayer('Red', isolation.Board.RED_TOKEN,
                                      '2018-11-25 15:52:29.435889.csv'),
                          isolation.Board())
    ref.start_play()

