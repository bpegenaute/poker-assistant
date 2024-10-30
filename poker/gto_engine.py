from typing import List, Dict, Tuple
import random
from utils.constants import PREMIUM_HANDS, STRONG_HANDS, PLAYABLE_HANDS

class GTOEngine:
    def __init__(self):
        # Enhanced position ranges with more conservative EP ranges
        self.position_ranges = {
            'EP': {'range': 0.08, 'rfi': 0.06, '3bet': 0.04, '4bet': 0.02},  # More conservative
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
            'EP': {'BTN': 0.9, 'CO': 0.9, 'MP': 0.9, 'BB': 0.95, 'SB': 0.9},  # More conservative
            'SB': {'BTN': 0.9, 'CO': 0.9, 'MP': 0.85, 'EP': 0.85, 'BB': 0.9},
            'BB': {'BTN': 1.1, 'CO': 1.05, 'MP': 1.0, 'EP': 0.95, 'SB': 1.15}
        }
        
        # Adjusted action frequencies for more folding in EP
        self.action_frequencies = {
            'EP': {'raise': 0.5, 'call': 0.2, 'fold': 0.3},  # Increased fold frequency
            'MP': {'raise': 0.65, 'call': 0.25, 'fold': 0.1},
            'CO': {'raise': 0.60, 'call': 0.30, 'fold': 0.1},
            'BTN': {'raise': 0.55, 'call': 0.35, 'fold': 0.1},
            'SB': {'raise': 0.45, 'call': 0.35, 'fold': 0.2},
            'BB': {'raise': 0.40, 'call': 0.45, 'fold': 0.15}
        }
        
        # Position-based bet sizing adjustments
        self.position_sizing = {
            'EP': {'pfr': 2.75, 'cbet': 0.6, '3bet': 3.0},  # Larger raises from EP
            'MP': {'pfr': 2.5, 'cbet': 0.65, '3bet': 3.0},
            'CO': {'pfr': 2.25, 'cbet': 0.7, '3bet': 2.75},
            'BTN': {'pfr': 2.25, 'cbet': 0.75, '3bet': 2.5},
            'SB': {'pfr': 3.0, 'cbet': 0.65, '3bet': 3.5},
            'BB': {'pfr': 3.0, 'cbet': 0.6, '3bet': 3.25}
        }

    def is_pocket_pair(self, hand: List[str]) -> Tuple[bool, int]:
        """Check if hand is a pocket pair and return rank"""
        if len(hand) != 2:
            return False, 0
        rank1, rank2 = hand[0][0], hand[1][0]
        if rank1 == rank2:
            ranks = '23456789TJQKA'
            return True, ranks.index(rank1)
        return False, 0

    def calculate_hand_equity(self, hand_strength: float, position: str, vs_position: str = None, 
                            hand: List[str] = None, stack_to_pot: float = None) -> float:
        """Calculate hand equity with additional pocket pair and stack considerations"""
        position_multiplier = self.position_ranges[position]['range']
        
        # Adjust for pocket pairs
        if hand:
            is_pair, pair_rank = self.is_pocket_pair(hand)
            if is_pair:
                # Reduce equity for low pairs in early position
                if position == 'EP' and pair_rank < 7:  # 22-77
                    position_multiplier *= 0.7
                # Adjust based on stack-to-pot ratio for small pairs
                if stack_to_pot and pair_rank < 9:  # 22-88
                    if stack_to_pot > 20:  # Deep stacks increase implied odds
                        position_multiplier *= 1.2
                    elif stack_to_pot < 10:  # Shallow stacks decrease playability
                        position_multiplier *= 0.8
        
        if vs_position and vs_position != position:
            pvp_mult = self.pvp_adjustments[position].get(vs_position, 1.0)
            position_multiplier *= pvp_mult
            
        return min(1.0, hand_strength * (1 + position_multiplier))

    def get_optimal_sizing(self, street: str, pot_size: float, stack: float, position: str) -> float:
        """Calculate GTO-based bet sizing with position consideration"""
        pos_sizes = self.position_sizing[position]
        stack_to_pot = stack / pot_size if pot_size > 0 else float('inf')
        
        if street == "Pre-flop":
            if stack_to_pot < 15:  # Shallow stack adjustments
                return min(pos_sizes['pfr'] * 0.8, stack * 0.1)
            return min(pos_sizes['pfr'], stack * 0.1)
        
        base_sizes = {
            "Flop": (0.5, 0.75),
            "Turn": (0.66, 0.85),
            "River": (0.75, 1.0)
        }
        
        min_size, max_size = base_sizes.get(street, (0.5, 0.75))
        position_adjustment = pos_sizes['cbet'] / 0.65
        
        # Adjust sizing based on stack depth
        if stack_to_pot < 10:
            position_adjustment *= 0.8  # Smaller bets with shallow stacks
        
        optimal_size = random.uniform(min_size, max_size) * pot_size * position_adjustment
        return min(optimal_size, stack)

    def get_gto_action_distribution(self, position: str, hand_strength: float, 
                                  vs_position: str = None, hand: List[str] = None,
                                  stack_to_pot: float = None) -> Dict[str, float]:
        """Get GTO-based action distribution with enhanced pocket pair handling"""
        base_frequencies = self.action_frequencies[position].copy()
        
        # Special handling for pocket pairs
        if hand:
            is_pair, pair_rank = self.is_pocket_pair(hand)
            if is_pair:
                if position == 'EP' and pair_rank < 7:
                    # Significantly reduce raising frequency for small pairs in EP
                    base_frequencies['raise'] *= 0.5
                    base_frequencies['fold'] += base_frequencies['raise'] * 0.5
                    
                if stack_to_pot:
                    if stack_to_pot > 20 and pair_rank < 9:
                        # Increase calling frequency with deep stacks
                        base_frequencies['call'] *= 1.3
                        base_frequencies['fold'] *= 0.7
                    elif stack_to_pot < 10:
                        # Increase folding frequency with shallow stacks
                        base_frequencies['fold'] *= 1.3
                        base_frequencies['call'] *= 0.7
        
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
        """Calculate range strength with enhanced pocket pair considerations"""
        hand_str = ''.join(sorted([card[0] for card in hand]))
        suited = hand[0][1] == hand[1][1]
        hand_str = hand_str + 's' if suited else hand_str
        
        # Special handling for pocket pairs
        is_pair, pair_rank = self.is_pocket_pair(hand)
        if is_pair:
            if pair_rank >= 10:  # TT+
                strength = 1.0
            elif pair_rank >= 7:  # 77-99
                strength = 0.8
            elif pair_rank >= 4:  # 44-66
                strength = 0.6
            else:  # 22-33
                strength = 0.4
                
            # Additional position-based adjustments for pairs
            if position == 'EP':
                strength *= 0.8  # More conservative in EP
            elif position in ['BTN', 'CO']:
                strength *= 1.1  # More playable in late position
        else:
            if hand_str in PREMIUM_HANDS:
                strength = 1.0
            elif hand_str in STRONG_HANDS:
                strength = 0.8
            elif hand_str in PLAYABLE_HANDS:
                strength = 0.6
            else:
                strength = 0.3
            
        position_rfi = self.position_ranges[position]['rfi']
        return min(1.0, strength * (1 + position_rfi))

    def calculate_gto_ev(self, hand_strength: float, pot_size: float, to_call: float,
                        position: str, stack: float, vs_position: str = None,
                        hand: List[str] = None) -> Dict[str, float]:
        """Calculate GTO-adjusted EV with enhanced stack and position considerations"""
        stack_to_pot = stack / pot_size if pot_size > 0 else float('inf')
        position_equity = self.calculate_hand_equity(
            hand_strength, position, vs_position, hand, stack_to_pot
        )
        
        fold_ev = 0
        call_ev = (position_equity * pot_size) - ((1 - position_equity) * to_call)
        
        # Adjust EV calculations for pocket pairs
        if hand:
            is_pair, pair_rank = self.is_pocket_pair(hand)
            if is_pair and pair_rank < 7 and position == 'EP':
                call_ev *= 0.8  # Reduce EV for small pairs in EP
        
        raise_size = self.get_optimal_sizing("Pre-flop", pot_size, stack, position)
        raise_ev = (position_equity * (pot_size + raise_size)) - ((1 - position_equity) * raise_size)
        
        # Stack depth considerations
        if stack_to_pot < 15:
            raise_ev *= 0.9  # Reduce raising EV with shallow stacks
        
        if vs_position:
            pvp_mult = self.pvp_adjustments[position].get(vs_position, 1.0)
            call_ev *= pvp_mult
            raise_ev *= pvp_mult
        
        return {
            'FOLD': fold_ev,
            'CALL': call_ev,
            'RAISE': raise_ev
        }
