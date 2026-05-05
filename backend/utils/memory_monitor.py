"""
Memory Monitor for Islamic AI Agent
===================================

Tracks memory usage, warns of issues, and triggers cleanup when needed.
"""

import os
import gc
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import threading

logger = logging.getLogger("MemoryMonitor")

# Try to import psutil for better memory tracking
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("⚠️  psutil not available - limited memory monitoring")


class MemoryMonitor:
    """Monitors memory usage and triggers cleanup when needed"""
    
    def __init__(self, warn_threshold_mb: int = 2000, error_threshold_mb: int = 3500):
        self.warn_threshold = warn_threshold_mb * 1024 * 1024  # Convert to bytes
        self.error_threshold = error_threshold_mb * 1024 * 1024
        self.peak_memory = 0
        self.measurements: Dict[datetime, int] = {}
        self._lock = threading.Lock()
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process(os.getpid())
                mem_info = process.memory_info()
                
                return {
                    'rss_mb': mem_info.rss / 1024 / 1024,  # Resident set size
                    'vms_mb': mem_info.vms / 1024 / 1024,  # Virtual memory size
                    'available_mb': psutil.virtual_memory().available / 1024 / 1024,
                    'available_percent': psutil.virtual_memory().percent,
                    'process_percent': process.memory_percent(),
                }
            except Exception as e:
                logger.warning(f"⚠️  Failed to get memory stats: {e}")
        
        return {'error': 'psutil not available'}
    
    def check_memory(self) -> Dict[str, Any]:
        """Check memory and return status"""
        memory_usage = self.get_memory_usage()
        
        if 'error' in memory_usage:
            return {
                'status': 'unknown',
                'message': 'Cannot monitor memory'
            }
        
        rss_mb = memory_usage.get('rss_mb', 0)
        available_mb = memory_usage.get('available_mb', 0)
        
        # Update peak
        with self._lock:
            if rss_mb > self.peak_memory:
                self.peak_memory = rss_mb
        
        # Determine status
        status = 'healthy'
        message = f"✅ Memory OK ({rss_mb:.0f}MB / {available_mb:.0f}MB available)"
        
        if rss_mb > self.error_threshold / 1024 / 1024:
            status = 'critical'
            message = f"❌ CRITICAL: Memory ({rss_mb:.0f}MB) exceeds error threshold ({self.error_threshold / 1024 / 1024:.0f}MB)"
            logger.error(message)
            self.trigger_cleanup()
        elif rss_mb > self.warn_threshold / 1024 / 1024:
            status = 'warning'
            message = f"⚠️  WARNING: Memory ({rss_mb:.0f}MB) exceeds warning threshold ({self.warn_threshold / 1024 / 1024:.0f}MB)"
            logger.warning(message)
            self.trigger_cleanup()
        
        return {
            'status': status,
            'message': message,
            'memory_usage': memory_usage,
            'peak_memory_mb': self.peak_memory,
            'timestamp': datetime.now().isoformat()
        }
    
    def trigger_cleanup(self) -> Dict[str, Any]:
        """Trigger garbage collection and cleanup"""
        logger.info("🧹 Triggering memory cleanup...")
        
        collected = gc.collect()
        
        # Get memory after cleanup
        memory_after = self.get_memory_usage()
        
        return {
            'action': 'cleanup',
            'objects_collected': collected,
            'memory_after': memory_after,
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_peak(self):
        """Reset peak memory counter"""
        with self._lock:
            self.peak_memory = 0


# Global monitor instance
_monitor: Optional[MemoryMonitor] = None


def get_memory_monitor() -> MemoryMonitor:
    """Get or create global memory monitor"""
    global _monitor
    if _monitor is None:
        _monitor = MemoryMonitor()
    return _monitor


def check_memory() -> Dict[str, Any]:
    """Check memory status"""
    monitor = get_memory_monitor()
    return monitor.check_memory()


def cleanup_memory() -> Dict[str, Any]:
    """Trigger memory cleanup"""
    monitor = get_memory_monitor()
    return monitor.trigger_cleanup()


def get_memory_status() -> Dict[str, Any]:
    """Get current memory status"""
    return check_memory()
