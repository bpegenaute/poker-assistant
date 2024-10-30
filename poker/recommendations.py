from typing import Dict, List, Optional
from .evaluator import HandEvaluator
from .calculator import PokerCalculator
from .gto_engine import GTOEngine
from .tournament_engine import TournamentEngine

class RecommendationEngine:
    def __init__(self):
        self.evaluator = HandEvaluator()
        self.calculator = PokerCalculator()
        self.gto_engine = GTOEngine()
        self.tournament_engine = TournamentEngine()

    def get_recommendation(
        self,
        hole_cards: List[str],
        community_cards: List[str],
        position: str,
        pot_size: float,
        to_call: float,
        stack_size: float,
        vs_position: str = None,
        tournament_info: Optional[Dict] = None
    ) -> Dict:
        # Calculate base hand strength and GTO-adjusted equity
        hand_strength = self.evaluator.evaluate_hand_strength(hole_cards, community_cards)
        range_strength = self.gto_engine.get_range_strength(hole_cards, position)
        adjusted_strength = (hand_strength + range_strength) / 2

        # Apply tournament adjustments if in tournament mode
        tournament_adjustments = None
        if tournament_info:
            adjusted_strength, tournament_adjustments = self.tournament_engine.adjust_ranges_for_tournament(
                adjusted_strength,
                stack_size,
                tournament_info.get('total_blinds', 1.0),
                tournament_info.get('players_left', 0),
                tournament_info.get('total_players', 0),
                tournament_info.get('avg_stack', stack_size),
                tournament_info.get('in_money_spots', 0)
            )

        # Calculate pot odds and position-adjusted equity
        pot_odds = self.calculator.calculate_pot_odds(to_call, pot_size)
        equity = self.gto_engine.calculate_hand_equity(adjusted_strength, position, vs_position)

        # Get GTO-based action frequencies with position considerations
        action_distribution = self.gto_engine.get_gto_action_distribution(
            position, adjusted_strength, vs_position
        )

        # Calculate EVs for each action with enhanced position logic
        evs = self.gto_engine.calculate_gto_ev(
            adjusted_strength, pot_size, to_call, position, stack_size, vs_position
        )

        # Determine optimal action based on GTO principles
        optimal_action = max(evs.items(), key=lambda x: x[1])[0]

        # Calculate confidence based on EV difference and action frequencies
        max_ev = max(evs.values())
        ev_range = max_ev - min(evs.values()) if max_ev > 0 else 1
        confidence = min(1.0, (max_ev / ev_range) * action_distribution[optimal_action.lower()])

        # Get tournament-specific advice if applicable
        tournament_advice = ""
        if tournament_info and tournament_adjustments:
            stage = self.tournament_engine.get_tournament_stage(
                tournament_info['players_left'],
                tournament_info['total_players']
            )
            m_ratio = self.tournament_engine.calculate_m_ratio(
                stack_size,
                tournament_info['total_blinds']
            )
            tournament_advice = self.tournament_engine.get_tournament_advice(
                stage,
                m_ratio,
                tournament_adjustments['icm_pressure']
            )

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
                range_strength,
                vs_position,
                tournament_info,
                tournament_adjustments,
                tournament_advice
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
        range_strength: float,
        vs_position: str = None,
        tournament_info: Optional[Dict] = None,
        tournament_adjustments: Optional[Dict] = None,
        tournament_advice: str = ""
    ) -> str:
        position_context = f"vs {vs_position}" if vs_position else "in general"
        
        position_analysis = f"""
        Position Analysis ({position} {position_context}):
        - Position Range: {self.gto_engine.position_ranges[position]['range']:.2%}
        - RFI Frequency: {self.gto_engine.position_ranges[position]['rfi']:.2%}
        - 3-Bet Range: {self.gto_engine.position_ranges[position]['3bet']:.2%}
        """
        
        if vs_position:
            pvp_mult = self.gto_engine.pvp_adjustments[position].get(vs_position, 1.0)
            position_analysis += f"- Position vs Position Adjustment: {pvp_mult:.2f}x\n"

        tournament_section = ""
        if tournament_info and tournament_adjustments:
            m_ratio = self.tournament_engine.calculate_m_ratio(
                tournament_info.get('stack_size', 0),
                tournament_info.get('total_blinds', 1)
            )
            tournament_section = f"""
            Tournament Considerations:
            - M-Ratio: {m_ratio:.1f}
            - ICM Pressure: {tournament_adjustments['icm_pressure']:.2f}
            - Bubble Factor: {tournament_adjustments['bubble_factor']:.2f}
            - Stage Aggression: {tournament_adjustments['stage_aggression']:.2f}
            
            Tournament Advice:
            {tournament_advice}
            """

        return f"""
        GTO Analysis:
        - Raw hand strength: {hand_strength:.2%}
        - Range strength: {range_strength:.2%}
        - Pot odds: {pot_odds:.2%}
        - Expected value: ${ev:.2f}
        
        {position_analysis}
        
        Recommended frequencies in this spot:
        - Raise: {action_freq['raise']:.1%}
        - Call: {action_freq['call']:.1%}
        - Fold: {action_freq['fold']:.1%}
        
        {tournament_section}
        
        The {action} recommendation is optimal according to GTO principles, considering your position, 
        hand strength relative to your range, and the mathematical expectation of each action.
        """
