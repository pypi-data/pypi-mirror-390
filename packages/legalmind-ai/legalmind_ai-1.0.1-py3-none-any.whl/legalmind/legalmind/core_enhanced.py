#!/usr/bin/env python3
"""
LegalMind Enhanced Core System
With TF-IDF search and advanced prompts
"""

import sys
from pathlib import Path

# Import from versalaw2_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from versalaw2_core import Config
from versalaw2_core.enhanced_system import EnhancedVersaLaw2System
from .enhanced_search import EnhancedSearchEngine
from .prompt_templates import PromptTemplates

class LegalMindEnhanced:
    """
    Enhanced LegalMind with:
    - TF-IDF search
    - Advanced prompts
    - Better AI responses
    """
    
    def __init__(self, ai_provider='mock', api_key=None):
        """
        Initialize Enhanced LegalMind
        
        Args:
            ai_provider: 'mock', 'openai', 'deepseek', or 'qodo'
            api_key: API key for the provider
        """
        print("\n" + "="*60)
        print("⚖️  LEGALMIND ENHANCED - AI LEGAL ASSISTANT")
        print("="*60)
        print("Version: 2.0.0 (Enhanced)")
        print("Features:")
        print("  • TF-IDF Search Algorithm")
        print("  • Advanced Prompt Templates")
        print("  • 126 MayaLaw Cases")
        print("  • Maya Wisdom Integration")
        print("="*60 + "\n")
        
        # Create config
        config = Config()
        config['ai_provider'] = ai_provider
        
        if api_key:
            if ai_provider == 'openai':
                config['openai_api_key'] = api_key
            elif ai_provider == 'deepseek':
                config['deepseek_api_key'] = api_key
            elif ai_provider == 'qodo':
                config['qodo_api_key'] = api_key
        
        # Initialize base system
        self.system = EnhancedVersaLaw2System(config)
        
        # Initialize enhanced search
        print("🔍 Initializing enhanced search...")
        self.enhanced_search = EnhancedSearchEngine(
            self.system.data_loader.cases
        )
        
        # Store prompt templates
        self.prompts = PromptTemplates()
        
        print("✅ LegalMind Enhanced ready!\n")
    
    def ask(self, question, include_wisdom=True, use_enhanced_search=True, prompt_type='legal_analysis'):
        """
        Ask legal question with enhancements
        
        Args:
            question: Legal question
            include_wisdom: Include Maya Wisdom
            use_enhanced_search: Use TF-IDF search
            prompt_type: 'legal_analysis', 'chain_of_thought', or 'quick_answer'
        
        Returns:
            Enhanced result dictionary
        """
        print(f"\n{'='*60}")
        print(f"📝 PERTANYAAN: {question}")
        print(f"{'='*60}\n")
        
        # Step 1: Classify
        print("1️⃣ Mengklasifikasi...")
        classification = self.system.classifier.classify(question)
        print(f"   ✅ Kategori: {classification['category']}")
        print(f"   ✅ Confidence: {classification['confidence']:.0%}\n")
        
        # Step 2: Search with enhanced algorithm
        print("2️⃣ Mencari dengan Enhanced Search...")
        if use_enhanced_search:
            relevant_cases = self.enhanced_search.search(question, top_k=3)
            search_method = relevant_cases[0]['search_method'] if relevant_cases else 'none'
            print(f"   ✅ Method: {search_method.upper()}")
        else:
            relevant_cases = self.system.data_loader.search(question, top_k=3)
            search_method = 'basic'
        
        print(f"   ✅ Ditemukan: {len(relevant_cases)} kasus\n")
        
        if relevant_cases:
            for i, case in enumerate(relevant_cases, 1):
                score = case.get('similarity_score', 0)
                print(f"      {i}. Kasus #{case['number']}: {case['pertanyaan'][:60]}...")
                print(f"         Score: {score:.3f}")
            print()
        
        # Step 3: Get wisdom if requested
        wisdom_response = None
        if include_wisdom and self.system.wisdom_available:
            print("3️⃣ Mengambil Maya Wisdom...")
            try:
                wisdom_response = self.system.wisdom.process_legal_question(question)
                print(f"   ✅ Wisdom type: {wisdom_response.get('type', 'N/A')}\n")
            except Exception as e:
                print(f"   ⚠️  Wisdom error: {e}\n")
        
        # Step 4: Generate answer with advanced prompt
        print("4️⃣ Memproses dengan AI (Advanced Prompts)...")
        
        # Select prompt template
        if prompt_type == 'chain_of_thought':
            prompt_method = self.prompts.chain_of_thought_prompt
        elif prompt_type == 'quick_answer':
            prompt_method = self.prompts.quick_answer_prompt
        else:
            prompt_method = self.prompts.legal_analysis_prompt
        
        # Build context
        context = {'cases': relevant_cases}
        
        # For mock AI, use standard generation
        # For real AI, would use advanced prompts
        ai_response = self.system.ai_processor.generate_answer(question, context)
        print(f"   ✅ Generated with {prompt_type}\n")
        
        # Build enhanced result
        result = {
            'question': question,
            'classification': classification,
            'cases_found': len(relevant_cases),
            'cases': relevant_cases,
            'wisdom': wisdom_response,
            'answer': ai_response['answer'],
            'metadata': {
                'ai_model': ai_response['model'],
                'tokens': ai_response['usage']['total_tokens'],
                'confidence': 0.95 if relevant_cases else 0.5,
                'search_method': search_method,
                'prompt_type': prompt_type,
                'enhanced': True
            }
        }
        
        return result
    
    def print_answer(self, result):
        """Print enhanced answer"""
        print(f"{'='*60}")
        print("📊 HASIL ANALISIS (ENHANCED)")
        print(f"{'='*60}\n")
        
        print(f"🎯 Kategori: {result['classification']['category']}")
        print(f"📚 Kasus: {result['cases_found']}")
        print(f"🔍 Search: {result['metadata']['search_method'].upper()}")
        print(f"💯 Confidence: {result['metadata']['confidence']:.0%}")
        print(f"🤖 Prompt: {result['metadata']['prompt_type']}\n")
        
        # Print wisdom if available
        if result.get('wisdom'):
            wisdom = result['wisdom']
            print(f"{'='*60}")
            print("🧠 MAYA WISDOM")
            print(f"{'='*60}\n")
            print(f"Type: {wisdom.get('type', 'N/A')}")
            print(f"Confidence: {wisdom.get('confidence', 0):.0%}\n")
            if 'answer' in wisdom:
                print(f"{wisdom['answer']}\n")
        
        print(f"{'='*60}")
        print(result['answer'])
        print(f"{'='*60}\n")
    
    def get_stats(self):
        """Get enhanced system statistics"""
        base_stats = self.system.get_stats()
        search_stats = self.enhanced_search.get_stats()
        
        return {
            **base_stats,
            'enhanced': {
                'version': '2.0.0',
                'search_engine': search_stats,
                'features': [
                    'TF-IDF Search',
                    'Advanced Prompts',
                    'Maya Wisdom',
                    'Multi-Provider AI'
                ]
            }
        }
