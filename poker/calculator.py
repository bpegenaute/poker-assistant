from typing import Dict
import numpy as np

class PokerCalculator:
    def calculate_pot_odds(self, to_call: float, pot_size: float) -> float:
        """Calculate pot odds"""
        if pot_size == 0 or to_call == 0:
            return 0.0
        return to_call / (pot_size + to_call)

    def calculate_ev(self, win_probability: float, pot_size: float, to_call: float) -> float:
        """Calculate expected value of a call"""
        return (win_probability * pot_size) - ((1 - win_probability) * to_call)

    def position_multiplier(self, position: str) -> float:
        """Get multiplier based on position"""
        position_weights = {
            'BTN': 1.2,
            'CO': 1.1,
            'MP': 0.9,
            'EP': 0.8,
            'BB': 0.85,
            'SB': 0.75
        }
        return position_weights.get(position, 1.0)
