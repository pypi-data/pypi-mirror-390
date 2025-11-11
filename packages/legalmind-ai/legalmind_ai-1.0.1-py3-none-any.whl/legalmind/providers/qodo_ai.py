"""
Qodo AI Provider for LegalMind
"""
import os
import requests
from typing import Dict, Any, Optional

class QodoAIAnalyzer:
    """Qodo AI integration for legal analysis"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.qodo.ai/v1/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze(self, question: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze legal question using Qodo AI"""
        
        # Build prompt with legal context
        prompt = self._build_legal_prompt(question, context)
        
        payload = {
            "prompt": prompt,
            "max_tokens": 800,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_response(result, question)
            else:
                return {
                    "success": False,
                    "error": f"Qodo AI API error: {response.status_code}",
                    "provider": "qodo_ai"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "qodo_ai"
            }
    
    def _build_legal_prompt(self, question: str, context: Optional[Dict] = None) -> str:
        """Build legal analysis prompt"""
        base_prompt = f"""Anda adalah asisten hukum profesional Indonesia. Berikan analisis hukum yang akurat berdasarkan UU yang berlaku.

PERTANYAAN: {question}

JAWABAN HUKUM:"""
        
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            base_prompt = f"KONTEKS:\n{context_str}\n\n{base_prompt}"
            
        return base_prompt
    
    def _parse_response(self, result: Dict, question: str) -> Dict[str, Any]:
        """Parse Qodo AI response"""
        if 'choices' in result and len(result['choices']) > 0:
            answer = result['choices'][0].get('text', '').strip()
        elif 'text' in result:
            answer = result['text'].strip()
        else:
            answer = "Tidak dapat memproses jawaban."
        
        return {
            "success": True,
            "question": question,
            "answer": answer,
            "provider": "qodo_ai",
            "raw_response": result
        }
