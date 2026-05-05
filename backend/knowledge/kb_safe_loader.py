"""
Safe Knowledge Base Loader with Disk Space Handling
"""

import os
import logging

logger = logging.getLogger("KBSafeLoader")


class SafeKnowledgeBaseLoader:
    """Wraps KB loading with disk space awareness"""
    
    @staticmethod
    def check_disk_space():
        """Check if we have enough disk space"""
        import shutil
        try:
            stat = shutil.disk_usage("/")
            free_gb = stat.free / (1024**3)
            total_gb = stat.total / (1024**3)
            used_pct = (stat.used / stat.total) * 100
            
            logger.info(f"Disk: {used_pct:.1f}% used ({free_gb:.1f}GB free of {total_gb:.1f}GB)")
            
            # Flag warning if < 500MB free
            if stat.free < 500 * 1024 * 1024:
                logger.warning(f"⚠️  Low disk space: Only {free_gb:.1f}GB free!")
                return False
            return True
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")
            return True  # Assume OK if can't check
    
    @staticmethod
    def load_kb_safe():
        """Load KB with fallback strategies"""
        try:
            # Check disk space first
            has_space = SafeKnowledgeBaseLoader.check_disk_space()
            
            if not has_space:
                logger.warning("Low disk space - using Lite KB (no heavy models)")
                try:
                    from backend.knowledge.local_knowledge_tools_lite import get_lite_kb
                    kb = get_lite_kb()
                    if kb:
                        logger.info("✅ Lite Knowledge base loaded successfully")
                        return kb
                except:
                    logger.warning("Lite KB also unavailable")
                    return None
            
            # Normal KB if space available
            try:
                from backend.knowledge.local_knowledge_tools import get_kb
                kb = get_kb()
                
                if kb and kb.db:
                    logger.info("✅ Knowledge base loaded successfully")
                    return kb
                else:
                    logger.warning("⚠️  Knowledge base not fully initialized")
                    return None
            except Exception as e:
                logger.warning(f"Full KB failed ({e}), trying lite version...")
                try:
                    from backend.knowledge.local_knowledge_tools_lite import get_lite_kb
                    kb = get_lite_kb()
                    if kb:
                        logger.info("✅ Lite Knowledge base loaded (fallback)")
                        return kb
                except:
                    pass
                return None
                
        except ImportError as e:
            logger.warning(f"KB modules not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load KB: {e}")
            return None
    
    @staticmethod
    def warm_kb_safe(kb):
        """Try to warm KB cache without failing if it can't"""
        if not kb:
            return False
        
        try:
            logger.info("Warming KB cache with light search...")
            # Use a simple one-word query to minimize memory/disk usage
            result = kb.search("Allah")
            if result:
                logger.info("✅ KB cache warmed successfully")
                return True
            else:
                logger.warning("⚠️  KB cache warm failed - might be slow on first search")
                return False
        except OSError as e:
            if "No space left on device" in str(e):
                logger.error("💾 Disk full - KB search may be unavailable")
                return False
            raise
        except Exception as e:
            logger.warning(f"Could not warm KB: {e}")
            return False
