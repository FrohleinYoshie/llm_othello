import React from 'react';
import { Paper, Typography, Stack, Chip } from '@mui/material';
import { GameState, LLMType } from '../types/types';

interface GameStatusProps {
    gameState: GameState;
    player1Type: LLMType;
    player2Type: LLMType;
}

const GameStatus: React.FC<GameStatusProps> = ({ gameState, player1Type, player2Type }) => {
    const getCurrentPlayerName = () => {
        return gameState.currentPlayer === 1 ? player1Type : player2Type;
    };

    const getPlayerColor = (type: LLMType) => {
        switch (type) {
            case 'gemini': return '#4285F4';
            case 'llama': return '#FF9800';
            case 'dify': return '#4CAF50';
            default: return '#666666';
        }
    };

    return (
        <Paper sx={{ p: 2, maxWidth: 400, mx: 'auto', my: 2 }}>
            <Stack spacing={1} alignItems="center">
                {gameState.skipTurn ? (
                    <Typography variant="h6" align="center" color="warning.main">
                        {getCurrentPlayerName()}の手番をスキップ
                    </Typography>
                ) : !gameState.gameOver ? (
                    <>
                        <Typography variant="h6" align="center">
                            現在の手番
                        </Typography>
                        <Chip
                            label={`${getCurrentPlayerName()} (${gameState.currentPlayer === 1 ? '白' : '黒'})`}
                            sx={{ 
                                bgcolor: getPlayerColor(getCurrentPlayerName() as LLMType),
                                color: 'white',
                                fontSize: '1.1rem',
                                py: 1
                            }}
                        />
                    </>
                ) : (
                    <>
                        <Typography variant="h6" align="center">
                            ゲーム終了!
                        </Typography>
                        {gameState.winner === 0 ? (
                            <Typography variant="h5" align="center" color="primary">
                                引き分け
                            </Typography>
                        ) : (
                            <Typography variant="h5" align="center" 
                                sx={{ 
                                    color: getPlayerColor(
                                        gameState.winner === 1 ? player1Type : player2Type
                                    )
                                }}
                            >
                                勝者: {gameState.winner === 1 ? player1Type : player2Type}
                                ({gameState.winner === 1 ? '白' : '黒'})
                            </Typography>
                        )}
                        {gameState.score && (
                            <Stack direction="row" spacing={3} sx={{ mt: 1 }}>
                                <Typography>
                                    白({player1Type}): {gameState.score.white}
                                </Typography>
                                <Typography>
                                    黒({player2Type}): {gameState.score.black}
                                </Typography>
                            </Stack>
                        )}
                    </>
                )}
            </Stack>
        </Paper>
    );
};

export default GameStatus;