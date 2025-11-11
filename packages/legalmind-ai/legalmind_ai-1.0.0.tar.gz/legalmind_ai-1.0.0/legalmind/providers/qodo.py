#!/usr/bin/env python3
"""
Demo VersaLaw2 with Qodo.ai
250 Free Calls Available!
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from versalaw2_core.enhanced_system import create_enhanced_system

def main():
    """Run Qodo.ai demo"""
    
    print("\n" + "="*60)
    print("⚖️  VERSALAW2 WITH QODO.AI")
    print("="*60)
    print("🎁 250 FREE CALLS AVAILABLE!")
    print("="*60)
    print("\nPowered by:")
    print("  • VersaLaw2 Framework (21 analyzers)")
    print("  • MayaLaw Database (126 study cases)")
    print("  • Maya Wisdom Processor (legal knowledge)")
    print("  • Qodo.ai API (250 free calls!)")
    print("="*60 + "\n")
    
    # Get API key
    api_key = os.getenv('QODO_API_KEY')
    
    if not api_key:
        print("⚠️  QODO_API_KEY not found in environment variables")
        print("\n📝 To use Qodo.ai:")
        print("   1. Get free API key from: https://qodo.ai")
        print("   2. Set environment variable:")
        print("      export QODO_API_KEY='your-api-key-here'")
        print("   3. Run this script again")
        print("\n💡 Or run with mock AI for testing:")
        print("   python demo_versalaw2.py")
        print()
        return
    
    # Initialize with Qodo.ai
    print("🚀 Initializing with Qodo.ai...")
    try:
        system = create_enhanced_system(
            ai_provider='qodo',
            api_key=api_key
        )
    except Exception as e:
        print(f"❌ Error initializing Qodo.ai: {e}")
        print("\n💡 Falling back to mock AI...")
        system = create_enhanced_system(
            ai_provider='mock',
            api_key=None
        )
    
    # Demo questions
    demo_questions = [
        "Apa syarat sah perjanjian?",
        "Apakah hakim boleh menjatuhkan pidana di bawah minimum?",
        "Bagaimana prosedur mengajukan gugatan perceraian?",
    ]
    
    print("\n📋 Demo Questions:\n")
    for i, q in enumerate(demo_questions, 1):
        print(f"{i}. {q}")
    
    print("\n" + "="*60)
    print("Starting analysis with Qodo.ai...")
    print("="*60 + "\n")
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{'#'*60}")
        print(f"QODO.AI DEMO {i}/{len(demo_questions)}")
        print(f"{'#'*60}\n")
        
        # Ask question
        result = system.ask(question, include_wisdom=True)
        
        # Print answer
        system.print_answer(result)
        
        # Show API info
        print(f"\n💡 API Info:")
        print(f"   Provider: {result['metadata']['ai_model']}")
        print(f"   Tokens used: {result['metadata']['tokens']}")
        
        if system.ai_processor.provider == 'qodo':
            remaining = 250 - i  # Approximate
            print(f"   🎁 Estimated free calls remaining: ~{remaining}")
        
        print()
    
    # Show statistics
    print("\n" + "="*60)
    print("📊 SESSION STATISTICS")
    print("="*60)
    
    stats = system.get_stats()
    print(f"\n🤖 AI Provider: {stats['system']['ai_provider']}")
    print(f"💾 Cache: {'Enabled' if stats['system']['cache_enabled'] else 'Disabled'}")
    print(f"📚 MayaLaw Cases: {stats['data']['total_cases']}")
    print(f"📁 Files Loaded: {stats['data']['files_loaded']}")
    print(f"🧠 Maya Wisdom: {'Available' if stats['wisdom']['available'] else 'Not Available'}")
    
    if system.ai_processor.provider == 'qodo':
        print(f"\n🎁 Qodo.ai Free Calls:")
        print(f"   Total available: 250")
        print(f"   Used in this demo: {len(demo_questions)}")
        print(f"   Estimated remaining: ~{250 - len(demo_questions)}")
    
    print("\n" + "="*60)
    print("✅ QODO.AI DEMO COMPLETED!")
    print("="*60)
    
    print("\n💡 Benefits of Qodo.ai:")
    print("   ✅ 250 free calls for testing")
    print("   ✅ Real AI responses (not mock)")
    print("   ✅ No credit card required")
    print("   ✅ Perfect for evaluation")
    
    print("\n🚀 Next Steps:")
    print("   1. Continue testing with remaining free calls")
    print("   2. Evaluate quality vs DeepSeek/OpenAI")
    print("   3. Choose best provider for production")
    
    print("\n📊 Cost Comparison:")
    print("   • Qodo.ai: 250 free calls, then check pricing")
    print("   • DeepSeek: $0.28 per 1,000 calls (CHEAPEST!)")
    print("   • OpenAI: $20 per 1,000 calls")
    print("   • Mock: Free (testing only)")
    
    print()

if __name__ == "__main__":
    main()
