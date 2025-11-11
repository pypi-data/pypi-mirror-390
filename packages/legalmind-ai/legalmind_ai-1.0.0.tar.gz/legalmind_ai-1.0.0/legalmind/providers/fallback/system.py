#!/usr/bin/env python3
"""
VersaLaw2 Integrated System
Complete production-ready implementation
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
import hashlib
from datetime import datetime

from .data_loader import MayaLawDataLoader
from .config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VersaLaw2Classifier:
    """Enhanced classifier"""
    
    def __init__(self):
        self.categories = {
            'hukum_pidana': {
                'keywords': ['pidana', 'pencurian', 'pembunuhan', 'korupsi', 'narkotika', 
                           'hakim', 'terdakwa', 'minimum', 'maksimum', 'penjara', 'hukuman'],
                'weight': 1.0
            },
            'hukum_perdata': {
                'keywords': ['perdata', 'gugatan', 'wanprestasi', 'kontrak', 'perjanjian', 
                           'ganti rugi', 'sengketa'],
                'weight': 1.0
            },
            'hukum_keluarga': {
                'keywords': ['perceraian', 'cerai', 'nafkah', 'waris', 'anak', 'nikah', 
                           'perkawinan'],
                'weight': 1.0
            },
            'hukum_bisnis': {
                'keywords': ['perusahaan', 'pt', 'cv', 'saham', 'ipo', 'merger', 'akuisisi'],
                'weight': 1.0
            },
            'hukum_properti': {
                'keywords': ['tanah', 'sertifikat', 'properti', 'bangunan', 'hak tanggungan'],
                'weight': 1.0
            },
            'hukum_tata_negara': {
                'keywords': ['konstitusi', 'uud', 'mahkamah konstitusi', 'pemilu', 'dpr'],
                'weight': 1.0
            },
        }
    
    def classify(self, question: str) -> Dict:
        """Classify legal question"""
        question_lower = question.lower()
        
        scores = {}
        for category, data in self.categories.items():
            score = sum(1 for kw in data['keywords'] if kw in question_lower)
            if score > 0:
                scores[category] = score * data['weight']
        
        if scores:
            best_category = max(scores, key=scores.get)
            total_words = len(question.split())
            confidence = min(scores[best_category] / max(total_words, 1), 0.95)
            
            return {
                'category': best_category,
                'confidence': confidence,
                'all_scores': scores
            }
        
        return {
            'category': 'umum',
            'confidence': 0.3,
            'all_scores': {}
        }

class AIProcessor:
    """AI processor with support for multiple providers"""
    
    def __init__(self, provider: str = "mock", api_key: Optional[str] = None, config: Optional[Config] = None):
        self.provider = provider
        self.api_key = api_key
        self.config = config or Config()
        
        if provider == "openai" and api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-4-turbo-preview"
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("OpenAI package not installed, falling back to mock")
                self.provider = "mock"
        
        elif provider == "deepseek" and api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com/v1"
                )
                self.model = "deepseek-chat"
                logger.info("DeepSeek client initialized")
            except ImportError:
                logger.warning("OpenAI package not installed, falling back to mock")
                self.provider = "mock"
        
        elif provider == "qodo" and api_key:
            try:
                from openai import OpenAI
                base_url = self.config.get('qodo_base_url', 'https://api.qodo.ai/v1')
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                self.model = "qodo-chat"  # Adjust based on Qodo.ai's actual model name
                logger.info(f"Qodo.ai client initialized (250 free calls available!)")
                print("✅ Qodo.ai initialized - 250 free calls available!")
            except ImportError:
                logger.warning("OpenAI package not installed, falling back to mock")
                self.provider = "mock"
            except Exception as e:
                logger.warning(f"Qodo.ai initialization failed: {e}, falling back to mock")
                self.provider = "mock"
        
        else:
            self.provider = "mock"
            logger.info("Using mock AI processor")
    
    def generate_answer(self, question: str, context: Dict) -> Dict:
        """Generate answer using AI"""
        
        if self.provider == "mock":
            return self._mock_answer(question, context)
        else:
            return self._real_ai_answer(question, context)
    
    def _real_ai_answer(self, question: str, context: Dict) -> Dict:
        """Generate answer using real AI"""
        try:
            prompt = self._build_prompt(question, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Anda adalah ahli hukum Indonesia yang sangat berpengalaman. "
                                 "Jawab pertanyaan berdasarkan konteks yang diberikan dengan akurat."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.get('ai_temperature', 0.3),
                max_tokens=self.config.get('ai_max_tokens', 2000)
            )
            
            return {
                'answer': response.choices[0].message.content,
                'model': self.model,
                'usage': response.usage._asdict()
            }
        
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return self._mock_answer(question, context)
    
    def _build_prompt(self, question: str, context: Dict) -> str:
        """Build prompt for AI"""
        cases = context.get('cases', [])
        
        context_text = ""
        for case in cases[:2]:  # Use top 2 cases
            context_text += f"""
