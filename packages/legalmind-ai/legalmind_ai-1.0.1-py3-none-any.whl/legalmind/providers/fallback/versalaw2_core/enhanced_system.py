#!/usr/bin/env python3
"""
Enhanced VersaLaw2 System with Maya Wisdom Integration
Combines MayaLaw cases + Maya Wisdom + AI
"""

import sys
from pathlib import Path
import logging

# Add maya-legal-system to path
maya_system_path = Path("/root/dragon/global/mayalaw/maya-legal-system")
if maya_system_path.exists():
    sys.path.insert(0, str(maya_system_path))

from .system import VersaLaw2System
from .config import Config

logger = logging.getLogger(__name__)

class EnhancedVersaLaw2System(VersaLaw2System):
    """
    Enhanced system with Maya Wisdom integration
    
    Features:
    - MayaLaw cases (126 cases)
    - Maya Wisdom knowledge base
    - AI processing
    - Combined context
    """
    
    def __init__(self, config=None):
        """Initialize enhanced system"""
        super().__init__(config)
        
        # Try to load Maya Wisdom
        self.wisdom = None
        self.wisdom_available = False
        
        try:
            from core.maya_wisdom_processor import MayaWisdomProcessor
            self.wisdom = MayaWisdomProcessor()
            self.wisdom_available = True
            print("✅ Maya Wisdom Processor loaded")
            logger.info("Maya Wisdom Processor loaded successfully")
        except ImportError as e:
            print("⚠️  Maya Wisdom not available (optional)")
            logger.warning(f"Maya Wisdom not loaded: {e}")
        except Exception as e:
            print(f"⚠️  Error loading Maya Wisdom: {e}")
            logger.error(f"Maya Wisdom error: {e}")
    
    def ask(self, question, use_cache=True, include_wisdom=True):
        """
        Enhanced ask with Maya Wisdom
        
        Args:
            question: Legal question
            use_cache: Use caching
            include_wisdom: Include Maya Wisdom in context
        
        Returns:
            Enhanced result with wisdom
        """
        
        # Get wisdom if available and requested
        wisdom_response = None
        if include_wisdom and self.wisdom_available:
            try:
                wisdom_response = self.wisdom.process_legal_question(question)
                logger.info("Maya Wisdom response generated")
            except Exception as e:
                logger.warning(f"Maya Wisdom processing error: {e}")
        
        # Get standard result
        result = super().ask(question, use_cache)
        
        # Enhance result with wisdom
        if wisdom_response:
            result['wisdom'] = wisdom_response
            result['enhanced'] = True
            
            # Add wisdom to metadata
            result['metadata']['wisdom_type'] = wisdom_response.get('type', 'unknown')
            result['metadata']['wisdom_confidence'] = wisdom_response.get('confidence', 0.0)
        else:
            result['enhanced'] = False
        
        return result
    
    def print_answer(self, result):
        """Enhanced print with wisdom"""
        
        # Print wisdom if available
        if result.get('enhanced') and result.get('wisdom'):
            wisdom = result['wisdom']
            
            print(f"{'='*60}")
            print("🧠 MAYA WISDOM")
            print(f"{'='*60}\n")
            
            print(f"Type: {wisdom.get('type', 'N/A')}")
            print(f"Confidence: {wisdom.get('confidence', 0):.0%}\n")
            
            if 'answer' in wisdom:
                print(f"Basic Knowledge:")
                print(f"{wisdom['answer']}\n")
            
            if 'details' in wisdom:
                print(f"Details:")
                for key, value in wisdom['details'].items():
                    print(f"  • {key}: {value}")
                print()
        
        # Print standard answer
        super().print_answer(result)
    
    def get_stats(self):
        """Enhanced stats with wisdom info"""
        stats = super().get_stats()
        
        stats['wisdom'] = {
            'available': self.wisdom_available,
            'loaded': self.wisdom is not None
        }
        
        return stats

def create_enhanced_system(ai_provider='mock', api_key=None):
    """
    Helper function to create enhanced system
    
    Args:
        ai_provider: 'openai', 'deepseek', 'qodo', or 'mock'
        api_key: API key for the provider
    
    Returns:
        EnhancedVersaLaw2System instance
    """
    config = Config()
    config['ai_provider'] = ai_provider
    
    if api_key:
        if ai_provider == 'openai':
            config['openai_api_key'] = api_key
        elif ai_provider == 'deepseek':
            config['deepseek_api_key'] = api_key
        elif ai_provider == 'qodo':
            config['qodo_api_key'] = api_key
    
    return EnhancedVersaLaw2System(config)
