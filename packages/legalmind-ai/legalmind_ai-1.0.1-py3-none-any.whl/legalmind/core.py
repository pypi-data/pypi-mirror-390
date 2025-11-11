"""
LegalMind Core - AI Legal Assistant
"""
import os
import json
from typing import Dict, Any, Optional
from .providers.qodo_ai import QodoAIAnalyzer
from .providers.fallback.enhanced_system import create_enhanced_system

class LegalMind:
    """
    Main LegalMind AI Legal Assistant
    """
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "auto"):
        self.api_key = api_key
        self.provider = provider
        self._setup_providers()
        
    def _setup_providers(self):
        """Initialize AI providers"""
        # Qodo AI provider
        if self.api_key and self.provider in ["auto", "qodo"]:
            try:
                self.qodo_analyzer = QodoAIAnalyzer(self.api_key)
                self.has_qodo = True
            except Exception as e:
                print(f"Qodo AI initialization failed: {e}")
                self.has_qodo = False
        else:
            self.has_qodo = False
        
        # Fallback provider (VersaLaw2)
        self.fallback_system = create_enhanced_system(ai_provider='mock')
        
    def analyze(self, question: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze legal question
        
        Args:
            question: Legal question to analyze
            context: Additional context (optional)
            
        Returns:
            Analysis results
        """
        # Try Qodo AI first if available
        if self.has_qodo:
            try:
                result = self.qodo_analyzer.analyze(question, context)
                result["provider"] = "qodo_ai"
                return result
            except Exception as e:
                print(f"Qodo AI analysis failed: {e}, falling back...")
        
        # Fallback to VersaLaw2
        result = self.fallback_system.ask(question)
        result["provider"] = "versalaw2_fallback"
        return result
    
    def batch_analyze(self, questions: list, context: Optional[Dict] = None) -> list:
        """
        Analyze multiple legal questions
        
        Args:
            questions: List of legal questions
            context: Additional context (optional)
            
        Returns:
            List of analysis results
        """
        results = []
        for question in questions:
            results.append(self.analyze(question, context))
        return results

# Convenience function
def create_analyzer(api_key: Optional[str] = None, **kwargs):
    """Create a LegalMind analyzer instance"""
    return LegalMind(api_key=api_key, **kwargs)