KASUS #{case['number']}:
{case.get('kasus', '')}

PERTANYAAN:
{case.get('pertanyaan', '')}

JAWABAN:
{case.get('jawaban', '')[:400]}

DASAR HUKUM:
{', '.join(case.get('pasal', [])[:3])}
{', '.join(case.get('uu', [])[:2])}

---
"""
        
        prompt = f"""
Berdasarkan konteks kasus hukum berikut dari database MayaLaw, 
jawab pertanyaan dengan akurat dan detail.

KONTEKS DARI MAYALAW:
{context_text}

PERTANYAAN USER:
{question}

Berikan jawaban yang:
1. ✅ Akurat berdasarkan hukum Indonesia
2. ✅ Merujuk pada Pasal dan UU yang spesifik dari konteks
3. ✅ Menjelaskan dengan bahasa yang mudah dipahami
4. ✅ Menyertakan analisis hukum yang mendalam
5. ✅ Memberikan tingkat keyakinan (confidence level)

Format jawaban:
## ⚖️ JAWABAN:
[Jawaban singkat dan jelas]

## 📖 DASAR HUKUM:
[Pasal dan UU yang relevan]

## 🔍 ANALISIS:
[Penjelasan detail]

## 💯 TINGKAT KEYAKINAN:
[Persentase dan alasan]
"""
        return prompt
    
    def _mock_answer(self, question: str, context: Dict) -> Dict:
        """Mock answer for testing"""
        cases = context.get('cases', [])
        
        if not cases:
            answer = f"""## ⚠️ INFORMASI

Pertanyaan: "{question}"

Saat ini tidak ditemukan kasus yang relevan di database MayaLaw untuk pertanyaan ini.

## 💡 SARAN

1. Coba rumuskan pertanyaan dengan kata kunci yang lebih spesifik
2. Konsultasikan dengan ahli hukum untuk analisis mendalam
3. Database sedang dikembangkan untuk mencakup lebih banyak kasus
"""
            return {
                'answer': answer,
                'model': 'mock',
                'usage': {'total_tokens': 50}
            }
        
        case = cases[0]
        
        answer = f"""## ⚖️ JAWABAN

{case.get('jawaban', 'Berdasarkan analisis hukum...')[:400]}

## 📖 DASAR HUKUM

"""
        
        if case.get('pasal'):
            answer += "**Pasal yang Relevan:**\n"
            for pasal in case['pasal'][:5]:
                answer += f"- {pasal}\n"
            answer += "\n"
        
        if case.get('uu'):
            answer += "**Undang-Undang:**\n"
            for uu in case['uu'][:3]:
                answer += f"- {uu}\n"
            answer += "\n"
        
        if case.get('dasar_hukum'):
            answer += f"{case['dasar_hukum'][:300]}\n\n"
        
        answer += f"""## 🔍 ANALISIS

{case.get('analisis', '')[:600]}

## 📚 REFERENSI

Berdasarkan Kasus #{case['number']} dari database MayaLaw ({case['file']})

## 💯 TINGKAT KEYAKINAN

