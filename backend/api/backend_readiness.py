"""
Backend Readiness Service
=========================

Manages backend initialization state and provides readiness status to frontend.
Ensures frontend only activates when backend is fully operational.
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from threading import Lock, Thread
import json

logger = logging.getLogger("BackendReadiness")


class BackendReadinessManager:
    """Tracks and manages backend initialization state"""
    
    def __init__(self):
        self.components_status = {
            'rag_loader': {'ready': False, 'timestamp': None, 'error': None},
            'single_agent': {'ready': False, 'timestamp': None, 'error': None},
            'multi_agent': {'ready': False, 'timestamp': None, 'error': None},
            'embeddings': {'ready': False, 'timestamp': None, 'error': None},
            'llm': {'ready': False, 'timestamp': None, 'error': None},
        }
        self.startup_start_time = time.time()
        self.fully_ready = False
        self.initialization_complete = False
        self._lock = Lock()
    
    def mark_component_ready(self, component: str, success: bool = True, error: str = None):
        """Mark a component as ready or failed"""
        with self._lock:
            if component in self.components_status:
                self.components_status[component]['ready'] = success
                self.components_status[component]['timestamp'] = datetime.now().isoformat()
                if error:
                    self.components_status[component]['error'] = error
                
                logger.info(f"{'✅' if success else '❌'} Component '{component}': {'ready' if success else 'failed'}")
    
    def check_core_ready(self) -> bool:
        """Check if core (critical) components are ready"""
        critical = ['rag_loader', 'single_agent']
        return all(
            self.components_status[comp]['ready'] 
            for comp in critical
        )
    
    def check_fully_ready(self) -> bool:
        """Check if all components are ready"""
        return all(comp['ready'] for comp in self.components_status.values())
    
    def set_initialization_complete(self):
        """Mark initialization as complete"""
        with self._lock:
            self.initialization_complete = True
            self.fully_ready = self.check_fully_ready()
            logger.info(f"🎉 Initialization complete. Fully ready: {self.fully_ready}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete readiness status"""
        with self._lock:
            elapsed = time.time() - self.startup_start_time
            
            return {
                'initialized': self.initialization_complete,
                'fully_ready': self.fully_ready,
                'core_ready': self.check_core_ready(),
                'startup_time': elapsed,
                'components': self.components_status,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_readiness_percentage(self) -> float:
        """Get readiness as percentage (0-100)"""
        total = len(self.components_status)
        ready = sum(1 for c in self.components_status.values() if c['ready'])
        return (ready / total) * 100
    
    def wait_for_core_ready(self, timeout: int = 30) -> bool:
        """Wait for core components to be ready"""
        start = time.time()
        while time.time() - start < timeout:
            if self.check_core_ready():
                return True
            time.sleep(0.5)
        
        logger.warning(f"⚠️  Core components not ready after {timeout}s")
        return False
    
    def wait_for_fully_ready(self, timeout: int = 60) -> bool:
        """Wait for all components to be ready"""
        start = time.time()
        while time.time() - start < timeout:
            if self.fully_ready:
                return True
            time.sleep(0.5)
        
        logger.warning(f"⚠️  System not fully ready after {timeout}s")
        return False


# Global instance
_readiness_manager: Optional[BackendReadinessManager] = None
_manager_lock = Lock()


def get_readiness_manager() -> BackendReadinessManager:
    """Get or create global readiness manager"""
    global _readiness_manager
    
    if _readiness_manager is None:
        with _manager_lock:
            if _readiness_manager is None:
                _readiness_manager = BackendReadinessManager()
    
    return _readiness_manager


def mark_component_ready(component: str, success: bool = True, error: str = None):
    """Convenience function to mark component ready"""
    manager = get_readiness_manager()
    manager.mark_component_ready(component, success, error)


def get_readiness_status() -> Dict[str, Any]:
    """Convenience function to get readiness status"""
    manager = get_readiness_manager()
    return manager.get_status()


def get_readiness_percentage() -> float:
    """Get readiness percentage"""
    manager = get_readiness_manager()
    return manager.get_readiness_percentage()


def is_core_ready() -> bool:
    """Check if core components ready"""
    manager = get_readiness_manager()
    return manager.check_core_ready()


def is_fully_ready() -> bool:
    """Check if fully ready"""
    manager = get_readiness_manager()
    return manager.fully_ready


def set_initialization_complete():
    """Mark initialization complete"""
    manager = get_readiness_manager()
    manager.set_initialization_complete()
