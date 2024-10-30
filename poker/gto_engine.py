from typing import List, Dict, Tuple
import random
from utils.constants import PREMIUM_HANDS, STRONG_HANDS, PLAYABLE_HANDS

class GTOEngine:
    def __init__(self):
        self.position_ranges = {
            'EP': 0.10,  # Tightest range
            'MP': 0.15,
            'CO': 0.25,
            'BTN': 0.35, # Widest range
            'SB': 0.20,
            'BB': 0.30
        }
        
        self.action_frequencies = {
            'EP': {'raise': 0.7, 'call': 0.2, 'fold': 0.1},
            'MP': {'raise': 0.65, 'call': 0.25, 'fold': 0.1},
            'CO': {'raise': 0.60, 'call': 0.30, 'fold': 0.1},
            'BTN': {'raise': 0.55, 'call': 0.35, 'fold': 0.1},
            'SB': {'raise': 0.45, 'call': 0.35, 'fold': 0.2},
            'BB': {'raise': 0.40, 'call': 0.45, 'fold': 0.15}
        }

    def calculate_hand_equity(self, hand_strength: float, position: str) -> float:
        """Calculate hand equity considering position and hand strength"""
        position_multiplier = self.position_ranges[position]
        return min(1.0, hand_strength * (1 + position_multiplier))

    def get_optimal_sizing(self, street: str, pot_size: float, stack: float) -> float:
        """Calculate GTO-based bet sizing"""
        if street == "Pre-flop":
            return min(3.0, stack * 0.1)  # Standard 3bb open
        
        # Post-flop sizings
        pot_percentages = {
            "Flop": (0.5, 0.75),  # 50-75% pot
            "Turn": (0.66, 0.85),  # 66-85% pot
            "River": (0.75, 1.0)   # 75-100% pot
        }
        
        min_size, max_size = pot_percentages.get(street, (0.5, 0.75))
        optimal_size = random.uniform(min_size, max_size) * pot_size
        return min(optimal_size, stack)

    def get_gto_action_distribution(self, position: str, hand_strength: float) -> Dict[str, float]:
        """Get GTO-based action distribution based on position and hand strength"""
        base_frequencies = self.action_frequencies[position].copy()
        
        # Adjust frequencies based on hand strength
        if hand_strength > 0.8:  # Very strong hands
            base_frequencies['raise'] += 0.2
            base_frequencies['call'] -= 0.1
            base_frequencies['fold'] -= 0.1
        elif hand_strength > 0.6:  # Strong hands
            base_frequencies['raise'] += 0.1
            base_frequencies['call'] += 0.1
            base_frequencies['fold'] -= 0.2
        elif hand_strength < 0.3:  # Weak hands
            base_frequencies['raise'] -= 0.2
            base_frequencies['call'] -= 0.1
            base_frequencies['fold'] += 0.3
            
        # Normalize frequencies
        total = sum(base_frequencies.values())
        return {k: v/total for k, v in base_frequencies.items()}

    def get_range_strength(self, hand: List[str], position: str) -> float:
        """Calculate how well a hand fits into the GTO range for the position"""
        hand_str = ''.join(sorted([card[0] for card in hand]))
        suited = hand[0][1] == hand[1][1]
        hand_str = hand_str + 's' if suited else hand_str
        
        if hand_str in PREMIUM_HANDS:
            return 1.0
        elif hand_str in STRONG_HANDS:
            return 0.8
        elif hand_str in PLAYABLE_HANDS:
            return 0.6
        else:
            return 0.3

    def calculate_gto_ev(self, hand_strength: float, pot_size: float, to_call: float,
                        position: str, stack: float) -> Dict[str, float]:
        """Calculate GTO-adjusted EV for each action"""
        position_equity = self.calculate_hand_equity(hand_strength, position)
        
        fold_ev = 0
        call_ev = (position_equity * pot_size) - ((1 - position_equity) * to_call)
        
        # Calculate raise EV
        raise_size = self.get_optimal_sizing("Pre-flop", pot_size, stack)
        raise_ev = (position_equity * (pot_size + raise_size)) - ((1 - position_equity) * raise_size)
        
        return {
            'FOLD': fold_ev,
            'CALL': call_ev,
            'RAISE': raise_ev
        }
