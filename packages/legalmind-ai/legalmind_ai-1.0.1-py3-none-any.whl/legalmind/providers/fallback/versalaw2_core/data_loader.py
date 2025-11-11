#!/usr/bin/env python3
"""
Enhanced MayaLaw Data Loader
Supports multiple markdown formats
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MayaLawDataLoader:
    """Enhanced data loader with multiple parsers"""
    
    def __init__(self, mayalaw_path="/root/dragon/global/mayalaw"):
        self.mayalaw_path = Path(mayalaw_path)
        self.cases = []
        self.stats = {
            'files_loaded': 0,
            'cases_loaded': 0,
            'errors': []
        }
        self.load_all_cases()
    
    def load_all_cases(self):
        """Load all study cases from MayaLaw"""
        files_to_load = [
            ("JAWABAN_LENGKAP_20_PERTANYAAN_HUKUM.md", "pertanyaan_format"),
            ("LAW_LIBRARY_BATCH_IV_ANSWERS.md", "qa_format"),
            ("LAW_LIBRARY_BATCH_V_FINAL.md", "qa_format"),
            ("LAW_LIBRARY_BATCH_IV_PART2.md", "qa_format"),
            ("ADVANCED_LEGAL_QUESTIONS_20_PART2.md", "pertanyaan_simple"),
        ]
        
        for filename, parser_type in files_to_load:
            filepath = self.mayalaw_path / filename
            if filepath.exists():
                try:
                    cases = self.parse_file(filepath, parser_type)
                    self.cases.extend(cases)
                    self.stats['files_loaded'] += 1
                    self.stats['cases_loaded'] += len(cases)
                    logger.info(f"✅ Loaded {len(cases)} cases from {filename}")
                    print(f"✅ Loaded {len(cases)} cases from {filename}")
                except Exception as e:
                    error_msg = f"Error loading {filename}: {e}"
                    self.stats['errors'].append(error_msg)
                    logger.error(error_msg)
                    print(f"⚠️  {error_msg}")
            else:
                logger.warning(f"File not found: {filename}")
        
        print(f"\n📚 Total: {len(self.cases)} study cases loaded from {self.stats['files_loaded']} files\n")
        logger.info(f"Total cases loaded: {len(self.cases)}")
    
    def parse_file(self, filepath: Path, parser_type: str) -> List[Dict]:
        """Parse file based on type"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if parser_type == "pertanyaan_format":
            return self.parse_pertanyaan_format(content, filepath.name)
        elif parser_type == "qa_format":
            return self.parse_qa_format(content, filepath.name)
        elif parser_type == "pertanyaan_simple":
            return self.parse_pertanyaan_simple(content, filepath.name)
        else:
            logger.warning(f"Unknown parser type: {parser_type}")
            return []
    
    def parse_pertanyaan_format(self, content: str, filename: str) -> List[Dict]:
        """Parse '## 📋 PERTANYAAN #N' format"""
        cases = []
        pattern = r'##\s+📋\s+PERTANYAAN\s+#(\d+)'
        parts = re.split(pattern, content)
        
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                case_num = parts[i]
                case_content = parts[i+1]
                case = self.parse_case_content(case_num, case_content, filename)
                if case:
                    cases.append(case)
        
        return cases
    
    def parse_qa_format(self, content: str, filename: str) -> List[Dict]:
        """Parse Q&A format like '**Q1:**'"""
        cases = []
        
        # Try multiple Q&A patterns
        patterns = [
            r'\*\*Q(\d+):\s*(.*?)\*\*',
            r'##\s+\*\*Q(\d+):',
            r'Q(\d+):\s+(.+?)(?=Q\d+:|$)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                case_num = match.group(1)
                # Get content after this Q until next Q or end
                start_pos = match.end()
                next_q = re.search(r'\*\*Q\d+:', content[start_pos:])
                end_pos = start_pos + next_q.start() if next_q else len(content)
                case_content = content[start_pos:end_pos]
                
                case = self.parse_qa_content(case_num, case_content, filename)
                if case:
                    cases.append(case)
            
            if cases:  # If we found cases with this pattern, stop trying others
                break
        
        return cases
    
    def parse_pertanyaan_simple(self, content: str, filename: str) -> List[Dict]:
        """Parse simple '## PERTANYAAN N' format"""
        cases = []
        pattern = r'##\s+PERTANYAAN\s+(\d+)'
        parts = re.split(pattern, content)
        
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                case_num = parts[i]
                case_content = parts[i+1]
                case = self.parse_case_content(case_num, case_content, filename)
                if case:
                    cases.append(case)
        
        return cases
    
    def parse_case_content(self, num: str, content: str, filename: str) -> Optional[Dict]:
        """Parse detailed case content with sections"""
        
        # Extract KASUS
        kasus_match = re.search(r'\*\*KASUS:\*\*\s*(.*?)(?=\*\*PERTANYAAN:|\*\*JAWABAN:|###|\Z)', content, re.DOTALL)
        kasus = kasus_match.group(1).strip() if kasus_match else ""
        
        # Extract PERTANYAAN
        pertanyaan_match = re.search(r'\*\*PERTANYAAN:\*\*\s*(.*?)(?=---|###|\*\*JAWABAN:|\Z)', content, re.DOTALL)
        pertanyaan = pertanyaan_match.group(1).strip() if pertanyaan_match else ""
        
        # Extract JAWABAN
        jawaban_match = re.search(r'###\s+⚖️\s+JAWABAN\s*(.*?)(?=###|\Z)', content, re.DOTALL)
        if not jawaban_match:
            jawaban_match = re.search(r'\*\*JAWABAN:\*\*\s*(.*?)(?=###|\Z)', content, re.DOTALL)
        jawaban = jawaban_match.group(1).strip() if jawaban_match else ""
        
        # Extract DASAR HUKUM
        dasar_hukum_match = re.search(r'###\s+📖\s+DASAR HUKUM\s*(.*?)(?=###|\Z)', content, re.DOTALL)
        dasar_hukum = dasar_hukum_match.group(1).strip() if dasar_hukum_match else ""
        
        # Extract ANALISIS
        analisis_match = re.search(r'###\s+🔍\s+ANALISIS\s*(.*?)(?=##|\Z)', content, re.DOTALL)
        analisis = analisis_match.group(1).strip() if analisis_match else ""
        
        # Extract references
        pasal = self.extract_pasal(content)
        uu = self.extract_uu(content)
        
        # Build case
        case = {
            'id': f'case_{num}',
            'number': num,
            'file': filename,
            'kasus': kasus[:500] if kasus else "",
            'pertanyaan': pertanyaan[:500] if pertanyaan else "",
            'jawaban': jawaban[:800] if jawaban else "",
            'dasar_hukum': dasar_hukum[:500] if dasar_hukum else "",
            'analisis': analisis[:1000] if analisis else "",
            'pasal': pasal,
            'uu': uu,
            'full_content': content[:2000]
        }
        
        # Only return if we have meaningful content
        if kasus or pertanyaan or jawaban:
            return case
        return None
    
    def parse_qa_content(self, num: str, content: str, filename: str) -> Optional[Dict]:
        """Parse Q&A style content"""
        
        # For Q&A format, the question is usually at the start
        lines = content.strip().split('\n')
        question = lines[0].strip() if lines else ""
        
        # Answer is usually after "JAWABAN:" or "A:"
        answer_match = re.search(r'(?:JAWABAN:|A:)\s*(.*?)(?=\*\*Q\d+:|\Z)', content, re.DOTALL)
        answer = answer_match.group(1).strip() if answer_match else content[:500]
        
        # Extract references
        pasal = self.extract_pasal(content)
        uu = self.extract_uu(content)
        
        case = {
            'id': f'case_{num}',
            'number': num,
            'file': filename,
            'kasus': "",
            'pertanyaan': question[:500],
            'jawaban': answer[:800],
            'dasar_hukum': "",
            'analisis': "",
            'pasal': pasal,
            'uu': uu,
            'full_content': content[:2000]
        }
        
        if question or answer:
            return case
        return None
    
    def extract_pasal(self, content: str) -> List[str]:
        """Extract Pasal references"""
        pasal_patterns = [
            r'Pasal\s+(\d+(?:\s+ayat\s+\(\d+\))?)\s+([A-Z]+)',
            r'Pasal\s+(\d+)',
        ]
        
        pasal_list = []
        for pattern in pasal_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        pasal_list.append(f"Pasal {match[0]} {match[1]}")
                    else:
                        pasal_list.append(f"Pasal {match[0]}")
                else:
                    pasal_list.append(f"Pasal {match}")
        
        # Remove duplicates
        seen = set()
        unique = []
        for p in pasal_list:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        
        return unique[:10]
    
    def extract_uu(self, content: str) -> List[str]:
        """Extract UU references"""
        uu_patterns = [
            r'UU\s+No\.?\s*(\d+)\s+Tahun\s+(\d+)',
            r'UU\s+No\.?\s*(\d+)/(\d+)',
        ]
        
        uu_list = []
        for pattern in uu_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                uu_list.append(f"UU No. {match[0]} Tahun {match[1]}")
        
        return list(set(uu_list))[:5]
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant cases"""
        query_lower = query.lower()
        
        scored_cases = []
        for case in self.cases:
            score = self.calculate_relevance(query_lower, case)
            if score > 0:
                scored_cases.append((score, case))
        
        scored_cases.sort(reverse=True, key=lambda x: x[0])
        return [case for score, case in scored_cases[:top_k]]
    
    def calculate_relevance(self, query: str, case: Dict) -> float:
        """Calculate relevance score"""
        score = 0.0
        
        # High weight for pertanyaan
        if query in case.get('pertanyaan', '').lower():
            score += 20
        
        # Medium weight for kasus
        if query in case.get('kasus', '').lower():
            score += 10
        
        # Lower weight for jawaban/analisis
        if query in case.get('jawaban', '').lower():
            score += 5
        if query in case.get('analisis', '').lower():
            score += 3
        
        # Keyword matching
        keywords = [k for k in query.split() if len(k) > 3]
        for keyword in keywords:
            full_content = case.get('full_content', '').lower()
            count = full_content.count(keyword)
            score += count * 2
        
        return score
    
    def get_stats(self) -> Dict:
        """Get loading statistics"""
        return {
            'total_cases': len(self.cases),
            'files_loaded': self.stats['files_loaded'],
            'cases_by_file': {},
            'errors': self.stats['errors']
        }
