"""
Use this module to run a match that is being displayed in a browser
"""
import urllib.request
import urllib.parse
import json
import isolation
import copy
import time

import randomplayer

import aqua  # ['Will', 'David S']
import silver  # ['Sergio', 'David W']
import blue  # ['Seth', 'Alex']
import fuchsia  # ['Aaron', 'Logan']
import lime  # ['Orlando', 'Brendon']
import maroon  # ['Sunny', 'Zach']
import olive  # ['Michael', 'Alec']
import teal  # ['Eduardo', 'Marshall']

_CGI_ROOT = 'http://wocoders.com/~sykesda/cgi-bin/'


def _server_request(script, **args):
    """
    Send a GET request to a server
    :param script: server CGI script to run
    :param args: a dictionary of argument, value pairings
    :return: A data structure created from a JSON response
    """
    url = _CGI_ROOT + script + '?' + urllib.parse.urlencode(args)
    print('REQUEST:', url)
    response = urllib.request.urlopen(url)

    reply = json.loads(response.read())
    print('REPLY:', reply)
    return reply


class LocalPlayer(isolation.Player):
    """
    A local player is one running on the local computer
    """

    def __init__(self, name, token, match_id, team_color, player_class):
        """

        :param name:
        :param token:
        :param match_id:
        :param team_color:
        """
        super().__init__(name, token)
        self._player = player_class(name, token)
        self._match_id = match_id
        self._team_color = team_color
        self._color = 'blue' if token is isolation.Board.BLUE_TOKEN else 'red'
        self._opponent_token = isolation.Board.RED_TOKEN if token is isolation.Board.BLUE_TOKEN else isolation.Board.RED_TOKEN

    def take_turn(self, board):
        """
        Make a move and post it to the server
        :param board:
        :return:
        """
        print(f'{self._color} [local] taking turn')

        move = self._player.take_turn(board)

        # Let's see if this is a winning move
        board_copy = copy.deepcopy(board)
        board_copy.make_move(self._token, move)
        winning_move = len(board_copy.neighbor_tiles(board_copy.token_location(self._opponent_token))) == 0

        # Post the move to the server
        move_number = len(board.moves()) + 1
        response = _server_request('postmove.py', matchid=self._match_id, movenumber=move_number,
                                   to=move.to_square_id, pushout=move.pushout_square_id,
                                   token=self._color, winningmove=int(winning_move))
        nbr_tries = 1
        while nbr_tries < 3 and response['status'] != 'OK':
            # Problem so wait a bit and try up to three more times
            print(f'*** PROBLEM POSTING TO SERVER {move}\n    {response["error"]}')
            nbr_tries += 1
            time.sleep(1.0)
            response = _server_request('postmove.py', matchid=self._match_id, movenumber=len(board.moves()),
                                       to=move.to_square_id, pushout=move.pushout_square_id,
                                       token=self._color, winningmove=int(winning_move))

        if response['status'] != 'OK':
            print(f'COULD NOT POST {move}')

        return move


class RemotePlayer(isolation.Player):
    """
    A remote player is posting moves to the server
    """

    def __init__(self, name, token, match_id, team_color, player_class):
        """

        :param name: a string
        :param token: a token
        :param match_id: a number
        :param team_color: a string
        """
        super().__init__(name, token)
        self._player = player_class(name, token)
        self._match_id = match_id
        self._team_color = team_color
        self._color = 'blue' if token is isolation.Board.BLUE_TOKEN else 'red'
        self._opponent_token = isolation.Board.RED_TOKEN if token is isolation.Board.BLUE_TOKEN else isolation.Board.RED_TOKEN

    def take_turn(self, board):
        """
        Fetch a move from the server
        :param board:
        :return:
        """

        print(f'{self._color} [remote] taking turn')

        # Fetch the move to the server
        move_number = len(board.moves()) + 1
        response = _server_request('fetchmove.py', matchid=self._match_id, movenumber=move_number,
                                   token=self._color)
        nbr_tries = 1
        while nbr_tries < 6 and response['status'] == 'NO MOVE':
            # Problem so wait a bit and try up to three more times
            print(f'*** PROBLEM FETCHING MOVE {move_number} FROM SERVER ({nbr_tries})\n    {response["error"]}')
            nbr_tries += 1
            time.sleep(2.0)
            response = _server_request('fetchmove.py', matchid=self._match_id, movenumber=len(board.moves()),
                                       token=self._color)
        if nbr_tries > 5:
            reply = input('No move on server. Try again? [Y/n]').strip() or 'Y'
            while reply[0].upper() == 'Y':
                response = _server_request('fetchmove.py', matchid=self._match_id, movenumber=len(board.moves()),
                                           token=self._color)
                if response['status'] == 'OK':
                    reply = 'N'  # nasty code to leave this loop!
                else:
                    reply = input('No move on server. Try again? [Y/n]').strip().upper() or 'Y'

        if response['status'] == 'OK':
            move = isolation.Move(response['to'], response['pushout'])
        else:
            move = None

        print(f'    {move}')

        return move


if __name__ == '__main__':
    isolation.Board.set_dimensions(6, 8)

    agent_classes = {
        'aqua': aqua.PlayerAgent,
        'silver': silver.PlayerAgent,
        'blue': blue.PlayerAgent,
        'fuchsia': fuchsia.PlayerAgent,
        'lime': lime.PlayerAgent,
        'maroon': maroon.PlayerAgent,
        'olive': olive.PlayerAgent,
        'teal': teal.PlayerAgent,
    }

    # The local team is always blue
    local_team = input('Enter the local team color: ')
    remote_team = input('Enter the remote team color: ')

    blue_player_local = input('Is the local player BLUE [y/n]? ').strip() in 'yY'

    match_id = int(input('Enter the match ID: '))

    if blue_player_local:
        blue_player = LocalPlayer(f'Local Player {local_team}', isolation.Board.BLUE_TOKEN, match_id,
                                  local_team, agent_classes[local_team])
        red_player = RemotePlayer(f'Remote Player {remote_team}', isolation.Board.RED_TOKEN, match_id,
                                  remote_team, agent_classes[remote_team])
    else:
        blue_player = RemotePlayer(f'Remote Player {remote_team}', isolation.Board.BLUE_TOKEN, match_id,
                                   remote_team, agent_classes[remote_team])
        red_player = LocalPlayer(f'Local Player {remote_team}', isolation.Board.RED_TOKEN, match_id,
                                 remote_team, agent_classes[remote_team])

    board = isolation.Board()
    match = isolation.Match(blue_player, red_player, board)

    match.start_play()
