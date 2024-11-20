export type LLMType = 'gemini' | 'llama' | 'dify';

export interface GameState {
    board: number[][];
    currentPlayer: number;
    gameOver: boolean;
    winner?: number;
    score?: {
        black: number;
        white: number;
    };
    skipTurn?: boolean;
    lastMove?: [number, number] | null;
}

export interface GameStats {
    [key: string]: {
        games_played: number;
        wins: number;
        win_rate: number;
        model_trained: boolean;
    };
}