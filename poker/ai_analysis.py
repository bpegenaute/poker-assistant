from typing import Dict, List, Optional
import openai
import os
from datetime import datetime
from .database import Database
import json

class AIAnalysis:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.db = Database()

    def analyze_player_profile(self, player_stats: Dict) -> Dict:
        """Analyze player statistics using OpenAI API"""
        prompt = f"""
        Analyze the following poker player statistics and provide strategic insights:
        
        Total Hands: {player_stats['total_hands']}
        Position Distribution: {json.dumps(player_stats['positions'])}
        Action Distribution: {json.dumps(player_stats['actions'])}
        Profit/Loss: ${player_stats['profit_loss']:.2f}
        Showdown Frequency: {player_stats['showdown_frequency']:.2%}
        
        Provide a concise analysis focusing on:
        1. Playing style (aggressive/passive, tight/loose)
        2. Position-based tendencies
        3. Key strengths and weaknesses
        4. Recommended adjustments
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a poker strategy expert analyzing player statistics."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            return {
                'analysis': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def get_opponent_model(self, opponent_actions: List[Dict]) -> Dict:
        """Generate opponent modeling insights"""
        prompt = f"""
        Analyze the following opponent actions and provide strategic insights:
        {json.dumps(opponent_actions, indent=2)}
        
        Focus on:
        1. Betting patterns
        2. Position-based tendencies
        3. Aggression frequency
        4. Bluffing frequency
        5. Recommended counter-strategies
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a poker strategy expert analyzing opponent behavior."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            return {
                'model': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def get_hand_history_insights(self, hand_type_performance: Dict) -> Dict:
        """Analyze hand history performance"""
        prompt = f"""
        Analyze the following hand type performance data and provide strategic insights:
        {json.dumps(hand_type_performance, indent=2)}
        
        Provide recommendations on:
        1. Most profitable hand types
        2. Hands to avoid or play differently
        3. Position-specific hand selection
        4. Suggested adjustments to current strategy
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a poker strategy expert analyzing hand history data."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            return {
                'insights': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def update_player_profile(self, player_id: str) -> Dict:
        """Update player profile with latest analysis"""
        stats = self.db.get_player_stats()
        hand_performance = self.db.get_hand_type_performance()
        
        profile_analysis = self.analyze_player_profile(stats)
        hand_insights = self.get_hand_history_insights(hand_performance)
        
        profile_data = {
            'stats': stats,
            'hand_performance': hand_performance,
            'analysis': profile_analysis,
            'hand_insights': hand_insights,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Store updated profile in database
        try:
            profile = self.db.session.query(self.db.PlayerProfile).filter_by(player_id=player_id).first()
            if not profile:
                profile = self.db.PlayerProfile(player_id=player_id)
            
            profile.stats = profile_data
            profile.last_updated = datetime.utcnow()
            self.db.session.add(profile)
            self.db.session.commit()
            
            return profile_data
        except Exception as e:
            return {'error': str(e)}
