from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import time
import psutil
import threading
from datetime import datetime
import os

class PokerMonitor:
    def __init__(self):
        self.logger = logging.getLogger('PokerMonitor')
        self.setup_logging()
        self.observer = Observer()
        self.running = False
        self.performance_thread = None
        
    def setup_logging(self):
        """Setup logging configuration"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/poker_monitor.log'),
                logging.StreamHandler()
            ]
        )

    def start_monitoring(self):
        """Start all monitoring systems"""
        self.running = True
        
        # Start performance monitoring thread
        self.performance_thread = threading.Thread(target=self._monitor_performance)
        self.performance_thread.daemon = True
        self.performance_thread.start()
        
        # Start file system monitoring
        event_handler = PokerEventHandler()
        self.observer.schedule(event_handler, '.', recursive=True)
        self.observer.start()
        
        self.logger.info("Monitoring systems started")

    def stop_monitoring(self):
        """Stop all monitoring systems"""
        self.running = False
        self.observer.stop()
        self.observer.join()
        if self.performance_thread:
            self.performance_thread.join()
        self.logger.info("Monitoring systems stopped")

    def _monitor_performance(self):
        """Monitor system performance metrics"""
        while self.running:
            try:
                # Get process info
                process = psutil.Process()
                
                # Collect metrics
                cpu_percent = process.cpu_percent(interval=1)
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                
                # Log metrics if they exceed thresholds
                if cpu_percent > 80:
                    self.logger.warning(f"High CPU usage detected: {cpu_percent}%")
                if memory_percent > 80:
                    self.logger.warning(f"High memory usage detected: {memory_percent}%")
                
                # Log general metrics every 5 minutes
                if int(time.time()) % 300 == 0:
                    self.logger.info(
                        f"Performance metrics - CPU: {cpu_percent}%, "
                        f"Memory: {memory_info.rss / 1024 / 1024:.2f}MB ({memory_percent:.1f}%)"
                    )
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {str(e)}")
                time.sleep(30)  # Wait longer on error

class PokerEventHandler(FileSystemEventHandler):
    """Handle file system events"""
    def __init__(self):
        self.logger = logging.getLogger('PokerEventHandler')
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Log modifications to important files
        if event.src_path.endswith(('.py', '.toml', '.streamlit')):
            self.logger.info(f"Modified: {event.src_path}")
            
    def on_created(self, event):
        if not event.is_directory:
            self.logger.info(f"Created: {event.src_path}")
            
    def on_deleted(self, event):
        if not event.is_directory:
            self.logger.info(f"Deleted: {event.src_path}")

# Global monitor instance
monitor = PokerMonitor()
