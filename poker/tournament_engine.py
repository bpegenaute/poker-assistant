from typing import Dict, Optional, Tuple
import math

class TournamentEngine:
    def __init__(self):
        # Tournament stage multipliers for adjusting ranges
        self.stage_multipliers = {
            'early': {'range': 0.8, 'aggression': 0.7},
            'middle': {'range': 1.0, 'aggression': 1.0},
            'bubble': {'range': 0.6, 'aggression': 1.3},
            'in_money': {'range': 1.2, 'aggression': 1.1},
            'final_table': {'range': 1.1, 'aggression': 1.2}
        }
        
        # Stack pressure thresholds in big blinds
        self.stack_pressure = {
            'critical': 10,  # Push/fold territory
            'shallow': 20,   # Very tight play
            'medium': 40,    # Standard play
            'deep': 100      # More room for play
        }

    def calculate_m_ratio(self, stack: float, total_blinds: float) -> float:
        """Calculate Harrington's M-ratio (stack size relative to blinds)"""
        return stack / total_blinds if total_blinds > 0 else float('inf')

    def calculate_icm_pressure(self, stack: float, avg_stack: float, 
                             players_left: int, in_money_spots: int) -> float:
        """Calculate ICM pressure factor"""
        if players_left <= in_money_spots:
            # Already in the money, less pressure
            return 0.7
        elif players_left - in_money_spots <= 3:
            # Bubble pressure
            if stack < avg_stack:
                return 0.4  # High pressure on short stacks
            else:
                return 1.2  # Can apply pressure with big stack
        else:
            # Normal tournament play
            return 1.0

    def get_tournament_stage(self, players_left: int, total_players: int) -> str:
        """Determine tournament stage based on remaining players"""
        percentage_left = players_left / total_players
        
        if percentage_left > 0.75:
            return 'early'
        elif percentage_left > 0.3:
            return 'middle'
        elif percentage_left > 0.15:
            return 'bubble'
        elif players_left > 9:
            return 'in_money'
        else:
            return 'final_table'

    def adjust_ranges_for_tournament(self, base_range: float, stack: float,
                                   total_blinds: float, players_left: int,
                                   total_players: int, avg_stack: float,
                                   in_money_spots: int) -> Tuple[float, Dict[str, float]]:
        """Adjust playing ranges based on tournament factors"""
        m_ratio = self.calculate_m_ratio(stack, total_blinds)
        stage = self.get_tournament_stage(players_left, total_players)
        icm_pressure = self.calculate_icm_pressure(stack, avg_stack, players_left, in_money_spots)
        
        # Get stage multipliers
        stage_mult = self.stage_multipliers[stage]
        
        # Stack depth adjustments
        if m_ratio < self.stack_pressure['critical']:
            stack_mult = 0.5  # Push/fold mode
        elif m_ratio < self.stack_pressure['shallow']:
            stack_mult = 0.7  # Very tight
        elif m_ratio < self.stack_pressure['medium']:
            stack_mult = 0.9  # Slightly tight
        else:
            stack_mult = 1.0  # Normal play
            
        # Calculate final adjusted range
        adjusted_range = base_range * stage_mult['range'] * stack_mult * icm_pressure
        
        # Additional tournament-specific adjustments
        adjustments = {
            'push_fold_threshold': 15 if m_ratio < self.stack_pressure['critical'] else 0,
            'bubble_factor': 1.5 if stage == 'bubble' else 1.0,
            'icm_pressure': icm_pressure,
            'stage_aggression': stage_mult['aggression']
        }
        
        return min(1.0, max(0.0, adjusted_range)), adjustments

    def get_tournament_advice(self, stage: str, m_ratio: float, 
                            icm_pressure: float) -> str:
        """Get specific tournament stage advice"""
        if m_ratio < self.stack_pressure['critical']:
            return (
                "PUSH/FOLD STRATEGY: With a critical stack (under 10BB), "
                "focus on push/fold decisions. Look for spots to shove with any "
                "reasonable hand when folded to you."
            )
        elif stage == 'bubble':
            if icm_pressure < 0.7:
                return (
                    "BUBBLE STRATEGY (Short Stack): Extremely selective with "
                    "marginal hands. Only play premium hands unless desperate."
                )
            else:
                return (
                    "BUBBLE STRATEGY (Big Stack): Apply maximum pressure on "
                    "medium stacks. Target players who are trying to sneak into "
                    "the money."
                )
        elif stage == 'final_table':
            return (
                "FINAL TABLE STRATEGY: Pay close attention to pay jumps and stack "
                "sizes. Look for spots to ladder up when short and apply pressure "
                "when deep stacked."
            )
        else:
            return (
                "STANDARD TOURNAMENT STRATEGY: Maintain healthy stack by picking "
                "good spots. Balance aggression with conservation based on stack size."
            )
