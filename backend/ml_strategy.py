import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

class GameLearning:
    def __init__(self):
        # 各モデル用の学習器を初期化
        self.models = {
            'gemini': RandomForestClassifier(n_estimators=100, random_state=42),
            'llama': RandomForestClassifier(n_estimators=100, random_state=42),
            'dify': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        self.game_history = []
        self.win_rates = {
            'gemini': {'wins': 0, 'total': 0},
            'llama': {'wins': 0, 'total': 0},
            'dify': {'wins': 0, 'total': 0}
        }

    def _extract_features(self, board, valid_moves, current_player):
        """ボード状態から特徴量を抽出"""
        features = []
        board_array = np.array(board)
        
        # 1. 基本的なボード情報
        features.extend(board_array.flatten())
        
        # 2. 局面の評価値
        importance_map = np.array([
            [120, -20, 20, 5, 5, 20, -20, 120],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [120, -20, 20, 5, 5, 20, -20, 120]
        ])
        position_score = np.sum(board_array * importance_map)
        features.append(position_score)
        
        # 3. 局面の支配状況
        player_stones = np.sum(board_array == current_player)
        opponent_stones = np.sum(board_array == (3 - current_player))
        stone_ratio = player_stones / (player_stones + opponent_stones) if (player_stones + opponent_stones) > 0 else 0.5
        features.extend([player_stones, opponent_stones, stone_ratio])
        
        # 4. モビリティ（有効手の数）と相対的なモビリティ
        mobility = len(valid_moves)
        relative_mobility = mobility / 32  # 最大32手で正規化
        features.extend([mobility, relative_mobility])
        
        # 5. 盤面の安定性分析
        corners = [board[0][0], board[0][7], board[7][0], board[7][7]]
        edges = [board[i][j] for i, j in [(0,1), (0,6), (1,0), (1,7), (6,0), (6,7), (7,1), (7,6)]]
        
        corner_control = sum(1 for c in corners if c == current_player)
        opponent_corner = sum(1 for c in corners if c == (3 - current_player))
        edge_control = sum(1 for e in edges if e == current_player)
        features.extend([corner_control, opponent_corner, edge_control])
        
        # 6. パリティ（手番の優位性）
        total_empty = np.sum(board_array == 0)
        parity = 1 if total_empty % 2 == 0 else -1
        features.append(parity)
        
        # 7. 盤面のクラスター分析
        clusters = self._analyze_clusters(board_array, current_player)
        features.extend([clusters['size'], clusters['boundary']])
        
        return np.array(features)

    def _analyze_clusters(self, board, player):
        def find_cluster(x, y, visited):
            if (x, y) in visited or not (0 <= x < 8 and 0 <= y < 8):
                return 0, 0
            if board[x][y] != player:
                return 0, 0
                
            visited.add((x, y))
            size = 1
            boundary = 0
            
            # 隣接マスをチェック
            for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    if board[nx][ny] == 0:
                        boundary += 1
                    elif board[nx][ny] == player and (nx, ny) not in visited:
                        s, b = find_cluster(nx, ny, visited)
                        size += s
                        boundary += b
                        
            return size, boundary

        visited = set()
        max_cluster_size = 0
        total_boundary = 0
        
        for i in range(8):
            for j in range(8):
                if board[i][j] == player and (i, j) not in visited:
                    size, boundary = find_cluster(i, j, visited)
                    max_cluster_size = max(max_cluster_size, size)
                    total_boundary += boundary
                    
        return {'size': max_cluster_size, 'boundary': total_boundary}

    def get_move_suggestion(self, model_type, board, valid_moves, current_player):
        """学習した戦略に基づいて手を提案"""
        if not valid_moves:
            return None
            
        try:
            features = self._extract_features(board, valid_moves, current_player)
            move_scores = []
            
            for move in valid_moves:
                # 仮想的に手を打った状態の評価
                temp_board = [row[:] for row in board]
                temp_board[move[0]][move[1]] = current_player
                move_features = self._extract_features(temp_board, valid_moves, current_player)
                
                # 戦略的評価を組み合わせる
                position_score = self._evaluate_position(move[0], move[1], temp_board)
                
                try:
                    model_score = self.models[model_type].predict_proba([move_features])[0][1]
                    # モデルスコアと位置スコアを組み合わせる
                    combined_score = 0.7 * model_score + 0.3 * position_score
                    move_scores.append((move, combined_score))
                except:
                    # モデルが未学習の場合は位置スコアのみを使用
                    move_scores.append((move, position_score))
            
            # トーナメント選択方式で手を選ぶ
            tournament_size = min(3, len(move_scores))
            tournament = np.random.choice(len(move_scores), size=tournament_size, replace=False)
            best_move = max((move_scores[i] for i in tournament), key=lambda x: x[1])[0]
            
            return best_move
            
        except Exception as e:
            print(f"Error in get_move_suggestion: {e}")
            return valid_moves[0] if valid_moves else None

    def _evaluate_position(self, row, col, board):
        """位置の価値を評価（局面に応じて動的に調整）"""
        score = 0.0
        
        # 角の評価
        if (row, col) in [(0,0), (0,7), (7,0), (7,7)]:
            score += 1.0
        # 角の隣は基本的に不利
        elif (row, col) in [(0,1), (1,0), (0,6), (1,7), (6,0), (7,1), (6,7), (7,6)]:
            # ただし、対応する角が取られている場合は価値が上がる
            if (row <= 1 and col <= 1) and board[0][0] != 0: score += 0.5
            elif (row <= 1 and col >= 6) and board[0][7] != 0: score += 0.5
            elif (row >= 6 and col <= 1) and board[7][0] != 0: score += 0.5
            elif (row >= 6 and col >= 6) and board[7][7] != 0: score += 0.5
            else: score += 0.2
        # エッジの評価
        elif row in [0, 7] or col in [0, 7]:
            score += 0.8
        # 中央の評価
        else:
            # 中央に近いほど価値が高い
            center_distance = abs(3.5 - row) + abs(3.5 - col)
            score += 0.5 * (1 - center_distance / 7)
        
        return score

    def record_game(self, moves_history, winner, player_types):
        """ゲームの結果を記録して即座に学習"""
        self.game_history.append({
            'moves': moves_history,
            'winner': winner,
            'players': player_types,
            'timestamp': datetime.now()
        })
        
        # 勝率の更新
        winner_type = player_types[winner - 1] if winner > 0 else None
        for llm_type in player_types:
            self.win_rates[llm_type]['total'] += 1
            if llm_type == winner_type:
                self.win_rates[llm_type]['wins'] += 1

        # 即座に学習を実行
        self.learn_from_history()

    def learn_from_history(self):
        """ゲーム履歴から学習"""
        # 最新のゲームから学習
        latest_game = self.game_history[-1]
        
        for llm_type in ['gemini', 'llama', 'dify']:
            if llm_type in latest_game['players']:
                X = []
                y = []
                
                player_idx = latest_game['players'].index(llm_type)
                is_winner = latest_game['winner'] == player_idx + 1
                
                for move in latest_game['moves']:
                    if move['player_type'] == llm_type:
                        try:
                            features = self._extract_features(
                                move['board'],
                                move['valid_moves'],
                                move['current_player']
                            )
                            X.append(features)
                            # 勝敗に応じて報酬を設定
                            y.append(1.0 if is_winner else 0.0)
                        except Exception as e:
                            print(f"Error extracting features: {e}")
                            continue
                
                if X and y:
                    try:
                        X = np.array(X)
                        y = np.array(y)
                        
                        # 既存のモデルを更新
                        if hasattr(self.models[llm_type], 'n_features_in_'):
                            self.models[llm_type].fit(X, y)
                        else:
                            # 初めての学習
                            self.models[llm_type] = RandomForestClassifier(
                                n_estimators=100, 
                                random_state=42
                            ).fit(X, y)
                            
                    except Exception as e:
                        print(f"Error training model for {llm_type}: {e}")

    def get_strategy_stats(self):
        stats = {}
        for llm_type in ['gemini', 'llama', 'dify']:
            wins = self.win_rates[llm_type]['wins']
            total = self.win_rates[llm_type]['total']
            win_rate = (wins / total * 100) if total > 0 else 0
            
            stats[llm_type] = {
                'games_played': total,
                'wins': wins,
                'win_rate': round(win_rate, 2),
                'model_trained': hasattr(self.models[llm_type], 'n_features_in_')
            }
        
        return stats