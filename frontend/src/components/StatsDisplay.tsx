import React from 'react';
import { 
    Paper, 
    Typography, 
    Grid, 
    Box,
    LinearProgress,
    Chip 
} from '@mui/material';
import { GameStats } from '../types/types';

interface StatsDisplayProps {
    stats: GameStats;
}

const StatsDisplay: React.FC<StatsDisplayProps> = ({ stats }) => {
    const modelColors = {
        gemini: '#4285F4',
        llama: '#FF9800',
        dify: '#4CAF50'
    };

    return (
        <Paper sx={{ p: 3, mt: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom align="center">
                モデル対戦成績
            </Typography>
            <Grid container spacing={3}>
                {Object.entries(stats).map(([model, data]) => (
                    <Grid item xs={12} key={model}>
                        <Box sx={{ mb: 2 }}>
                            <Box sx={{ 
                                display: 'flex', 
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                mb: 1
                            }}>
                                <Typography variant="subtitle1" sx={{ 
                                    color: modelColors[model as keyof typeof modelColors],
                                    fontWeight: 'bold'
                                }}>
                                    {model.toUpperCase()}
                                </Typography>
                                <Chip
                                    label={data.model_trained ? "学習済み" : "未学習"}
                                    color={data.model_trained ? "success" : "default"}
                                    size="small"
                                />
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                <Typography variant="body2" color="text.secondary">
                                    対戦数: {data.games_played}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    勝利数: {data.wins}
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Box sx={{ width: '100%', mr: 1 }}>
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={data.win_rate} 
                                        sx={{ 
                                            height: 8, 
                                            borderRadius: 4,
                                            backgroundColor: '#e0e0e0',
                                            '& .MuiLinearProgress-bar': {
                                                backgroundColor: modelColors[model as keyof typeof modelColors],
                                                borderRadius: 4
                                            }
                                        }}
                                    />
                                </Box>
                                <Typography 
                                    variant="body2" 
                                    color="text.secondary"
                                    sx={{ minWidth: 60 }}
                                >
                                    {data.win_rate.toFixed(1)}%
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>
                ))}
            </Grid>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2, textAlign: 'center' }}>
                ※ 勝率は直近の対戦結果から計算されています
            </Typography>
        </Paper>
    );
};

export default StatsDisplay;