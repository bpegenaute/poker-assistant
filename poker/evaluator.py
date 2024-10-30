from typing import List, Tuple, Dict
from collections import Counter
import itertools

class HandEvaluator:
    def __init__(self):
        self.ranks = '23456789TJQKA'
        self.suits = 'cdhs'
        # Hand rankings from strongest to weakest
        self.hand_rankings = [
            'straight_flush', 'four_kind', 'full_house', 'flush',
            'straight', 'three_kind', 'two_pair', 'pair', 'high_card'
        ]

    def _parse_card(self, card: str) -> Tuple[int, str]:
        """Convert card string to (rank_value, suit)"""
        rank, suit = card[0], card[1]
        return self.ranks.index(rank), suit

    def _get_hand_rank_value(self, hand_type: str) -> float:
        """Get base value for hand type"""
        base_values = {
            'straight_flush': 0.95,
            'four_kind': 0.90,
            'full_house': 0.85,
            'flush': 0.80,
            'straight': 0.75,
            'three_kind': 0.70,
            'two_pair': 0.65,
            'pair': 0.50,
            'high_card': 0.30
        }
        return base_values.get(hand_type, 0.0)

    def _detect_straight(self, rank_values: List[int]) -> bool:
        """Detect if the ranks form a straight"""
        sorted_ranks = sorted(set(rank_values))
        if len(sorted_ranks) < 5:
            return False
        
        # Check for regular straight
        for i in range(len(sorted_ranks) - 4):
            if sorted_ranks[i+4] - sorted_ranks[i] == 4:
                return True
                
        # Check for Ace-low straight (A,2,3,4,5)
        if 12 in rank_values:  # If Ace is present
            low_straight = [0, 1, 2, 3, 12]  # 2,3,4,5,A
            if all(r in rank_values for r in low_straight):
                return True
        return False

    def _detect_flush(self, suits: List[str]) -> bool:
        """Detect if the suits form a flush"""
        suit_counts = Counter(suits)
        return max(suit_counts.values()) >= 5

    def evaluate_hand_type(self, cards: List[str]) -> Tuple[str, List[int]]:
        """Evaluate the type of poker hand"""
        if not cards:
            return 'high_card', []
            
        rank_values = []
        suits = []
        for card in cards:
            rank_val, suit = self._parse_card(card)
            rank_values.append(rank_val)
            suits.append(suit)
            
        # Count frequencies of ranks
        rank_counts = Counter(rank_values)
        max_rank_count = max(rank_counts.values())
        
        # Check for straight flush
        if self._detect_flush(suits) and self._detect_straight(rank_values):
            return 'straight_flush', sorted(rank_values, reverse=True)
            
        # Four of a kind
        if max_rank_count == 4:
            return 'four_kind', [r for r, c in rank_counts.items() if c == 4]
            
        # Full house
        if max_rank_count == 3 and len([c for c in rank_counts.values() if c >= 2]) >= 2:
            return 'full_house', [r for r, c in rank_counts.items() if c == 3]
            
        # Flush
        if self._detect_flush(suits):
            return 'flush', sorted(rank_values, reverse=True)[:5]
            
        # Straight
        if self._detect_straight(rank_values):
            return 'straight', sorted(rank_values, reverse=True)[:5]
            
        # Three of a kind
        if max_rank_count == 3:
            return 'three_kind', [r for r, c in rank_counts.items() if c == 3]
            
        # Two pair
        pairs = [r for r, c in rank_counts.items() if c == 2]
        if len(pairs) >= 2:
            return 'two_pair', sorted(pairs, reverse=True)[:2]
            
        # One pair
        if max_rank_count == 2:
            return 'pair', [r for r, c in rank_counts.items() if c == 2]
            
        # High card
        return 'high_card', sorted(rank_values, reverse=True)[:5]

    def evaluate_hand_strength(self, hole_cards: List[str], community_cards: List[str]) -> float:
        """Calculate relative hand strength (0-1)"""
        if not hole_cards:
            return 0.0
            
        total_cards = hole_cards + (community_cards if community_cards else [])
        hand_type, key_ranks = self.evaluate_hand_type(total_cards)
        
        # Base strength from hand type
        strength = self._get_hand_rank_value(hand_type)
        
        # Adjust strength based on key ranks
        if key_ranks:
            rank_adjustment = sum(r / len(self.ranks) for r in key_ranks) / len(key_ranks)
            strength += (1 - strength) * rank_adjustment * 0.2
        
        # Adjust for hole cards involvement
        hole_ranks = set(card[0] for card in hole_cards)
        key_card_ranks = set(self.ranks[r] for r in key_ranks)
        if not key_card_ranks.intersection(hole_ranks):
            strength *= 0.7  # Significantly reduce strength if hole cards aren't involved
            
        return min(1.0, max(0.0, strength))

    def calculate_hand_potential(self, hole_cards: List[str], community_cards: List[str]) -> Tuple[float, float]:
        """Calculate positive and negative potential"""
        if len(community_cards) >= 5:
            return (0.0, 0.0)
            
        current_strength = self.evaluate_hand_strength(hole_cards, community_cards)
        remaining_cards = []
        
        # Generate remaining possible cards
        used_cards = set(hole_cards + community_cards)
        for rank in self.ranks:
            for suit in self.suits:
                card = f"{rank}{suit}"
                if card not in used_cards:
                    remaining_cards.append(card)
                    
        # Sample possible outcomes
        better_count = worse_count = total_count = 0
        max_samples = 100  # Limit sampling for performance
        
        possible_cards = min(5 - len(community_cards), 2)
        for next_cards in itertools.combinations(remaining_cards, possible_cards):
            future_community = community_cards + list(next_cards)
            future_strength = self.evaluate_hand_strength(hole_cards, future_community)
            
            if future_strength > current_strength:
                better_count += 1
            elif future_strength < current_strength:
                worse_count += 1
            total_count += 1
            
            if total_count >= max_samples:
                break
                
        if total_count == 0:
            return (0.0, 0.0)
            
        positive_potential = better_count / total_count
        negative_potential = worse_count / total_count
        
        return (positive_potential, negative_potential)
