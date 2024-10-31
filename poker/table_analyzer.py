import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
import pytesseract
import re
import logging
from dataclasses import dataclass
from PIL import Image
import time

@dataclass
class TableRegion:
    name: str
    top: int
    left: int
    width: int
    height: int
    type: str  # 'text', 'cards', 'position'

class TableAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('TableAnalyzer')
        self.setup_regions()
        self.position_map = {
            'BTN': {'text': ['BTN', 'BUTTON', 'D'], 'confidence': 0.0},
            'SB': {'text': ['SB', 'SMALL BLIND'], 'confidence': 0.0},
            'BB': {'text': ['BB', 'BIG BLIND'], 'confidence': 0.0},
            'UTG': {'text': ['UTG', 'UNDER THE GUN'], 'confidence': 0.0},
            'MP': {'text': ['MP', 'MIDDLE'], 'confidence': 0.0},
            'CO': {'text': ['CO', 'CUTOFF'], 'confidence': 0.0}
        }
        self.last_analysis = None
        self.analysis_history = []

    def setup_regions(self):
        """Setup default table regions for analysis"""
        self.regions = {
            'player_cards': TableRegion('player_cards', 0, 0, 200, 100, 'cards'),
            'community_cards': TableRegion('community_cards', 0, 200, 500, 100, 'cards'),
            'pot': TableRegion('pot', 100, 0, 200, 50, 'text'),
            'player_stack': TableRegion('player_stack', 150, 0, 200, 50, 'text'),
            'position_indicator': TableRegion('position_indicator', 50, 0, 100, 30, 'position'),
            'action_area': TableRegion('action_area', 200, 0, 300, 100, 'text')
        }

    def calibrate_regions(self, template_image: np.ndarray) -> bool:
        """Calibrate analysis regions using template image"""
        try:
            height, width = template_image.shape[:2]
            
            # Adjust regions based on template dimensions
            self.regions['player_cards'].width = width // 3
            self.regions['player_cards'].height = height // 4
            
            self.regions['community_cards'].left = width // 3
            self.regions['community_cards'].width = width // 2
            self.regions['community_cards'].height = height // 4
            
            self.regions['pot'].top = height // 2
            self.regions['pot'].width = width // 4
            
            self.regions['player_stack'].top = height * 3 // 4
            self.regions['player_stack'].width = width // 4
            
            self.regions['position_indicator'].width = width // 6
            self.regions['position_indicator'].height = height // 8
            
            self.regions['action_area'].width = width // 2
            self.regions['action_area'].top = height // 2
            
            return True
        except Exception as e:
            self.logger.error(f"Calibration failed: {str(e)}")
            return False

    def detect_position(self, image: np.ndarray) -> Tuple[str, float]:
        """Detect player position from position indicator region"""
        position_region = self.regions['position_indicator']
        roi = image[position_region.top:position_region.top + position_region.height,
                   position_region.left:position_region.left + position_region.width]
        
        text = pytesseract.image_to_string(roi).upper()
        max_confidence = 0.0
        detected_position = None
        
        for position, patterns in self.position_map.items():
            for pattern in patterns['text']:
                if pattern in text:
                    confidence = 1.0 if pattern == text.strip() else 0.8
                    if confidence > max_confidence:
                        max_confidence = confidence
                        detected_position = position
        
        return detected_position or 'Unknown', max_confidence

    def detect_cards(self, image: np.ndarray, region: TableRegion) -> List[str]:
        """Detect cards in the specified region"""
        roi = image[region.top:region.top + region.height,
                   region.left:region.left + region.width]
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Define card templates (simplified for demonstration)
        cards = []
        ranks = '23456789TJQKA'
        suits = 'cdhs'  # clubs, diamonds, hearts, spades
        
        # Use contour detection to find card shapes
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Minimum card size
                x, y, w, h = cv2.boundingRect(contour)
                card_roi = roi[y:y+h, x:x+w]
                
                # Extract rank and suit using OCR
                text = pytesseract.image_to_string(card_roi, config='--psm 10')
                rank_match = re.search(f'[{ranks}]', text.upper())
                suit_match = re.search(f'[CDHS]', text.upper())
                
                if rank_match and suit_match:
                    rank = rank_match.group()
                    suit = suits[['C','D','H','S'].index(suit_match.group())]
                    cards.append(f"{rank}{suit}")
        
        return cards

    def detect_numbers(self, image: np.ndarray, region: TableRegion) -> float:
        """Detect numerical values (pot size, stack size) from region"""
        roi = image[region.top:region.top + region.height,
                   region.left:region.left + region.width]
        
        # Enhance image for number detection
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        text = pytesseract.image_to_string(thresh, config='--psm 6 digits')
        numbers = re.findall(r'\d+\.?\d*', text)
        
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        return 0.0

    def detect_actions(self, image: np.ndarray) -> Dict:
        """Detect player actions and timing"""
        action_region = self.regions['action_area']
        roi = image[action_region.top:action_region.top + action_region.height,
                   action_region.left:action_region.left + action_region.width]
        
        text = pytesseract.image_to_string(roi).upper()
        
        actions = {
            'RAISE': 0.0,
            'CALL': 0.0,
            'CHECK': 0.0,
            'FOLD': 0.0,
            'ALL-IN': 0.0
        }
        
        for action in actions.keys():
            if action in text:
                amount_match = re.search(r'\d+\.?\d*', text)
                if amount_match:
                    actions[action] = float(amount_match.group())
                else:
                    actions[action] = 1.0  # Action detected but no amount
                    
        return actions

    def analyze_table(self, image: np.ndarray) -> Dict:
        """Perform complete table analysis"""
        try:
            position, pos_confidence = self.detect_position(image)
            
            analysis = {
                'timestamp': time.time(),
                'position': position,
                'position_confidence': pos_confidence,
                'hole_cards': self.detect_cards(image, self.regions['player_cards']),
                'community_cards': self.detect_cards(image, self.regions['community_cards']),
                'pot_size': self.detect_numbers(image, self.regions['pot']),
                'stack_size': self.detect_numbers(image, self.regions['player_stack']),
                'actions': self.detect_actions(image)
            }
            
            # Store analysis history
            self.analysis_history.append(analysis)
            if len(self.analysis_history) > 10:
                self.analysis_history.pop(0)
            
            self.last_analysis = analysis
            return analysis
            
        except Exception as e:
            self.logger.error(f"Table analysis failed: {str(e)}")
            return None

    def get_action_timing(self) -> Dict:
        """Analyze timing between actions"""
        if len(self.analysis_history) < 2:
            return {}
            
        timings = []
        for i in range(1, len(self.analysis_history)):
            time_diff = self.analysis_history[i]['timestamp'] - \
                       self.analysis_history[i-1]['timestamp']
            timings.append(time_diff)
            
        return {
            'average_time': sum(timings) / len(timings),
            'min_time': min(timings),
            'max_time': max(timings)
        }

    def detect_significant_changes(self) -> Dict:
        """Detect significant changes between consecutive analyses"""
        if len(self.analysis_history) < 2:
            return {}
            
        prev = self.analysis_history[-2]
        curr = self.analysis_history[-1]
        
        changes = {
            'new_cards': False,
            'pot_changed': False,
            'stack_changed': False,
            'position_changed': False,
            'new_action': False
        }
        
        if len(curr['hole_cards']) != len(prev['hole_cards']) or \
           len(curr['community_cards']) != len(prev['community_cards']):
            changes['new_cards'] = True
            
        if abs(curr['pot_size'] - prev['pot_size']) > 0.1:
            changes['pot_changed'] = True
            
        if abs(curr['stack_size'] - prev['stack_size']) > 0.1:
            changes['stack_changed'] = True
            
        if curr['position'] != prev['position']:
            changes['position_changed'] = True
            
        if curr['actions'] != prev['actions']:
            changes['new_action'] = True
            
        return changes
