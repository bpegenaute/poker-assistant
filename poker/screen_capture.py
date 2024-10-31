import mss
import cv2
import numpy as np
from PIL import Image
import time
from typing import Dict, Tuple, Optional
import logging
import pytesseract
import re

class PokerScreenCapture:
    def __init__(self):
        """Initialize screen capture with MSS"""
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[0]  # Use primary monitor
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

    def calibrate_regions(self, template_image_path: str) -> bool:
        """Calibrate screen regions using a template image"""
        try:
            template = cv2.imread(template_image_path)
            if template is None:
                self.logger.error(f"Failed to load template image: {template_image_path}")
                return False

            # Take a screenshot of the entire monitor
            screenshot = self.capture_screen()
            if screenshot is None:
                return False

            # Convert screenshot to cv2 format
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Find template in screenshot
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            _, _, _, max_loc = cv2.minMaxLoc(result)

            # Update regions based on template match
            template_h, template_w = template.shape[:2]
            base_x, base_y = max_loc
            
            # Update region coordinates based on template match
            self.regions = {
                'hole_cards': {
                    'top': base_y,
                    'left': base_x,
                    'width': template_w // 3,
                    'height': template_h // 2
                },
                'community_cards': {
                    'top': base_y,
                    'left': base_x + template_w // 3,
                    'width': template_w * 2 // 3,
                    'height': template_h // 2
                },
                'pot': {
                    'top': base_y + template_h // 2,
                    'left': base_x,
                    'width': template_w // 4,
                    'height': template_h // 4
                },
                'stack': {
                    'top': base_y + template_h * 3 // 4,
                    'left': base_x,
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

    def capture_screen(self) -> Optional[Image.Image]:
        """Capture the entire screen"""
        try:
            screenshot = self.sct.grab(self.monitor)
            return Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        except Exception as e:
            self.logger.error(f"Screen capture failed: {str(e)}")
            return None

    def capture_region(self, region_name: str) -> Optional[Image.Image]:
        """Capture a specific region of the screen"""
        if not self.is_calibrated:
            self.logger.warning("Screen regions not calibrated")
            return None

        try:
            region = self.regions.get(region_name)
            if not region:
                self.logger.error(f"Invalid region name: {region_name}")
                return None

            screenshot = self.sct.grab(region)
            return Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        except Exception as e:
            self.logger.error(f"Region capture failed: {str(e)}")
            return None

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
        # Define card patterns
        suits = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
        ranks = '23456789TJQKA'
        
        # Clean up text and extract cards
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
            # Remove currency symbols and other non-numeric characters
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

    def monitor_poker_table(self, callback=None, interval: float = 1.0):
        """Continuously monitor poker table and analyze changes"""
        self.logger.info("Starting poker table monitoring")
        
        last_captures = {}
        
        while True:
            try:
                current_captures = {}
                table_state = {}
                
                for region_name in self.regions:
                    img = self.capture_region(region_name)
                    if img:
                        current_captures[region_name] = img
                        
                        # Compare with last capture
                        if region_name not in last_captures or self._images_different(
                            current_captures[region_name], 
                            last_captures[region_name]
                        ):
                            analysis = self.analyze_region(region_name, img)
                            table_state[region_name] = analysis
                            if callback:
                                callback(region_name, analysis)
                
                last_captures = current_captures
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {str(e)}")
                time.sleep(interval)

    def _images_different(self, img1: Image.Image, img2: Image.Image, 
                        threshold: float = 0.95) -> bool:
        """Compare two images to detect changes"""
        try:
            # Convert PIL images to CV2 format
            img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
            img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
            
            # Calculate image difference
            diff = cv2.absdiff(img1_cv, img2_cv)
            diff_sum = np.sum(diff)
            max_diff = img1_cv.shape[0] * img1_cv.shape[1] * 255 * 3
            
            return (diff_sum / max_diff) > (1 - threshold)
        except Exception as e:
            self.logger.error(f"Image comparison failed: {str(e)}")
            return False
