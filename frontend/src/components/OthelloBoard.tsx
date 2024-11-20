import React from 'react';
import { styled } from '@mui/material/styles';
import { Box } from '@mui/material';

interface OthelloBoardProps {
    board: number[][];
    lastMove?: [number, number] | null;
}

const BoardContainer = styled('div')`
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 2px;
    background-color: #2f4f4f;
    padding: 8px;
    border-radius: 4px;
    width: 400px;
    height: 400px;
`;

const Cell = styled('div')<{ isLastMove?: boolean }>`
    background-color: ${props => props.isLastMove ? '#3d5f3d' : '#228b22'};
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    transition: background-color 0.3s ease;

    &:hover {
        background-color: ${props => props.isLastMove ? '#4d6f4d' : '#32a132'};
    }
`;

const Piece = styled('div')<{ player: number }>`
    width: 80%;
    height: 80%;
    border-radius: 50%;
    background-color: ${props => props.player === 1 ? 'white' : 'black'};
    box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease-in-out;

    &:hover {
        transform: scale(1.05);
    }
`;

const LastMoveMarker = styled('div')`
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 15px;
    height: 15px;
    border-radius: 50%;
    background-color: rgba(255, 255, 0, 0.5);
    pointer-events: none;
    animation: pulse 1.5s infinite;

    @keyframes pulse {
        0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
        50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.3; }
        100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
    }
`;

const OthelloBoard: React.FC<OthelloBoardProps> = ({ board, lastMove }) => {
    return (
        <BoardContainer>
            {board.map((row, i) => 
                row.map((cell, j) => {
                    const isLastMove = !!lastMove && lastMove[0] === i && lastMove[1] === j;
                    return (
                        <Cell key={`${i}-${j}`} isLastMove={isLastMove}>
                            {cell !== 0 && (
                                <Box sx={{ 
                                    position: 'relative', 
                                    width: '100%', 
                                    height: '100%', 
                                    display: 'flex', 
                                    alignItems: 'center', 
                                    justifyContent: 'center'
                                }}>
                                    <Piece player={cell} />
                                    {isLastMove && <LastMoveMarker />}
                                </Box>
                            )}
                        </Cell>
                    );
                })
            )}
        </BoardContainer>
    );
};

export default OthelloBoard;