"""
This module runs a sequence of round-robin matches.
It flips a coin to determine who moves first
"""
import itertools
import urllib.request
import urllib.parse
import json
import pickle
import time
import random

import isolation

import aqua  # ['Will', 'David S']
import silver  # ['Sergio', 'David W']
import blue  # ['Seth', 'Alex']
import fuchsia  # ['Aaron', 'Logan']
import lime  # ['Orlando', 'Brendon']
import maroon  # ['Sunny', 'Zach']
import olive  # ['Michael', 'Alec']
import teal  # ['Eduardo', 'Marshall']

CGI_ROOT = 'http://wocoders.com/~sykesda/cgi-bin/'


def server_request(script, args):
    """
    Send a GET request to a server
    :param script: server CGI script to run
    :param args: a dictionary of argument, value pairings
    :return: A data structure created from a JSON response
    """
    url = CGI_ROOT + script + '?' + urllib.parse.urlencode(args)
    print(url)
    response = urllib.request.urlopen(url)

    return json.loads(response.read())


TEAMS = {
    'silver': ['Sergio', 'David W'],
    'blue': ['Seth', 'Alex'],
    'fuchsia': ['Aaron', 'Logan'],
    'lime': ['Orlando', 'Brendon'],
    'maroon': ['Sunny', 'Zach'],
    'olive': ['Michael', 'Alec'],
    'teal': ['Eduardo', 'Marshall']
}


def generate_matches(agent_classes):
    """
    Generate matches on the server and store the data in a pickle
    file matchinfo.txt
    :param agent_classes: a dictionary of player classes {color: class, ...}
    :return: None
    """
    colors = agent_classes.keys()
    pairings = [pair for pair in itertools.product(colors, colors) if pair[0] != pair[1]]

    matches = []
    for pairing in pairings:
        players = list(pairing)
        random.shuffle(players)
        blue, red = players
        match_info = server_request('newmatch.py', {'bluetoken': blue, 'redtoken': red})
        matches.append(match_info)
        time.sleep(1.0)

    print('\n'.join(str(match) for match in matches))

    pickle_file = open('matchinfo.txt', 'wb')
    pickle.dump(matches, pickle_file)
    pickle_file.close()


def run_tournament(agent_classes):
    """
    Play a bunch of matches between the teams listed in teams
    :param agent_classes: a dictionary of player classes
    :return:
    """

    # Create new red players
    # red_agents = {team: agent_classes[team](team, isolation.Board.RED_TOKEN) for team in agent_classes}
    #
    # blue_agents = {team: agent_classes[team](team, isolation.Board.BLUE_TOKEN) for team in agent_classes}

    pairings = [pair for pair in itertools.product(agent_classes.keys(), agent_classes.keys()) if pair[0] != pair[1]]

    print(pairings)

    for team1, team2 in pairings:
        # Flip a coin to see who goes first
        if random.choice(('H', 'T')) == 'H':
            blue_player = agent_classes[team1](team1, isolation.Board.BLUE_TOKEN)
            red_player = agent_classes[team2](team2, isolation.Board.RED_TOKEN)
        else:
            blue_player = agent_classes[team2](team2, isolation.Board.BLUE_TOKEN)
            red_player = agent_classes[team1](team1, isolation.Board.RED_TOKEN)

        board = isolation.Board()
        match = isolation.Match(blue_player, red_player, board)

        match.start_play()

        moves = board.moves()
        filename = f'{blue_player.name()}_{red_player.name()}.txt'
        with open(filename, 'w') as log_file:
            print('\n'.join(str(move) for move in moves), file=log_file)


        input('Hit RETURN to continue')


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

    # generate_matches(agent_classes)

    run_tournament(agent_classes)
