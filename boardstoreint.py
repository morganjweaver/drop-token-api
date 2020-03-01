import pickle
from board import Board
# Though interfaces are not as necessary in Python as in other languages, the need for one--or at least an abstract class--
# to sit in front of a real DB (Dynamo might be good here since the board object is lightweight)
# is acknowledged here as a principle of responsible OO design--loose coupling and minimal dependencies.

class BoardStoreInterface:
    def get_game_list(self) -> list:
        """Load in the list of games."""
        pass

    def get_game(self, game_id: str) -> dict:
        """Extract text from the currently loaded file."""
        pass

    def update_game(self, game_id:str, game_object: object)->bool:
        """Update Board object"""
        pass
    def create_game(self, game_id:str, game_object: object) -> bool:
        """Create Board object--should return True"""
        pass

class BoardStore(BoardStoreInterface):
    def __init__(self):
        db_file = open("fake_datastore.p","rb")
        self.fake_datastore:dict = pickle.load(db_file)
        db_file.close()

    def get_game_list(self) -> list:
        """Load in the list of games--here we simply create new dict"""
        if not self.fake_datastore:
            return []
        return list(self.fake_datastore.keys())

    def get_game(self, game_id: str) -> Board:
        """
        Extract text from the currently loaded file.
        This f(x) is 'dumb' in that get_game_list should
        be used first to check for game existence
        """
        return self.fake_datastore[game_id]

    def update_game(self, game_id:str, game_object: object) -> bool:
        """Update Board object"""
        if game_id not in self.fake_datastore.keys():
            return False
        self.fake_datastore[game_id] = game_object
        return True

    def create_game(self, game_id:str, game_object: object) -> bool:
        """Create Board object--should return True"""
        if game_id in self.fake_datastore.keys():
            return False
        self.fake_datastore[game_id] = game_object
        self.update_db_file()
        return True

    def update_db_file(self)->None:
        db_file = open("fake_datastore.p", "wb")
        pickle.dump(self.fake_datastore, db_file)
        db_file.close()
