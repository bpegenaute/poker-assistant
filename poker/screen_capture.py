import numpy as np
from PIL import Image
import time
from typing import Dict, Tuple, Optional
import logging
import pytesseract
import re
import io
import base64
import cv2
import streamlit as st

class PokerScreenCapture:
    def __init__(self):
        """Initialize browser-based screen capture"""
        self.regions = {
            'hole_cards': {'top': 0, 'left': 0, 'width': 200, 'height': 100},
            'community_cards': {'top': 0, 'left': 200, 'width': 500, 'height': 100},
            'pot': {'top': 100, 'left': 0, 'width': 200, 'height': 50},
            'stack': {'top': 150, 'left': 0, 'width': 200, 'height': 50}
        }
        self.is_calibrated = False
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for screen capture"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('PokerScreenCapture')

    def base64_to_image(self, base64_str: str) -> Optional[Image.Image]:
        """Convert base64 string to PIL Image"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]
            
            # Decode base64 string
            img_data = base64.b64decode(base64_str)
            return Image.open(io.BytesIO(img_data))
        except Exception as e:
            self.logger.error(f"Failed to convert base64 to image: {str(e)}")
            return None

    def calibrate_regions(self, template_base64: str) -> bool:
        """Calibrate screen regions using a template image"""
        try:
            # Convert base64 template to PIL Image
            template_img = self.base64_to_image(template_base64)
            if template_img is None:
                return False

            # Convert PIL Image to CV2 format
            template = cv2.cvtColor(np.array(template_img), cv2.COLOR_RGB2BGR)

            # Update regions based on template dimensions
            template_h, template_w = template.shape[:2]
            
            self.regions = {
                'hole_cards': {
                    'top': 0,
                    'left': 0,
                    'width': template_w // 3,
                    'height': template_h // 2
                },
                'community_cards': {
                    'top': 0,
                    'left': template_w // 3,
                    'width': template_w * 2 // 3,
                    'height': template_h // 2
                },
                'pot': {
                    'top': template_h // 2,
                    'left': 0,
                    'width': template_w // 4,
                    'height': template_h // 4
                },
                'stack': {
                    'top': template_h * 3 // 4,
                    'left': 0,
                    'width': template_w // 4,
                    'height': template_h // 4
                }
            }
            
            self.is_calibrated = True
            self.logger.info("Screen regions calibrated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Calibration failed: {str(e)}")
            return False

    def process_image(self, image: Image.Image) -> np.ndarray:
        """Process captured image for better OCR results"""
        # Convert PIL Image to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding for better text recognition
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply noise reduction
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Apply dilation to make text more prominent
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        
        return dilated

    def extract_text(self, image: np.ndarray) -> str:
        """Extract text from processed image using OCR"""
        try:
            # Configure Tesseract parameters for better accuracy
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            return text.strip()
        except Exception as e:
            self.logger.error(f"OCR failed: {str(e)}")
            return ""

    def parse_cards(self, text: str) -> list:
        """Parse card text into standardized format"""
        suits = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
        ranks = '23456789TJQKA'
        
        cards = []
        pattern = r'([2-9TJQKA])([♣♦♥♠])'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            rank, suit = match.groups()
            if rank in ranks and suit in suits:
                cards.append(f"{rank}{suits[suit]}")
        
        return cards

    def parse_numbers(self, text: str) -> float:
        """Parse numerical values (pot size, stack size) from text"""
        try:
            cleaned = re.sub(r'[^\d.]', '', text)
            if cleaned:
                return float(cleaned)
        except ValueError:
            pass
        return 0.0

    def analyze_region(self, region_name: str, image: Image.Image) -> Dict:
        """Analyze a specific region and extract relevant information"""
        processed = self.process_image(image)
        text = self.extract_text(processed)
        
        result = {'type': region_name, 'raw_text': text}
        
        if region_name in ['hole_cards', 'community_cards']:
            result['cards'] = self.parse_cards(text)
        elif region_name in ['pot', 'stack']:
            result['value'] = self.parse_numbers(text)
            
        return result

    def process_captured_image(self, base64_img: str, region_name: str) -> Dict:
        """Process a captured image from browser"""
        try:
            image = self.base64_to_image(base64_img)
            if image:
                return self.analyze_region(region_name, image)
            return {'error': 'Failed to process image'}
        except Exception as e:
            self.logger.error(f"Image processing failed: {str(e)}")
            return {'error': str(e)}
