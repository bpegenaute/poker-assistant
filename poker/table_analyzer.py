import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
import pytesseract
import re
import logging
from dataclasses import dataclass
from PIL import Image
import time
from collections import deque

@dataclass
class TableRegion:
    name: str
    top: int
    left: int
    width: int
    height: int
    type: str  # 'text', 'cards', 'position', 'stack'
    confidence: float = 0.0

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
        self.analysis_history = deque(maxlen=10)
        self.frame_buffer = deque(maxlen=5)  # Store last 5 frames for comparison

    def setup_regions(self):
        """Setup default table regions for analysis with improved structure"""
        self.regions = {
            'player_cards': TableRegion('player_cards', 0, 0, 200, 100, 'cards'),
            'community_cards': TableRegion('community_cards', 0, 200, 500, 100, 'cards'),
            'pot': TableRegion('pot', 100, 0, 200, 50, 'text'),
            'player_stack': TableRegion('player_stack', 150, 0, 200, 50, 'stack'),
            'position_indicator': TableRegion('position_indicator', 50, 0, 100, 30, 'position'),
            'action_area': TableRegion('action_area', 200, 0, 300, 100, 'text'),
            # Add regions for other player stacks
            'btn_stack': TableRegion('btn_stack', 150, 200, 200, 50, 'stack'),
            'sb_stack': TableRegion('sb_stack', 150, 400, 200, 50, 'stack'),
            'bb_stack': TableRegion('bb_stack', 150, 600, 200, 50, 'stack'),
            'utg_stack': TableRegion('utg_stack', 150, 800, 200, 50, 'stack')
        }

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Enhanced image preprocessing for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Apply morphological operations
        kernel = np.ones((2,2), np.uint8)
        processed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        return processed

    def detect_position(self, image: np.ndarray) -> Tuple[str, float]:
        """Enhanced position detection with confidence scoring"""
        region = self.regions['position_indicator']
        roi = image[region.top:region.top + region.height,
                   region.left:region.left + region.width]
        
        processed = self.preprocess_image(roi)
        text = pytesseract.image_to_string(processed).upper()
        
        # Calculate confidence scores for each position
        position_scores = {}
        for position, patterns in self.position_map.items():
            max_score = 0
            for pattern in patterns['text']:
                if pattern in text:
                    # Calculate confidence based on text match quality
                    similarity = len(pattern) / len(text.strip())
                    score = similarity * (1.0 if pattern == text.strip() else 0.8)
                    max_score = max(max_score, score)
            position_scores[position] = max_score
        
        # Get position with highest confidence
        if position_scores:
            best_position = max(position_scores.items(), key=lambda x: x[1])
            return best_position[0], best_position[1]
        
        return 'Unknown', 0.0

    def detect_cards(self, image: np.ndarray, region: TableRegion) -> Tuple[List[str], float]:
        """Enhanced card detection with confidence scoring"""
        roi = image[region.top:region.top + region.height,
                   region.left:region.left + region.width]
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        cards = []
        confidences = []
        ranks = '23456789TJQKA'
        suits = 'cdhs'
        
        # Process image for better card detection
        processed = self.preprocess_image(roi)
        
        # Detect card contours
        contours, _ = cv2.findContours(
            processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                x, y, w, h = cv2.boundingRect(contour)
                card_roi = roi[y:y+h, x:x+w]
                
                # Enhanced OCR configuration
                text = pytesseract.image_to_string(
                    card_roi,
                    config='--psm 10 --oem 3'
                )
                
                rank_match = re.search(f'[{ranks}]', text.upper())
                suit_match = re.search(f'[CDHS]', text.upper())
                
                if rank_match and suit_match:
                    rank = rank_match.group()
                    suit = suits[['C','D','H','S'].index(suit_match.group())]
                    cards.append(f"{rank}{suit}")
                    
                    # Calculate confidence based on clarity of detection
                    confidence = pytesseract.image_to_data(
                        card_roi,
                        config='--psm 10 --oem 3',
                        output_type=pytesseract.Output.DICT
                    )
                    conf_values = [float(c) for c in confidence['conf'] if c != '-1']
                    if conf_values:
                        confidences.append(sum(conf_values) / len(conf_values) / 100)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        return cards, avg_confidence

    def detect_numbers(self, image: np.ndarray, region: TableRegion) -> Tuple[float, float]:
        """Enhanced number detection with confidence scoring"""
        roi = image[region.top:region.top + region.height,
                   region.left:region.left + region.width]
        
        processed = self.preprocess_image(roi)
        
        # Use multiple OCR passes with different configurations
        configs = [
            '--psm 6 digits',
            '--psm 7 digits',
            '--psm 8 digits'
        ]
        
        results = []
        confidences = []
        
        for config in configs:
            data = pytesseract.image_to_data(
                processed,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            for i, text in enumerate(data['text']):
                if text.strip():
                    conf = float(data['conf'][i])
                    if conf > 0:
                        try:
                            number = float(re.sub(r'[^\d.]', '', text))
                            results.append((number, conf))
                        except ValueError:
                            continue
        
        if results:
            # Weight results by confidence
            weighted_sum = sum(num * conf for num, conf in results)
            total_conf = sum(conf for _, conf in results)
            return weighted_sum / total_conf, total_conf / (100 * len(results))
        
        return 0.0, 0.0

    def detect_actions(self, image: np.ndarray) -> Dict:
        """Enhanced action detection with timing and confidence"""
        region = self.regions['action_area']
        roi = image[region.top:region.top + region.height,
                   region.left:region.left + region.width]
        
        processed = self.preprocess_image(roi)
        
        actions = {
            'RAISE': {'amount': 0.0, 'confidence': 0.0},
            'CALL': {'amount': 0.0, 'confidence': 0.0},
            'CHECK': {'amount': 0.0, 'confidence': 0.0},
            'FOLD': {'amount': 0.0, 'confidence': 0.0},
            'ALL-IN': {'amount': 0.0, 'confidence': 0.0}
        }
        
        # Multiple OCR passes for better accuracy
        data = pytesseract.image_to_data(
            processed,
            config='--psm 6',
            output_type=pytesseract.Output.DICT
        )
        
        text = ' '.join(data['text']).upper()
        confidences = [float(c) for c in data['conf'] if c != '-1']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        for action in actions.keys():
            if action in text:
                amount_match = re.search(r'\d+\.?\d*', text)
                if amount_match:
                    actions[action]['amount'] = float(amount_match.group())
                    actions[action]['confidence'] = avg_confidence / 100
                else:
                    actions[action]['amount'] = 1.0
                    actions[action]['confidence'] = avg_confidence / 100
        
        return actions

    def analyze_table(self, image: np.ndarray) -> Dict:
        """Perform comprehensive table analysis with error correction"""
        try:
            # Add frame to buffer for comparison
            self.frame_buffer.append(image)
            
            # Detect all components with confidence scores
            position, pos_confidence = self.detect_position(image)
            hole_cards, hole_confidence = self.detect_cards(image, self.regions['player_cards'])
            community_cards, comm_confidence = self.detect_cards(image, self.regions['community_cards'])
            pot_size, pot_confidence = self.detect_numbers(image, self.regions['pot'])
            stack_size, stack_confidence = self.detect_numbers(image, self.regions['player_stack'])
            actions = self.detect_actions(image)
            
            # Detect other player stacks
            other_stacks = {}
            for pos in ['btn', 'sb', 'bb', 'utg']:
                region = self.regions[f'{pos}_stack']
                amount, conf = self.detect_numbers(image, region)
                other_stacks[pos] = {'amount': amount, 'confidence': conf}
            
            analysis = {
                'timestamp': time.time(),
                'position': position,
                'position_confidence': pos_confidence,
                'hole_cards': hole_cards,
                'hole_cards_confidence': hole_confidence,
                'community_cards': community_cards,
                'community_cards_confidence': comm_confidence,
                'pot_size': pot_size,
                'pot_confidence': pot_confidence,
                'stack_size': stack_size,
                'stack_confidence': stack_confidence,
                'actions': actions,
                'other_stacks': other_stacks
            }
            
            # Error correction using frame comparison
            if len(self.frame_buffer) >= 2:
                analysis = self._apply_error_correction(analysis)
            
            # Store analysis history
            self.analysis_history.append(analysis)
            self.last_analysis = analysis
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Table analysis failed: {str(e)}")
            return None

    def _apply_error_correction(self, current_analysis: Dict) -> Dict:
        """Apply error correction using frame comparison"""
        if not self.analysis_history:
            return current_analysis
        
        prev_analysis = self.analysis_history[-1]
        
        # Correct sudden changes with low confidence
        def correct_value(curr_val, curr_conf, prev_val, threshold=0.5):
            if curr_conf < threshold:
                return prev_val
            return curr_val
        
        # Apply corrections
        current_analysis['position'] = correct_value(
            current_analysis['position'],
            current_analysis['position_confidence'],
            prev_analysis['position']
        )
        
        current_analysis['pot_size'] = correct_value(
            current_analysis['pot_size'],
            current_analysis['pot_confidence'],
            prev_analysis['pot_size']
        )
        
        current_analysis['stack_size'] = correct_value(
            current_analysis['stack_size'],
            current_analysis['stack_confidence'],
            prev_analysis['stack_size']
        )
        
        # Correct cards only if confidence is very low
        if current_analysis['hole_cards_confidence'] < 0.3:
            current_analysis['hole_cards'] = prev_analysis['hole_cards']
        
        if current_analysis['community_cards_confidence'] < 0.3:
            current_analysis['community_cards'] = prev_analysis['community_cards']
        
        return current_analysis

    def get_action_timing(self) -> Dict:
        """Analyze timing between actions with confidence scores"""
        if len(self.analysis_history) < 2:
            return {}
            
        timings = []
        confidences = []
        
        for i in range(1, len(self.analysis_history)):
            curr = self.analysis_history[i]
            prev = self.analysis_history[i-1]
            
            time_diff = curr['timestamp'] - prev['timestamp']
            
            # Calculate confidence based on detection quality
            conf = min(
                curr['position_confidence'],
                curr['pot_confidence'],
                curr['stack_confidence']
            )
            
            timings.append(time_diff)
            confidences.append(conf)
            
        return {
            'average_time': sum(timings) / len(timings),
            'min_time': min(timings),
            'max_time': max(timings),
            'confidence': sum(confidences) / len(confidences)
        }

    def detect_significant_changes(self) -> Dict:
        """Detect significant changes with confidence scores"""
        if len(self.analysis_history) < 2:
            return {}
            
        prev = self.analysis_history[-2]
        curr = self.analysis_history[-1]
        
        changes = {
            'new_cards': {
                'detected': False,
                'confidence': 0.0
            },
            'pot_changed': {
                'detected': False,
                'confidence': 0.0
            },
            'stack_changed': {
                'detected': False,
                'confidence': 0.0
            },
            'position_changed': {
                'detected': False,
                'confidence': 0.0
            },
            'new_action': {
                'detected': False,
                'confidence': 0.0
            }
        }
        
        # Check card changes
        if (len(curr['hole_cards']) != len(prev['hole_cards']) or
            len(curr['community_cards']) != len(prev['community_cards'])):
            changes['new_cards']['detected'] = True
            changes['new_cards']['confidence'] = min(
                curr['hole_cards_confidence'],
                curr['community_cards_confidence']
            )
        
        # Check pot changes
        if abs(curr['pot_size'] - prev['pot_size']) > 0.1:
            changes['pot_changed']['detected'] = True
            changes['pot_changed']['confidence'] = curr['pot_confidence']
        
        # Check stack changes
        if abs(curr['stack_size'] - prev['stack_size']) > 0.1:
            changes['stack_changed']['detected'] = True
            changes['stack_changed']['confidence'] = curr['stack_confidence']
        
        # Check position changes
        if curr['position'] != prev['position']:
            changes['position_changed']['detected'] = True
            changes['position_changed']['confidence'] = curr['position_confidence']
        
        # Check action changes
        curr_actions = set(k for k, v in curr['actions'].items() if v['amount'] > 0)
        prev_actions = set(k for k, v in prev['actions'].items() if v['amount'] > 0)
        if curr_actions != prev_actions:
            changes['new_action']['detected'] = True
            changes['new_action']['confidence'] = max(
                (v['confidence'] for v in curr['actions'].values()),
                default=0.0
            )
        
        return changes
