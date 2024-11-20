import React, { useState } from 'react';
import { 
    Button,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
    Stack,
    Typography,
    SelectChangeEvent
} from '@mui/material';
import { LLMType } from '../types/types';

interface GameSetupProps {
    onStartGame: (player1: LLMType, player2: LLMType) => void;
    isLoading?: boolean;
}

const GameSetup: React.FC<GameSetupProps> = ({ onStartGame, isLoading = false }) => {
    const [player1, setPlayer1] = useState<LLMType>('gemini');
    const [player2, setPlayer2] = useState<LLMType>('llama');

    const handlePlayer1Change = (event: SelectChangeEvent) => {
        setPlayer1(event.target.value as LLMType);
    };

    const handlePlayer2Change = (event: SelectChangeEvent) => {
        setPlayer2(event.target.value as LLMType);
    };

    return (
        <Stack spacing={4} sx={{ maxWidth: 400, mx: 'auto', p: 3 }}>
            <Typography variant="h4" align="center">
                LLM オセロバトル
            </Typography>

            <FormControl fullWidth>
                <InputLabel>プレイヤー1 (白)</InputLabel>
                <Select
                    value={player1}
                    label="プレイヤー1 (白)"
                    onChange={handlePlayer1Change}
                    disabled={isLoading}
                >
                    <MenuItem value="gemini">Gemini</MenuItem>
                    <MenuItem value="llama">Llama</MenuItem>
                    <MenuItem value="dify">Dify</MenuItem>
                </Select>
            </FormControl>

            <FormControl fullWidth>
                <InputLabel>プレイヤー2 (黒)</InputLabel>
                <Select
                    value={player2}
                    label="プレイヤー2 (黒)"
                    onChange={handlePlayer2Change}
                    disabled={isLoading}
                >
                    <MenuItem value="gemini">Gemini</MenuItem>
                    <MenuItem value="llama">Llama</MenuItem>
                    <MenuItem value="dify">Dify</MenuItem>
                </Select>
            </FormControl>

            <Button 
                variant="contained" 
                size="large"
                onClick={() => onStartGame(player1, player2)}
                disabled={isLoading}
            >
                {isLoading ? '準備中...' : 'ゲーム開始'}
            </Button>
        </Stack>
    );
};

export default GameSetup;