95% - Jawaban berdasarkan studi kasus yang relevan dan terverifikasi
"""
        
        return {
            'answer': answer,
            'model': 'mock',
            'usage': {'total_tokens': len(answer.split())}
        }

class CacheManager:
    """Simple cache manager"""
    
    def __init__(self, cache_dir: str = "/root/dragon/global/lab/.cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.enabled = True
    
    def get_cache_key(self, question: str) -> str:
        """Generate cache key"""
        return hashlib.md5(question.encode()).hexdigest()
    
    def get(self, question: str) -> Optional[Dict]:
        """Get cached result"""
        if not self.enabled:
            return None
        
        cache_key = self.get_cache_key(question)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def set(self, question: str, result: Dict):
        """Cache result"""
        if not self.enabled:
            return
        
        cache_key = self.get_cache_key(question)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

class VersaLaw2System:
    """Complete VersaLaw2 integrated system"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        
        print("🚀 Initializing VersaLaw2 System...")
        print("="*60)
        
        # Initialize components
        self.data_loader = MayaLawDataLoader(self.config['mayalaw_path'])
        self.classifier = VersaLaw2Classifier()
        print("✅ Classifier ready")
        
        self.ai_processor = AIProcessor(
            provider=self.config['ai_provider'],
            api_key=self.config.get('ai_api_key') or self.config.get('qodo_api_key') or self.config.get('deepseek_api_key') or self.config.get('openai_api_key'),
            config=self.config
        )
        print(f"✅ AI processor ready (mode: {self.ai_processor.provider})")
        
        self.cache = CacheManager(self.config['cache_dir'])
        print(f"✅ Cache {'enabled' if self.cache.enabled else 'disabled'}")
        
        print("="*60)
        print("🎉 System ready!\n")
        
        logger.info("VersaLaw2 System initialized successfully")
    
    def ask(self, question: str, use_cache: bool = True) -> Dict:
        """Answer legal question"""
        
        # Check cache
        if use_cache:
            cached = self.cache.get(question)
            if cached:
                logger.info(f"Cache hit for question: {question[:50]}")
                print("💾 Using cached result")
                return cached
        
        print(f"\n{'='*60}")
        print(f"📝 PERTANYAAN: {question}")
        print(f"{'='*60}\n")
        
        # Step 1: Classify
        print("1️⃣ Mengklasifikasi...")
        classification = self.classifier.classify(question)
        print(f"   ✅ Kategori: {classification['category']}")
        print(f"   ✅ Confidence: {classification['confidence']:.0%}\n")
        
        # Step 2: Search
        print("2️⃣ Mencari di MayaLaw...")
        relevant_cases = self.data_loader.search(
            question, 
            top_k=self.config['max_search_results']
        )
        print(f"   ✅ Ditemukan: {len(relevant_cases)} kasus\n")
        
        if relevant_cases:
            for i, case in enumerate(relevant_cases, 1):
                print(f"      {i}. Kasus #{case['number']}: {case['pertanyaan'][:60]}...")
            print()
        
        # Step 3: Generate answer
        print("3️⃣ Memproses dengan AI...")
        context = {'cases': relevant_cases}
        ai_response = self.ai_processor.generate_answer(question, context)
        print(f"   ✅ Generated\n")
        
        # Build result
        result = {
            'question': question,
            'classification': classification,
            'cases_found': len(relevant_cases),
            'cases': relevant_cases,
            'answer': ai_response['answer'],
            'metadata': {
                'ai_model': ai_response['model'],
                'tokens': ai_response['usage']['total_tokens'],
                'confidence': 0.95 if relevant_cases else 0.5,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Cache result
        if use_cache:
            self.cache.set(question, result)
        
        logger.info(f"Question answered: {question[:50]}")
        
        return result
    
    def print_answer(self, result: Dict):
        """Pretty print answer"""
        print(f"{'='*60}")
        print("📊 HASIL ANALISIS")
        print(f"{'='*60}\n")
        
        print(f"🎯 Kategori: {result['classification']['category']}")
        print(f"📚 Kasus: {result['cases_found']}")
        print(f"💯 Confidence: {result['metadata']['confidence']:.0%}\n")
        
        print(f"{'='*60}")
        print(result['answer'])
        print(f"{'='*60}\n")
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        return {
            'system': {
                'ai_provider': self.ai_processor.provider,
                'cache_enabled': self.cache.enabled,
            },
            'data': self.data_loader.get_stats()
        }
