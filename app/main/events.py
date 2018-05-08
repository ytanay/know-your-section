from flask import session
from flask_socketio import emit, join_room, send

from app.main.game import Game
from app.main.state import CONNECTED_CLIENTS
from .. import socketio

ROOM_NAME = 'global-room'
CURRENT_GAME = None


# Player name: the person who is being tested, must be on the voting team
# Human name: name presented to the world
# Computer name: actual player


# TODO: voting
# TODO: assertions
# TODO: prefill names


class Player:
    def __init__(self, name, team, score=0):
        self.name, self.team, self.score = name, team, score

    def serialize(self):
        return vars(self)


def serialized_clients():
    return {'players': [y.serialize() for y in CONNECTED_CLIENTS.values()]}


@socketio.on('connect', namespace='/game')
def game_connection():
    join_room(ROOM_NAME)
    join_room(session['name'])
    CONNECTED_CLIENTS[session['name']] = Player(session['name'], session['team'])
    emit('player-state', serialized_clients(), room='admin', namespace='/admin')


@socketio.on('disconnect', namespace='/game')
def disconnected():
    print(f'{session["name"]} has disconnected')

    CONNECTED_CLIENTS.pop(session['name'])

    if CURRENT_GAME and CURRENT_GAME.active and session['name'] in CURRENT_GAME.players:   # TODO: test this
        print('Oh no, player has disconnected')

    emit('player-state', serialized_clients(), room='admin', namespace='/admin')


@socketio.on('player-state', namespace='/admin')
def get_state():
    join_room('admin')
    emit('player-state', serialized_clients())


@socketio.on('start-game', namespace='/admin')
def start_game(params):

    global CURRENT_GAME

    player_name, computer_name, human_name = params['player-name'].capitalize(), params['computer-name'].capitalize(), params['human-name'].capitalize()
    players = {player_name, computer_name, human_name}

    print(CONNECTED_CLIENTS, players)

    if not all(x in CONNECTED_CLIENTS for x in players) or player_name == computer_name or player_name == human_name:
        return emit('start-game', 'Invalid players')

    player, computer, human = CONNECTED_CLIENTS[player_name], CONNECTED_CLIENTS[computer_name], CONNECTED_CLIENTS[
        human_name]

    if computer.team != human.team or player.team == computer.team or player.team == human.team:
        return emit('start-game', 'Invalid player groups')

    voting_team = player.team

    CURRENT_GAME = Game(player_name, human_name, computer_name, voting_team, params['duration'])

    for name, user in CONNECTED_CLIENTS.items():
        emit('start-game', {
            'player-name': player_name,
            'human-name': human_name,
            'computer-name': computer_name if user.team != voting_team else '',
            'is-player': name == player_name,
            'is-computer': name == computer_name,
            'duration': params['duration']
        }, room=name, namespace='/game')

    emit('start-game', {
        'duration': params['duration']
    })


@socketio.on('end-game', namespace='/admin')
def end_game(params):
    print('Ending game!')
    emit('end-game', {
        'voting-team': CURRENT_GAME.voting_team
    }, room=ROOM_NAME, namespace='/game')
    CURRENT_GAME.end_game()


@socketio.on('vote', namespace='/game')
def vote(vote):
    print(f"{session['name']} voted for {vote}")
    if CURRENT_GAME.active:
        raise Exception('Someones causing problems')

    user = CONNECTED_CLIENTS[session['name']]

    was_real = CURRENT_GAME.computer == CURRENT_GAME.human
    user_said_real = vote == 'option-real'

    user.score += 2 if was_real is user_said_real else 1
    emit('player-state', serialized_clients(), room='admin', namespace='/admin')


@socketio.on('message', namespace='/game')
def message(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    emit('message', {
        'from': CURRENT_GAME.player if session['name'] == CURRENT_GAME.player else CURRENT_GAME.human,
        'contents': message,
        'team': session['team']
    }, room=ROOM_NAME)


@socketio.on('vote-result', namespace='/admin')
def vote_result():
    print('Publishing!')
    emit('vote-result', {
        'answer': CURRENT_GAME.computer
    }, room=ROOM_NAME, namespace='/game')