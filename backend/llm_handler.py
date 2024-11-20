import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from huggingface_hub import InferenceClient
from ml_strategy import GameLearning
import json
import re

load_dotenv()

class LLMHandler:
    _game_learning = GameLearning()
    _moves_history = []

    def __init__(self, model_type):
        """APIキーの存在を確認し、なければエラーを発生"""
        self.model_type = model_type
        if model_type == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Gemini API key not found. Please set GOOGLE_API_KEY in .env file")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        elif model_type == "llama":
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                raise ValueError("Hugging Face API key not found. Please set HUGGINGFACE_API_KEY in .env file")
            self.client = InferenceClient(
                model="meta-llama/Llama-3-8b-instruct",
                token=api_key
            )
        elif model_type == "dify":
            self.api_key = os.getenv("DIFY_API_KEY")
            self.api_endpoint = os.getenv("DIFY_API_ENDPOINT")
            if not self.api_key or not self.api_endpoint:
                raise ValueError("Dify API credentials not found. Please set DIFY_API_KEY and DIFY_API_ENDPOINT in .env file")

    def _convert_board_text_to_array(self, board_text):
        board = []
        lines = board_text.strip().split('\n')[1:]
        for line in lines:
            row = []
            cells = line.split()[1:]
            for cell in cells:
                if cell == '-':
                    row.append(0)
                elif cell == 'W':
                    row.append(1)
                elif cell == 'B':
                    row.append(2)
            board.append(row)
        return board

    def get_move(self, board_state, valid_moves):
        """LLMと機械学習を組み合わせて最適な手を選択"""
        try:
            # ボードの状態を解析
            board_array = self._convert_board_text_to_array(board_state)
            
            # 機械学習モデルから提案を取得
            ml_suggestion = self._game_learning.get_move_suggestion(
                self.model_type,
                board_array,
                valid_moves,
                2 if board_state.count('B') > board_state.count('W') else 1
            )

            # プロンプトを生成
            prompt = self._create_prompt(board_state, valid_moves, ml_suggestion)
            
            try:
                if self.model_type == "gemini":
                    response = self.model.generate_content(prompt)
                    if not response.text:
                        raise Exception("Empty response from Gemini")
                    move_text = response.text
                elif self.model_type == "llama":
                    response = self.client.text_generation(
                        prompt,
                        max_new_tokens=50,
                        temperature=0.7,
                        top_p=0.9,
                        repetition_penalty=1.1,
                        do_sample=True
                    )
                    if not response:
                        raise Exception("Empty response from Llama")
                    move_text = response.strip()
                else:  # dify
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "query": prompt,
                        "response_mode": "blocking",
                        "conversation_id": "",
                        "user": "user"
                    }
                    
                    api_url = f"{self.api_endpoint.rstrip('/')}/chat-messages"
                    response = requests.post(
                        api_url,
                        headers=headers,
                        json=data,
                        timeout=10
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"API returned status {response.status_code}")
                    
                    response_data = response.json()
                    move_text = response_data.get("answer", "")
                    if not move_text:
                        raise Exception("Empty response from API")

                # LLMの応答から座標を抽出
                move = self._extract_move_from_response(move_text, valid_moves)
                if move:
                    return move

                if ml_suggestion and ml_suggestion in valid_moves:
                    print(f"Using ML suggestion: {ml_suggestion}")
                    return ml_suggestion

                # 最後の手段として最初の有効な手を選択
                return valid_moves[0]

            except Exception as e:
                print(f"Error in LLM response processing: {e}")
                return ml_suggestion if ml_suggestion in valid_moves else valid_moves[0]

        except Exception as e:
            print(f"Error in get_move: {e}")
            return valid_moves[0] if valid_moves else None

    def _extract_move_from_response(self, move_text, valid_moves):
        """LLMの応答から有効な手を抽出"""
        try:
            matches = re.findall(r'(\d+)\s*,\s*(\d+)', move_text)
            if matches:
                row, col = map(int, matches[0])
                if (row, col) in valid_moves:
                    return row, col
            
            numbers = re.findall(r'\d+', move_text)
            if len(numbers) >= 2:
                row, col = map(int, numbers[:2])
                if (row, col) in valid_moves:
                    return row, col
            
            return None
        except:
            return None

    def _create_prompt(self, board_state, valid_moves, ml_suggestion):
        if self.model_type == "llama":
            # Llama用のプロンプトフォーマット
            base_prompt = f"""<s>[INST] あなたは熟練のオセロプレイヤーです。
以下のボード状態から最適な手を選んでください。

ボード状態:
{board_state}

有効な手: {valid_moves}

以下の戦略を考慮してください:
- 角の確保が最重要
- 相手に角を取られる手は避ける
- 安定した石を増やす
- 相手の動きを予測

必ず「行番号,列番号」の形式で1手だけ返してください。
例: 2,3 [/INST]"""
        else:
            # その他のモデル用のプロンプト
            base_prompt = f"""あなたは熟練のオセロプレイヤーです。
以下のボード状態から最適な手を選んでください。

ボード状態:
{board_state}

有効な手: {valid_moves}

以下の戦略を考慮してください:
- 角の確保が最重要
- 相手に角を取られる手は避ける
- 安定した石を増やす
- 相手の動きを予測

必ず「行番号,列番号」の形式で1手だけ返してください。
例: 2,3"""

        if ml_suggestion:
            ml_hint = f"""

機械学習の分析によると ({ml_suggestion[0]}, {ml_suggestion[1]}) が有望な手です。
この提案も考慮に入れて最適な手を選んでください。"""
            return base_prompt + ml_hint

        return base_prompt

    def record_move(self, board, valid_moves, move, current_player):
        """記録"""
        if move:
            self._moves_history.append({
                'board': board,
                'valid_moves': valid_moves,
                'move': move,
                'player_type': self.model_type,
                'current_player': current_player
            })

    @classmethod
    def end_game(cls, winner, player_types):
        """ゲーム終了時の処理"""
        if cls._moves_history:
            cls._game_learning.record_game(cls._moves_history, winner, player_types)
            cls._moves_history = []
            
            # 戦績を表示
            stats = cls._game_learning.get_strategy_stats()
            print("\n=== 戦績レポート ===")
            for llm_type, stat in stats.items():
                print(f"\n{llm_type.upper()}:")
                print(f"対戦数: {stat['games_played']}")
                print(f"勝利数: {stat['wins']}")
                print(f"勝率: {stat['win_rate']}%")

    @classmethod
    def get_stats(cls):
        """現在の戦績を取得"""
        return cls._game_learning.get_strategy_stats()