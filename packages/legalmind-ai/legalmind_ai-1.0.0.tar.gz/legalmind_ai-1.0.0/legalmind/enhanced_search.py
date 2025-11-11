#!/usr/bin/env python3
"""
Enhanced Search Algorithm
TF-IDF + Cosine Similarity for better relevance
"""

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn not installed. Using basic search.")

import numpy as np

class EnhancedSearchEngine:
    """
    Advanced search with TF-IDF and cosine similarity
    Falls back to basic search if sklearn not available
    """
    
    def __init__(self, cases):
        self.cases = cases
        self.use_tfidf = SKLEARN_AVAILABLE
        
        if self.use_tfidf:
            self._init_tfidf()
        else:
            print("ℹ️  Using basic keyword search")
    
    def _init_tfidf(self):
        """Initialize TF-IDF vectorizer"""
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
            
            # Build corpus from all case fields
            corpus = []
            for c in self.cases:
                text = " ".join([
                    c.get('pertanyaan', ''),
                    c.get('kasus', ''),
                    c.get('jawaban', ''),
                    c.get('analisis', ''),
                    " ".join(c.get('pasal', [])),
                ])
                corpus.append(text)
            
            # Fit and transform
            self.vectors = self.vectorizer.fit_transform(corpus)
            print(f"✅ Enhanced search initialized with {len(self.cases)} cases")
            print(f"   Features: {self.vectorizer.get_feature_names_out()[:10]}...")
        
        except Exception as e:
            print(f"⚠️  TF-IDF initialization failed: {e}")
            self.use_tfidf = False
    
    def search(self, query, top_k=3):
        """
        Search with TF-IDF similarity or fallback to basic
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            List of cases with similarity scores
        """
        if self.use_tfidf:
            return self._tfidf_search(query, top_k)
        else:
            return self._basic_search(query, top_k)
    
    def _tfidf_search(self, query, top_k):
        """TF-IDF based search"""
        try:
            # Transform query
            query_vec = self.vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vec, self.vectors)[0]
            
            # Get top results
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only return if similarity > 0
                    case = self.cases[idx].copy()
                    case['similarity_score'] = float(similarities[idx])
                    case['search_method'] = 'tfidf'
                    results.append(case)
            
            return results
        
        except Exception as e:
            print(f"⚠️  TF-IDF search failed: {e}, using basic search")
            return self._basic_search(query, top_k)
    
    def _basic_search(self, query, top_k):
        """Fallback basic keyword search"""
        query_lower = query.lower()
        keywords = [k for k in query_lower.split() if len(k) > 3]
        
        scored_cases = []
        for case in self.cases:
            score = 0
            
            # Search in pertanyaan
            if query_lower in case.get('pertanyaan', '').lower():
                score += 20
            
            # Search in kasus
            if query_lower in case.get('kasus', '').lower():
                score += 10
            
            # Search in jawaban
            if query_lower in case.get('jawaban', '').lower():
                score += 5
            
            # Keyword matching
            full_content = case.get('full_content', '').lower()
            for keyword in keywords:
                count = full_content.count(keyword)
                score += count * 2
            
            if score > 0:
                case_copy = case.copy()
                case_copy['similarity_score'] = score / 100.0  # Normalize
                case_copy['search_method'] = 'basic'
                scored_cases.append((score, case_copy))
        
        # Sort and return top k
        scored_cases.sort(reverse=True, key=lambda x: x[0])
        return [case for score, case in scored_cases[:top_k]]
    
    def get_stats(self):
        """Get search engine statistics"""
        return {
            'total_cases': len(self.cases),
            'search_method': 'tfidf' if self.use_tfidf else 'basic',
            'sklearn_available': SKLEARN_AVAILABLE
        }
