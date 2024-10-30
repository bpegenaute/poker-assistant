from typing import List, Tuple
import numpy as np

class HandEvaluator:
    def __init__(self):
        self.ranks = '23456789TJQKA'
        self.suits = 'cdhs'

    def evaluate_hand_strength(self, hole_cards: List[str], community_cards: List[str]) -> float:
        """Calculate relative hand strength (0-1)"""
        if not hole_cards:
            return 0.0
            
        total_cards = hole_cards + (community_cards if community_cards else [])
        
        # Basic hand strength calculation
        # This is a simplified version - in production you'd want more sophisticated evaluation
        hand_value = 0
        for card in total_cards:
            rank = card[0]
            hand_value += self.ranks.index(rank)
        
        return min(1.0, hand_value / (len(total_cards) * 12))

    def calculate_hand_potential(self, hole_cards: List[str], community_cards: List[str]) -> Tuple[float, float]:
        """Calculate positive and negative potential"""
        if len(community_cards) >= 5:
            return (0.0, 0.0)
            
        # Simplified potential calculation
        cards_to_come = 5 - len(community_cards)
        positive_potential = 0.4 * cards_to_come  # Simplified approximation
        negative_potential = 0.3 * cards_to_come
        
        return (positive_potential, negative_potential)
