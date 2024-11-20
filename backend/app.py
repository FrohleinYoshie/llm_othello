from flask import Flask, request, jsonify
from flask_cors import CORS
from othello import OthelloGame
from llm_handler import LLMHandler
import traceback

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

games = {}

@app.route('/api/start', methods=['POST', 'OPTIONS'])
def start_game():
    try:
        if request.method == 'OPTIONS':
            return handle_options_request()

        data = request.json
        game_id = str(len(games))
        llm1_type = data.get('player1')
        llm2_type = data.get('player2')
        
        # LLMハンドラーの作成を試みる
        try:
            player1 = LLMHandler(llm1_type)
            player2 = LLMHandler(llm2_type)
        except ValueError as e:
            return jsonify({
                'error': f"API key error: {str(e)}. Please check your .env file."
            }), 400
        
        games[game_id] = {
            'game': OthelloGame(),
            'players': [player1, player2],
            'player_types': [llm1_type, llm2_type],
            'consecutive_skips': 0
        }
        
        return jsonify({
            'gameId': game_id,
            'board': games[game_id]['game'].get_board_state(),
            'currentPlayer': games[game_id]['game'].current_player,
            'playerTypes': games[game_id]['player_types']
        })
    except Exception as e:
        print(f"Error in start_game: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/move/<game_id>', methods=['GET', 'OPTIONS'])
def make_move(game_id):
    try:
        if request.method == 'OPTIONS':
            return handle_options_request()

        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
            
        game_data = games[game_id]
        game = game_data['game']
        
        if game.is_game_over():
            winner = game.get_winner()
            score = game.get_score()
            
            LLMHandler.end_game(winner, game_data['player_types'])
            
            return jsonify({
                'gameOver': True,
                'winner': winner,
                'score': score,
                'board': game.get_board_state(),
                'playerTypes': game_data['player_types']
            })
        
        # パスが必要かチェック
        if game.should_skip_turn():
            game_data['consecutive_skips'] += 1
            if game_data['consecutive_skips'] >= 2:
                # 両プレイヤーが連続でパスした場合、ゲーム終了
                winner = game.get_winner()
                score = game.get_score()
                
                LLMHandler.end_game(winner, game_data['player_types'])
                
                return jsonify({
                    'gameOver': True,
                    'winner': winner,
                    'score': score,
                    'board': game.get_board_state(),
                    'playerTypes': game_data['player_types']
                })
            
            # パスして次のプレイヤーへ
            game.current_player = 3 - game.current_player
            return jsonify({
                'board': game.get_board_state(),
                'currentPlayer': game.current_player,
                'skipTurn': True,
                'playerTypes': game_data['player_types']
            })
        
        # 有効な手があれば、連続パスカウントをリセット
        game_data['consecutive_skips'] = 0
        
        current_player_idx = 0 if game.current_player == 1 else 1
        llm = game_data['players'][current_player_idx]
        
        valid_moves = game.get_valid_moves()
        board_string = game.to_string()
        
        try:
            move = llm.get_move(board_string, valid_moves)
            
            last_move = None
            if move:
                llm.record_move(
                    game.get_board_state(),
                    valid_moves,
                    move,
                    game.current_player
                )
                row, col = move
                game.make_move(row, col)
                last_move = move
            
            return jsonify({
                'board': game.get_board_state(),
                'currentPlayer': game.current_player,
                'lastMove': last_move,
                'playerTypes': game_data['player_types']
            })
        
        except Exception as e:
            print(f"Error getting move from LLM: {str(e)}")
            return jsonify({'error': f"LLM error: {str(e)}"}), 500

    except Exception as e:
        print(f"Error in make_move: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET', 'OPTIONS'])
def get_stats():
    try:
        if request.method == 'OPTIONS':
            return handle_options_request()
        return jsonify(LLMHandler.get_stats())
    except Exception as e:
        print(f"Error in get_stats: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

def handle_options_request():
    response = jsonify({'status': 'ok'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.route('/api/check-keys', methods=['GET', 'OPTIONS'])
def check_api_keys():
    try:
        if request.method == 'OPTIONS':
            return handle_options_request()
            
        keys_status = {
            'gemini': bool(os.getenv("GOOGLE_API_KEY")),
            'llama': bool(os.getenv("HUGGINGFACE_API_KEY")),
            'dify': bool(os.getenv("DIFY_API_KEY")) and bool(os.getenv("DIFY_API_ENDPOINT"))
        }
        
        return jsonify({
            'keysValid': all(keys_status.values()),
            'status': keys_status
        })
    except Exception as e:
        print(f"Error checking API keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)