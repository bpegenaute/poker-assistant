from typing import Dict, List
from .evaluator import HandEvaluator
from .calculator import PokerCalculator
from .gto_engine import GTOEngine

class RecommendationEngine:
    def __init__(self):
        self.evaluator = HandEvaluator()
        self.calculator = PokerCalculator()
        self.gto_engine = GTOEngine()

    def get_recommendation(
        self,
        hole_cards: List[str],
        community_cards: List[str],
        position: str,
        pot_size: float,
        to_call: float,
        stack_size: float
    ) -> Dict:
        # Calculate hand strength and GTO-adjusted equity
        hand_strength = self.evaluator.evaluate_hand_strength(hole_cards, community_cards)
        range_strength = self.gto_engine.get_range_strength(hole_cards, position)
        adjusted_strength = (hand_strength + range_strength) / 2
        
        # Calculate pot odds and position-adjusted equity
        pot_odds = self.calculator.calculate_pot_odds(to_call, pot_size)
        equity = self.gto_engine.calculate_hand_equity(adjusted_strength, position)
        
        # Get GTO-based action frequencies
        action_distribution = self.gto_engine.get_gto_action_distribution(position, adjusted_strength)
        
        # Calculate EVs for each action
        evs = self.gto_engine.calculate_gto_ev(
            adjusted_strength, pot_size, to_call, position, stack_size
        )
        
        # Determine optimal action based on GTO principles
        optimal_action = max(evs.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence based on EV difference and action frequencies
        max_ev = max(evs.values())
        ev_range = max_ev - min(evs.values()) if max_ev > 0 else 1
        confidence = min(1.0, (max_ev / ev_range) * action_distribution[optimal_action.lower()])

        return {
            'action': optimal_action,
            'confidence': confidence,
            'reasoning': self._generate_reasoning(
                optimal_action,
                hand_strength,
                pot_odds,
                evs[optimal_action],
                position,
                action_distribution,
                range_strength
            )
        }

    def _generate_reasoning(
        self,
        action: str,
        hand_strength: float,
        pot_odds: float,
        ev: float,
        position: str,
        action_freq: Dict[str, float],
        range_strength: float
    ) -> str:
        return f"""
        GTO Analysis:
        - Raw hand strength: {hand_strength:.2%}
        - Range strength: {range_strength:.2%}
        - Pot odds: {pot_odds:.2%}
        - Expected value: ${ev:.2f}
        - Position: {position}
        
        Recommended frequencies in this spot:
        - Raise: {action_freq['raise']:.1%}
        - Call: {action_freq['call']:.1%}
        - Fold: {action_freq['fold']:.1%}
        
        The {action} recommendation is optimal according to GTO principles, considering your position, 
        hand strength relative to your range, and the mathematical expectation of each action.
        """
