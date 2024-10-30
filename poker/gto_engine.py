from typing import List, Dict, Tuple
import random
from utils.constants import PREMIUM_HANDS, STRONG_HANDS, PLAYABLE_HANDS

class GTOEngine:
    def __init__(self):
        # Enhanced position ranges with more granularity
        self.position_ranges = {
            'EP': {'range': 0.10, 'rfi': 0.08, '3bet': 0.05, '4bet': 0.03},
            'MP': {'range': 0.15, 'rfi': 0.12, '3bet': 0.07, '4bet': 0.04},
            'CO': {'range': 0.25, 'rfi': 0.22, '3bet': 0.12, '4bet': 0.06},
            'BTN': {'range': 0.35, 'rfi': 0.32, '3bet': 0.15, '4bet': 0.08},
            'SB': {'range': 0.20, 'rfi': 0.18, '3bet': 0.13, '4bet': 0.07},
            'BB': {'range': 0.30, 'rfi': 0.25, '3bet': 0.14, '4bet': 0.06}
        }
        
        # Position vs Position adjustments
        self.pvp_adjustments = {
            'BTN': {'BB': 1.2, 'SB': 1.15, 'CO': 0.9, 'MP': 0.85, 'EP': 0.8},
            'CO': {'BTN': 1.1, 'BB': 1.15, 'SB': 1.1, 'MP': 0.9, 'EP': 0.85},
            'MP': {'BTN': 1.05, 'CO': 1.05, 'BB': 1.1, 'SB': 1.05, 'EP': 0.9},
            'EP': {'BTN': 1.0, 'CO': 1.0, 'MP': 1.0, 'BB': 1.05, 'SB': 1.0},
            'SB': {'BTN': 0.9, 'CO': 0.9, 'MP': 0.85, 'EP': 0.85, 'BB': 0.9},
            'BB': {'BTN': 1.1, 'CO': 1.05, 'MP': 1.0, 'EP': 0.95, 'SB': 1.15}
        }
        
        # Enhanced action frequencies with position consideration
        self.action_frequencies = {
            'EP': {'raise': 0.7, 'call': 0.2, 'fold': 0.1},
            'MP': {'raise': 0.65, 'call': 0.25, 'fold': 0.1},
            'CO': {'raise': 0.60, 'call': 0.30, 'fold': 0.1},
            'BTN': {'raise': 0.55, 'call': 0.35, 'fold': 0.1},
            'SB': {'raise': 0.45, 'call': 0.35, 'fold': 0.2},
            'BB': {'raise': 0.40, 'call': 0.45, 'fold': 0.15}
        }
        
        # Position-based bet sizing adjustments
        self.position_sizing = {
            'EP': {'pfr': 2.5, 'cbet': 0.6, '3bet': 3.0},
            'MP': {'pfr': 2.5, 'cbet': 0.65, '3bet': 3.0},
            'CO': {'pfr': 2.25, 'cbet': 0.7, '3bet': 2.75},
            'BTN': {'pfr': 2.25, 'cbet': 0.75, '3bet': 2.5},
            'SB': {'pfr': 3.0, 'cbet': 0.65, '3bet': 3.5},
            'BB': {'pfr': 3.0, 'cbet': 0.6, '3bet': 3.25}
        }

    def calculate_hand_equity(self, hand_strength: float, position: str, vs_position: str = None) -> float:
        """Calculate hand equity considering position and hand strength with position vs position adjustment"""
        position_multiplier = self.position_ranges[position]['range']
        
        if vs_position and vs_position != position:
            pvp_mult = self.pvp_adjustments[position].get(vs_position, 1.0)
            position_multiplier *= pvp_mult
            
        return min(1.0, hand_strength * (1 + position_multiplier))

    def get_optimal_sizing(self, street: str, pot_size: float, stack: float, position: str) -> float:
        """Calculate GTO-based bet sizing with position consideration"""
        pos_sizes = self.position_sizing[position]
        
        if street == "Pre-flop":
            return min(pos_sizes['pfr'], stack * 0.1)
        
        # Post-flop sizings adjusted by position
        base_sizes = {
            "Flop": (0.5, 0.75),
            "Turn": (0.66, 0.85),
            "River": (0.75, 1.0)
        }
        
        min_size, max_size = base_sizes.get(street, (0.5, 0.75))
        position_adjustment = pos_sizes['cbet'] / 0.65  # Normalize to average cbet size
        
        optimal_size = random.uniform(min_size, max_size) * pot_size * position_adjustment
        return min(optimal_size, stack)

    def get_gto_action_distribution(self, position: str, hand_strength: float, vs_position: str = None) -> Dict[str, float]:
        """Get GTO-based action distribution based on position and hand strength"""
        base_frequencies = self.action_frequencies[position].copy()
        
        # Adjust frequencies based on position vs position
        if vs_position:
            pvp_mult = self.pvp_adjustments[position].get(vs_position, 1.0)
            if pvp_mult > 1:
                base_frequencies['raise'] *= pvp_mult
                base_frequencies['fold'] /= pvp_mult
            else:
                base_frequencies['raise'] /= (2 - pvp_mult)
                base_frequencies['fold'] *= (2 - pvp_mult)
        
        # Adjust frequencies based on hand strength
        if hand_strength > 0.8:
            base_frequencies['raise'] += 0.2
            base_frequencies['call'] -= 0.1
            base_frequencies['fold'] -= 0.1
        elif hand_strength > 0.6:
            base_frequencies['raise'] += 0.1
            base_frequencies['call'] += 0.1
            base_frequencies['fold'] -= 0.2
        elif hand_strength < 0.3:
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
            strength = 1.0
        elif hand_str in STRONG_HANDS:
            strength = 0.8
        elif hand_str in PLAYABLE_HANDS:
            strength = 0.6
        else:
            strength = 0.3
            
        # Adjust strength based on position's RFI range
        position_rfi = self.position_ranges[position]['rfi']
        return min(1.0, strength * (1 + position_rfi))

    def calculate_gto_ev(self, hand_strength: float, pot_size: float, to_call: float,
                        position: str, stack: float, vs_position: str = None) -> Dict[str, float]:
        """Calculate GTO-adjusted EV for each action with position considerations"""
        position_equity = self.calculate_hand_equity(hand_strength, position, vs_position)
        
        fold_ev = 0
        call_ev = (position_equity * pot_size) - ((1 - position_equity) * to_call)
        
        # Calculate raise EV with position-based sizing
        raise_size = self.get_optimal_sizing("Pre-flop", pot_size, stack, position)
        raise_ev = (position_equity * (pot_size + raise_size)) - ((1 - position_equity) * raise_size)
        
        # Adjust EVs based on position vs position
        if vs_position:
            pvp_mult = self.pvp_adjustments[position].get(vs_position, 1.0)
            call_ev *= pvp_mult
            raise_ev *= pvp_mult
        
        return {
            'FOLD': fold_ev,
            'CALL': call_ev,
            'RAISE': raise_ev
        }
