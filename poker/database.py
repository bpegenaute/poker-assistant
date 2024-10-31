from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import json

Base = declarative_base()

class Hand(Base):
    __tablename__ = 'hands'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    position = Column(String)
    hole_cards = Column(String)  # JSON string of hole cards
    community_cards = Column(String)  # JSON string of community cards
    action_taken = Column(String)
    pot_size = Column(Float)
    stack_size = Column(Float)
    
    result = relationship("Result", back_populates="hand", uselist=False)
    player_actions = relationship("PlayerAction", back_populates="hand")

class Result(Base):
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True)
    hand_id = Column(Integer, ForeignKey('hands.id'))
    profit_loss = Column(Float)
    showdown_reached = Column(Boolean, default=False)
    opponent_cards = Column(String, nullable=True)  # JSON string of opponent cards if shown
    
    hand = relationship("Hand", back_populates="result")

class PlayerAction(Base):
    __tablename__ = 'player_actions'
    
    id = Column(Integer, primary_key=True)
    hand_id = Column(Integer, ForeignKey('hands.id'))
    street = Column(String)  # preflop, flop, turn, river
    action_type = Column(String)  # bet, raise, call, fold
    amount = Column(Float)
    time_taken = Column(Float)  # seconds taken to make decision
    
    hand = relationship("Hand", back_populates="player_actions")

class PlayerProfile(Base):
    __tablename__ = 'player_profiles'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String, unique=True)
    stats = Column(JSON)  # Store aggregated statistics
    tendencies = Column(JSON)  # Store identified patterns
    last_updated = Column(DateTime, default=datetime.utcnow)

class AutomatedCapture(Base):
    __tablename__ = 'automated_captures'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    position = Column(String)
    active_position = Column(String)
    pot_size = Column(Float)
    current_bet = Column(Float)
    player_stacks = Column(JSON)  # Store stack sizes for all positions
    detected_cards = Column(JSON)  # Store all detected cards
    action_history = Column(JSON)  # Store sequence of actions
    confidence_score = Column(Float)  # OCR confidence level

class Database:
    def __init__(self):
        self.engine = create_engine(os.environ['DATABASE_URL'])
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def record_automated_capture(self, position: str, active_position: str,
                               pot_size: float, current_bet: float,
                               player_stacks: dict, detected_cards: dict,
                               action_history: list, confidence_score: float) -> AutomatedCapture:
        """Record an automated screen capture analysis"""
        capture = AutomatedCapture(
            position=position,
            active_position=active_position,
            pot_size=pot_size,
            current_bet=current_bet,
            player_stacks=json.dumps(player_stacks),
            detected_cards=json.dumps(detected_cards),
            action_history=json.dumps(action_history),
            confidence_score=confidence_score
        )
        self.session.add(capture)
        self.session.commit()
        return capture

    def record_hand(self, position: str, hole_cards: list, community_cards: list,
                   action_taken: str, pot_size: float, stack_size: float) -> Hand:
        """Record a new hand in the database"""
        hand = Hand(
            position=position,
            hole_cards=json.dumps(hole_cards),
            community_cards=json.dumps(community_cards),
            action_taken=action_taken,
            pot_size=pot_size,
            stack_size=stack_size
        )
        self.session.add(hand)
        self.session.commit()
        return hand

    def record_result(self, hand_id: int, profit_loss: float,
                     showdown_reached: bool = False, opponent_cards: list = None):
        """Record the result of a hand"""
        result = Result(
            hand_id=hand_id,
            profit_loss=profit_loss,
            showdown_reached=showdown_reached,
            opponent_cards=json.dumps(opponent_cards) if opponent_cards else None
        )
        self.session.add(result)
        self.session.commit()

    def record_player_action(self, hand_id: int, street: str,
                           action_type: str, amount: float, time_taken: float):
        """Record a player action during a hand"""
        action = PlayerAction(
            hand_id=hand_id,
            street=street,
            action_type=action_type,
            amount=amount,
            time_taken=time_taken
        )
        self.session.add(action)
        self.session.commit()

    def get_player_stats(self, position: str = None, last_n_hands: int = None) -> dict:
        """Get aggregated statistics for hands played"""
        query = self.session.query(Hand)
        if position:
            query = query.filter(Hand.position == position)
        if last_n_hands:
            query = query.order_by(Hand.timestamp.desc()).limit(last_n_hands)
        
        hands = query.all()
        
        stats = {
            'total_hands': len(hands),
            'positions': {},
            'actions': {},
            'profit_loss': 0.0,
            'showdown_frequency': 0.0
        }
        
        for hand in hands:
            stats['positions'][hand.position] = stats['positions'].get(hand.position, 0) + 1
            stats['actions'][hand.action_taken] = stats['actions'].get(hand.action_taken, 0) + 1
            if hand.result:
                stats['profit_loss'] += hand.result.profit_loss
                if hand.result.showdown_reached:
                    stats['showdown_frequency'] += 1
        
        if stats['total_hands'] > 0:
            stats['showdown_frequency'] /= stats['total_hands']
            
        return stats

    def get_position_success_rate(self, position: str) -> dict:
        """Calculate success rate for a specific position"""
        hands = self.session.query(Hand).filter(Hand.position == position).all()
        
        stats = {
            'total_hands': len(hands),
            'profitable_hands': 0,
            'average_profit': 0.0,
            'win_rate': 0.0
        }
        
        total_profit = 0.0
        for hand in hands:
            if hand.result:
                if hand.result.profit_loss > 0:
                    stats['profitable_hands'] += 1
                total_profit += hand.result.profit_loss
        
        if stats['total_hands'] > 0:
            stats['win_rate'] = stats['profitable_hands'] / stats['total_hands']
            stats['average_profit'] = total_profit / stats['total_hands']
            
        return stats

    def get_hand_type_performance(self) -> dict:
        """Analyze performance by hand type"""
        hands = self.session.query(Hand).all()
        
        performance = {}
        for hand in hands:
            hole_cards = json.loads(hand.hole_cards)
            # Simplified hand type classification
            hand_type = self._classify_hand_type(hole_cards)
            
            if hand_type not in performance:
                performance[hand_type] = {
                    'total_hands': 0,
                    'profitable_hands': 0,
                    'total_profit': 0.0
                }
            
            performance[hand_type]['total_hands'] += 1
            if hand.result:
                if hand.result.profit_loss > 0:
                    performance[hand_type]['profitable_hands'] += 1
                performance[hand_type]['total_profit'] += hand.result.profit_loss
        
        # Calculate win rates and average profits
        for hand_type in performance:
            stats = performance[hand_type]
            if stats['total_hands'] > 0:
                stats['win_rate'] = stats['profitable_hands'] / stats['total_hands']
                stats['average_profit'] = stats['total_profit'] / stats['total_hands']
        
        return performance

    def _classify_hand_type(self, hole_cards: list) -> str:
        """Classify hole cards into hand types"""
        if not hole_cards or len(hole_cards) != 2:
            return 'unknown'
        
        rank1, rank2 = hole_cards[0][0], hole_cards[1][0]
        suited = hole_cards[0][1] == hole_cards[1][1]
        
        if rank1 == rank2:
            return f"pocket_pair_{rank1}"
        elif suited:
            return f"suited_{rank1}{rank2}"
        else:
            return f"offsuit_{rank1}{rank2}"

    def close(self):
        """Close the database session"""
        self.session.close()
