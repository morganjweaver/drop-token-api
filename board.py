STATES = ("IN PROGRESS", "DONE")
ACTION_TYPES = ("MOVE", "QUIT")


class Board:
    def __init__(self, id, rows, cols, playerA, playerB):
        self.id = id
        self.board = [[0 for i in range(rows)] for j in range(cols)]
        self.players = [playerA, playerB]
        self.move_list = []
        self.col_totals = [0 for i in range(cols)]
        self.row_totals = [0 for j in range(rows)]
        self.left_right_diag_totals = [0, 0]
        self.status = []  # Contains winner if applicable; otherwise state is in progress or draw
        self.row = rows
        self.col = cols
        self.state = "IN PROGRESS"
        self.winner = None
        self.gamepieces = {playerA: -1, playerB: 1}
        # diagonals are easy to ID but antidiagonals are trickier!  create list
        self.antidiagonals = self.tiresome_antidiagonal_coords_initializer(rows)

    def tiresome_antidiagonal_coords_initializer(self, square_size: int) -> list:
        antidiags = []
        j = square_size - 1
        for i in range(square_size):
            antidiags.append((i, j))
            j -= 1
        return antidiags

    def action_record_formatter(self, action_type: str, player: str, col=None) -> dict:
        # Safety checks happen mostly outside this function as it's just a formatting tool
        # to eliminate redundancy and error
        if col:
            return {"type": action_type, "player": player, "column": col}
        else:
            return {"type": action_type, "player": player}

    def get_move(self, move_num: int) -> dict:
        return self.move_list[move_num - 1]  # Correct for zero-indexing

    def get_game_status(self) -> dict:
        if not self.winner:
            return {"players": self.players, "state": self.state}
        else:
            return {"players": self.players, "state": self.state, "winner": self.winner}

    def quit_game(self, userID: str) -> dict:
        if userID not in self.players:
            return {"status": False, "reason": "player not found in game"}
        elif self.state != "IN PROGRESS":
            return {"status": False, "reason": "game is not in quittable state"}
        else:
            action_record = self.action_record_formatter("QUIT", userID)
            if len(list(action_record.keys())) > 0:
                self.move_list.append(action_record)
                self.state = "DONE"
                return {"status": True, "reason": "Successful quit"}

    def check_for_win(self) -> bool:
        """
        Check for possible wins by calculating total number of player A or player B tokens on each axis and diag
        :returns: True or False
        """
        total_list = self.row_totals + self.col_totals + self.left_right_diag_totals
        for i in total_list:
            if abs(i) == self.row:
                return True
        return False

    def check_for_draw(self) -> bool:
        """
        Checks to see if ANY spaces remain on board; assumes square board
        :return:
        """
        total_list = self.row_totals + self.col_totals + self.left_right_diag_totals
        for i in total_list:
            if abs(i) != self.row:
                return False
        return True

    def column_is_not_full(self, col: int) -> int:
        """
        Returns empty row number for new placement in col; otherwise -1
        :param col: desired column to drop token in
        :return: -1 if unavail or int in range [0,max_col_size-1] due to zero-indexing
        """
        for row in range(self.row - 1, -1, -1):
            if self.board[row][col] == 0:
                return row
        return -1

    def gameplay_move(self, player: str, col: int) -> (bool, int):
        """
        This function only places the token if there is space but does not check player turn.
        Function does not check for win
        :param player: player ID to place move
        :param col: col to drop token into
        :return: bool and err code if applicable
        """
        avail_row = self.column_is_not_full(col - 1)  # TODO: Make sure zero-indexing checks align
        if avail_row == -1:
            return False, -1
        else:
            self.board[avail_row][col - 1] = self.gamepieces[
                player]  # Set the position on the board to that player's token
            return True, avail_row

    def update_board_counts(self, player: str, row: int, col: int) -> None:  # col and row not zero-indexed in args
        """
        Incoming row/col are already zero-indexed
        Updates vert/horiz/diag counts, does NOT set winner or check win
        :return:
        """
        self.row_totals[row] += self.gamepieces[player]
        self.col_totals[col] += self.gamepieces[player]
        if col == row: self.left_right_diag_totals[0] += self.gamepieces[player]
        if (row, col) in self.antidiagonals: self.left_right_diag_totals[1] += self.gamepieces[player]

    def move_handler(self, player: str, column: int) -> (bool, int):
        """
        Update the board with latest move:
            1. Check player turn
            2. Check space avail.
            3. Add token to board
            4. Update the row/col/diag count
            5. Update game state--win/lose/etc.
        :param player: str - player ID
        :returns: bool - success or err code
        """
        # TODO: Should this f(x) allow moves if state is DONE?  Not sure.  Instructions don't mention this!
        if self.move_list and self.move_list[-1]["player"] == player:
            return False, 409  # Not player's turn
        elif self.state != "DONE":
            result, row = self.gameplay_move(player,
                                             column)  # TODO: zero-indexing corrected only inside gameplay move f(x) and checker
            if result:
                self.update_board_counts(player, row, column - 1)  # col must be zero-indexed
                action_record = self.action_record_formatter("MOVE", player, column)
                self.move_list.append(action_record)  # Update game record
                if self.check_for_win():
                    self.state = "DONE"
                if self.check_for_draw():
                    self.state = "DONE"
                    self.winner = None
                return True  # Placed move, did book-keeping
        else:
            return False  # Something has gone wrong
