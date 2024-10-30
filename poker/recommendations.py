from typing import Dict, List
from .evaluator import HandEvaluator
from .calculator import PokerCalculator

class RecommendationEngine:
    def __init__(self):
        self.evaluator = HandEvaluator()
        self.calculator = PokerCalculator()

    def get_recommendation(
        self,
        hole_cards: List[str],
        community_cards: List[str],
        position: str,
        pot_size: float,
        to_call: float,
        stack_size: float
    ) -> Dict:
        # Calculate hand strength
        hand_strength = self.evaluator.evaluate_hand_strength(hole_cards, community_cards)
        
        # Calculate pot odds
        pot_odds = self.calculator.calculate_pot_odds(to_call, pot_size)
        
        # Position adjustment
        position_mult = self.calculator.position_multiplier(position)
        adjusted_strength = hand_strength * position_mult
        
        # Calculate EV
        ev = self.calculator.calculate_ev(adjusted_strength, pot_size, to_call)
        
        # Generate recommendation
        action = self._determine_action(adjusted_strength, pot_odds, ev, stack_size, to_call)
        
        return {
            'action': action['action'],
            'confidence': action['confidence'],
            'reasoning': self._generate_reasoning(
                action['action'],
                hand_strength,
                pot_odds,
                ev,
                position
            )
        }

    def _determine_action(
        self,
        strength: float,
        pot_odds: float,
        ev: float,
        stack: float,
        to_call: float
    ) -> Dict:
        if strength > pot_odds * 1.5 and ev > 0:
            return {
                'action': 'RAISE',
                'confidence': min(1.0, strength * 1.5)
            }
        elif strength > pot_odds and ev > 0:
            return {
                'action': 'CALL',
                'confidence': min(1.0, strength * 1.2)
            }
        else:
            return {
                'action': 'FOLD',
                'confidence': min(1.0, (1 - strength) * 1.2)
            }

    def _generate_reasoning(
        self,
        action: str,
        strength: float,
        pot_odds: float,
        ev: float,
        position: str
    ) -> str:
        return f"""
        Recommendation based on:
        - Hand strength: {strength:.2%}
        - Pot odds: {pot_odds:.2%}
        - Expected value: ${ev:.2f}
        - Position: {position}
        
        This {action} recommendation considers your position and the mathematical expectation of the situation.
        """
