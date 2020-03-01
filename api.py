from board import Board
from boardstoreint import BoardStore
from flask import Flask, Response
from flask_restplus import Resource, Api, reqparse
import uuid
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

# The below switch controls whether boards larger than 4x4 or non-square are allowed.
# This is an expansion point for future development.
BASIC_BOARD_MODE = True

app = Flask(__name__)
api = Api(app)
data_store = BoardStore()


class DropToken(Resource):  # this Resource class composes the list and new game with BoardList and Board classes
    def get(self, gameID=None):
        games = data_store.get_game_list()
        if gameID not in games:
            return "Game not found", 404
        elif gameID is None:
            print("Game dict: ", str(data_store.get_game_list()))
            return {'games': list(data_store.get_game_list())}
        elif gameID in data_store.get_game_list():
            game = data_store.get_game(gameID)
            return game.get_game_status()
        else:
            return "Malformed Request or Game Not Found", 400

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("players", required=True, action='append')
        parser.add_argument("columns", type=int, required=True)
        parser.add_argument("rows", type=int, required=True)
        args = parser.parse_args()
        rows, cols = args['rows'], args['columns']

        players = args['players']

        if BASIC_BOARD_MODE:
            if (rows != 4) or (cols != 4) or rows != cols:
                # Returns 400 by default
                return 'Wrong board size; must be 4x4 for now.', 400
        if len(players) == 2 and (players[0] != players[1]):
            uni_id = uuid.uuid1().hex[:7]
            new_game = Board(id, rows, cols, players[0], players[1])
            success = data_store.create_game(uni_id, new_game)
            if success:
                return {"gameId": uni_id}
            else:
                return "Malformed Request", 400
                # Maybe the DB died or perms expired if this didn't work.
        else:
            return 'Players must be different IDs or must have exactly 2 players', 400


class PlayGame(Resource):

    def get(self, gameID: str):
        games = data_store.get_game_list()
        if gameID not in games:
            return "Game or moves not found", 404
        game = data_store.get_game(gameID)
        if len(game.move_list) > 0:
            return {"moves": game.move_list}, 200
        else:
            return "Malformed req", 400

    def post(self, gameID=None, playerID=None):
        parser = reqparse.RequestParser()
        parser.add_argument("column", type=int, required=True)
        args = parser.parse_args()
        col = args['column']
        games = data_store.get_game_list()

        # Don't need to worry about second condition erring out--statement evals False first
        if gameID not in games or playerID not in data_store.get_game(gameID).players:
            return "Game not found or player not a part of it", 404
        game = data_store.get_game(gameID)
        result:bool = game.move_handler(playerID, col)
        if result:
            data_store.update_db_file()
            return "OK", 200
        elif not result:
            return "Player tried to post when not their turn", 409

        return "Malformed or illegal or game is over", 400

    def delete(self, gameID=None, playerID=None):
        if gameID is None or playerID == None:
            return Response("Game or player not legit", status=404)
        else:
            game = data_store.get_game(game_id=gameID)
            result = game.quit_game(playerID)
            if result["status"]:
                data_store.update_db_file()
                return "OK", 202
            elif not result["status"]:
                return "Game already in DONE state or player/game not found", 410
            else:
                return "Malformed Request", 400


class MoveList(Resource):
    def get(self, gameID, move_number):
        game: Board = data_store.get_game(gameID)
        if not game:
            return "Game/move not found", 404
        elif move_number > len(game.move_list):
            return "Game/move not found", 404
        move = game.get_move(move_number)
        if move:
            return move, 200
        return "Malformed request", 400


api.add_resource(DropToken, "/drop_token/<string:gameID>", "/drop_token")
api.add_resource(PlayGame, "/drop_token/<string:gameID>/<string:playerID>", "/drop_token/<string:gameID>/moves")
api.add_resource(MoveList, "/drop_token/<string:gameID>/moves/<int:move_number>")

if __name__ == "__main__":
    app.run(debug=False, threaded=True)
