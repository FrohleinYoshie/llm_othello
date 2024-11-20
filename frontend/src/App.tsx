import React, { useState, useEffect } from 'react';
import { Container, Button, Box, CircularProgress, Alert, Typography } from '@mui/material';
import OthelloBoard from './components/OthelloBoard';
import GameSetup from './components/GameSetup';
import GameStatus from './components/GameStatus';
import StatsDisplay from './components/StatsDisplay';
import { GameState, LLMType, GameStats } from './types/types';

const initialGameState: GameState = {
    board: Array(8).fill(null).map(() => Array(8).fill(0)),
    currentPlayer: 2,
    gameOver: false,
    skipTurn: false
};

function App() {
    const [gameState, setGameState] = useState<GameState>(initialGameState);
    const [gameId, setGameId] = useState<string | null>(null);
    const [player1Type, setPlayer1Type] = useState<LLMType | null>(null);
    const [player2Type, setPlayer2Type] = useState<LLMType | null>(null);
    const [isGameStarted, setIsGameStarted] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [gameStats, setGameStats] = useState<GameStats | null>(null);

    const startGame = async (p1: LLMType, p2: LLMType) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch('http://127.0.0.1:5000/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    player1: p1,
                    player2: p2,
                }),
                credentials: 'omit'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'ゲームの開始に失敗しました');
            }
            
            const data = await response.json();
            setGameId(data.gameId);
            setGameState({
                ...gameState,
                board: data.board,
                currentPlayer: data.currentPlayer,
            });
            setPlayer1Type(p1);
            setPlayer2Type(p2);
            setIsGameStarted(true);
        } catch (error) {
            console.error('Error starting game:', error);
            setError(error instanceof Error ? error.message : 'ゲームの開始に失敗しました');
        } finally {
            setIsLoading(false);
        }
    };

    const makeMove = async () => {
        if (!gameId || gameState.gameOver || isLoading) return;

        setIsLoading(true);
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/move/${gameId}`, {
                credentials: 'omit'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '手の実行に失敗しました');
            }

            const data = await response.json();
            setGameState({
                board: data.board,
                currentPlayer: data.currentPlayer,
                gameOver: data.gameOver || false,
                winner: data.winner,
                score: data.score,
                skipTurn: data.skipTurn || false,
                lastMove: data.lastMove
            });

            if (data.gameOver) {
                fetchGameStats();
            }
        } catch (error) {
            console.error('Error making move:', error);
            setError(error instanceof Error ? error.message : '手の実行中にエラーが発生しました');
            if (!gameState.gameOver) {
                setTimeout(resetGame, 3000);
            }
        } finally {
            setIsLoading(false);
        }
    };

    const fetchGameStats = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/stats', {
                credentials: 'omit'
            });
            
            if (!response.ok) {
                throw new Error('統計データの取得に失敗しました');
            }

            const stats = await response.json();
            setGameStats(stats);
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    };

    useEffect(() => {
        fetchGameStats();
    }, []);

    useEffect(() => {
        let timeoutId: NodeJS.Timeout;
        if (isGameStarted && !gameState.gameOver && !error && !isLoading) {
            timeoutId = setTimeout(makeMove, 1000);
        }
        return () => {
            if (timeoutId) clearTimeout(timeoutId);
        };
    }, [gameState, isGameStarted, error, isLoading]);

    const resetGame = () => {
        setGameState(initialGameState);
        setGameId(null);
        setPlayer1Type(null);
        setPlayer2Type(null);
        setIsGameStarted(false);
        setError(null);
        setIsLoading(false);
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {!isGameStarted ? (
                <>
                    <GameSetup onStartGame={startGame} isLoading={isLoading} />
                    {gameStats && <StatsDisplay stats={gameStats} />}
                </>
            ) : (
                <Box sx={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center', 
                    gap: 2 
                }}>
                    {player1Type && player2Type && (
                        <GameStatus 
                            gameState={gameState}
                            player1Type={player1Type}
                            player2Type={player2Type}
                        />
                    )}
                    <Box sx={{ position: 'relative' }}>
                        <OthelloBoard 
                            board={gameState.board} 
                            lastMove={gameState.lastMove}
                        />
                        {isLoading && (
                            <Box sx={{
                                position: 'absolute',
                                top: '50%',
                                left: '50%',
                                transform: 'translate(-50%, -50%)',
                                bgcolor: 'rgba(255, 255, 255, 0.8)',
                                borderRadius: '50%',
                                p: 1,
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: 1
                            }}>
                                <CircularProgress />
                                <Typography variant="caption" sx={{ bgcolor: 'rgba(255, 255, 255, 0.9)', px: 1 }}>
                                    思考中...
                                </Typography>
                            </Box>
                        )}
                    </Box>
                    <Button 
                        variant="contained" 
                        color="secondary" 
                        onClick={resetGame}
                        disabled={isLoading}
                        sx={{ mt: 2 }}
                    >
                        新しいゲームを開始
                    </Button>
                    {gameStats && <StatsDisplay stats={gameStats} />}
                </Box>
            )}
        </Container>
    );
}

export default App;