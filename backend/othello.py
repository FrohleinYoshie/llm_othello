class OthelloGame:
    def __init__(self):
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 1  # 白
        self.board[3][4] = self.board[4][3] = 2  # 黒
        self.current_player = 2  # 黒から開始
        self.move_history = []  # 手の履歴を記録
        
    def get_board_state(self):
        """現在のボード状態を取得"""
        return [row[:] for row in self.board]
    
    def is_valid_move(self, row, col):
        """指定された位置が有効な手かどうかを判定"""
        if not (0 <= row < 8 and 0 <= col < 8) or self.board[row][col] != 0:
            return False
            
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        opponent = 1 if self.current_player == 2 else 2
        
        for dx, dy in directions:
            if self._check_direction(row, col, dx, dy, opponent):
                return True
        return False
    
    def _check_direction(self, row, col, dx, dy, opponent):
        """特定の方向に石を裏返せるかチェック"""
        x, y = row + dx, col + dy
        if not (0 <= x < 8 and 0 <= y < 8) or self.board[x][y] != opponent:
            return False
            
        while 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == opponent:
            x, y = x + dx, y + dy
            
        return 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == self.current_player
    
    def make_move(self, row, col):
        """指定された位置に石を置き、挟まれた石を裏返す"""
        if not self.is_valid_move(row, col):
            return False
            
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        opponent = 1 if self.current_player == 2 else 2
        
        self.board[row][col] = self.current_player
        pieces_to_flip = []
        
        for dx, dy in directions:
            x, y = row + dx, col + dy
            temp_flip = []
            while 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == opponent:
                temp_flip.append((x, y))
                x, y = x + dx, y + dy
                
            if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == self.current_player:
                pieces_to_flip.extend(temp_flip)
        
        for x, y in pieces_to_flip:
            self.board[x][y] = self.current_player
        
        # 手と結果を履歴に記録
        self.move_history.append({
            'position': (row, col),
            'player': self.current_player,
            'flipped': pieces_to_flip,
            'board_state': self.get_board_state()
        })
            
        self.current_player = opponent
        return True

    def has_empty_spaces(self):
        """盤面に空きマスがあるかチェック"""
        return any(0 in row for row in self.board)
    
    def get_valid_moves(self):
        """現在のプレイヤーの有効な手をすべて取得"""
        valid_moves = []
        for i in range(8):
            for j in range(8):
                if self.is_valid_move(i, j):
                    valid_moves.append((i, j))
        return valid_moves
    
    def should_skip_turn(self):
        """現在のプレイヤーがパスすべきかどうかを判定"""
        return len(self.get_valid_moves()) == 0 and self.has_empty_spaces()
    
    def is_game_over(self):
        """ゲームが終了したかどうかを判定"""
        # 盤面が埋まっている場合
        if not self.has_empty_spaces():
            return True
            
        # 現在のプレイヤーが置けるか確認
        current_moves = self.get_valid_moves()
        if current_moves:
            return False
            
        # 相手プレイヤーが置けるか確認
        self.current_player = 3 - self.current_player
        opponent_moves = self.get_valid_moves()
        self.current_player = 3 - self.current_player
        
        # 両プレイヤーとも置けない場合
        return not opponent_moves
    
    def get_winner(self):
        """勝者を判定して返す"""
        if not self.is_game_over():
            return None
            
        black_count = sum(row.count(2) for row in self.board)
        white_count = sum(row.count(1) for row in self.board)
        
        if black_count > white_count:
            return 2
        elif white_count > black_count:
            return 1
        else:
            return 0  # Draw
            
    def get_score(self):
        """現在のスコアを取得"""
        black_count = sum(row.count(2) for row in self.board)
        white_count = sum(row.count(1) for row in self.board)
        return {"black": black_count, "white": white_count}
    
    def to_string(self):
        """ボードを文字列として返す（LLMのための入力形式）"""
        result = ["  0 1 2 3 4 5 6 7"]
        for i in range(8):
            row = [str(i)]
            for j in range(8):
                if self.board[i][j] == 0:
                    row.append("-")
                elif self.board[i][j] == 1:
                    row.append("W")
                else:
                    row.append("B")
            result.append(" ".join(row))
        return "\n".join(result)

    def get_game_stats(self):
        """ゲームの統計情報を取得"""
        total_moves = len(self.move_history)
        moves_by_player = {
            1: len([m for m in self.move_history if m['player'] == 1]),
            2: len([m for m in self.move_history if m['player'] == 2])
        }
        flips_by_player = {
            1: sum(len(m['flipped']) for m in self.move_history if m['player'] == 1),
            2: sum(len(m['flipped']) for m in self.move_history if m['player'] == 2)
        }
        corners_taken = sum(1 for m in self.move_history 
                          if m['position'] in [(0,0), (0,7), (7,0), (7,7)])
        
        return {
            'total_moves': total_moves,
            'moves_by_player': moves_by_player,
            'flips_by_player': flips_by_player,
            'corners_taken': corners_taken,
            'current_score': self.get_score()
        }

    def undo_last_move(self):
        """最後の手を取り消す（デバッグ用）"""
        if not self.move_history:
            return False
        
        last_move = self.move_history.pop()
        self.board = last_move['board_state']
        self.current_player = last_move['player']
        return True