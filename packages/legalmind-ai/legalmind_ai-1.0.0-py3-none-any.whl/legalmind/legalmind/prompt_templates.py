#!/usr/bin/env python3
"""
Advanced Prompt Templates
Optimized prompts for better AI responses
"""

class PromptTemplates:
    """Collection of optimized prompt templates"""
    
    @staticmethod
    def legal_analysis_prompt(question, context_cases):
        """
        Comprehensive legal analysis prompt
        
        Args:
            question: User's legal question
            context_cases: Relevant cases from MayaLaw
        
        Returns:
            Optimized prompt string
        """
        
        # Build context from cases
        context = ""
        for i, case in enumerate(context_cases[:2], 1):
            context += f"""
KASUS REFERENSI #{i}:
Pertanyaan: {case.get('pertanyaan', '')[:200]}
Jawaban: {case.get('jawaban', '')[:300]}
Dasar Hukum: {', '.join(case.get('pasal', [])[:3])}
UU: {', '.join(case.get('uu', [])[:2])}
---
"""
        
        return f"""
Anda adalah ahli hukum Indonesia senior dengan pengalaman 20+ tahun di berbagai bidang hukum.

KONTEKS DARI DATABASE MAYALAW:
{context}

PERTANYAAN KLIEN:
{question}

INSTRUKSI ANALISIS:
1. Baca pertanyaan dengan teliti dan identifikasi isu hukum utama
2. Analisis konteks dari database MayaLaw yang relevan
3. Identifikasi Pasal dan UU yang spesifik dan berlaku
4. Berikan reasoning yang jelas dan logis
5. Sertakan confidence level dengan justifikasi

FORMAT JAWABAN (WAJIB IKUTI):

## 🎯 RINGKASAN SINGKAT
[Jawaban dalam 1-2 kalimat yang langsung menjawab pertanyaan]

## ⚖️ ANALISIS HUKUM
[Analisis mendalam dengan reasoning step-by-step]

## 📖 DASAR HUKUM
**Pasal yang Relevan:**
- Pasal [nomor] [nama UU]: [penjelasan singkat]
- [tambahkan pasal lain jika relevan]

**Undang-Undang:**
- UU No. [nomor] Tahun [tahun] tentang [judul]
- [tambahkan UU lain jika relevan]

## 💡 REKOMENDASI PRAKTIS
1. [Langkah konkret yang bisa diambil]
2. [Pertimbangan penting]
3. [Alternatif jika ada]

## 📊 TINGKAT KEYAKINAN
[X%] - [Alasan spesifik mengapa confidence level ini, berdasarkan kekuatan dasar hukum dan relevansi kasus]

## 📚 REFERENSI
- Berdasarkan Kasus MayaLaw #{case.get('number', 'N/A')}
- [Sumber lain jika ada]

PENTING:
- Gunakan bahasa yang jelas dan mudah dipahami
- Hindari jargon hukum yang tidak perlu
- Berikan contoh konkret jika membantu
- Jika tidak yakin, katakan dengan jujur

Mulai analisis Anda:
"""
    
    @staticmethod
    def chain_of_thought_prompt(question, context_cases):
        """
        Chain-of-thought reasoning prompt
        
        Args:
            question: User's legal question
            context_cases: Relevant cases
        
        Returns:
            Chain-of-thought prompt
        """
        
        context = "\n".join([
            f"- Kasus #{c.get('number')}: {c.get('pertanyaan', '')[:100]}"
            for c in context_cases[:3]
        ])
        
        return f"""
Gunakan chain-of-thought reasoning untuk menjawab pertanyaan hukum ini secara sistematis.

PERTANYAAN: {question}

KONTEKS DARI MAYALAW:
{context}

PROSES ANALISIS STEP-BY-STEP:

**Langkah 1: Identifikasi Isu Hukum**
[Tuliskan dengan jelas isu hukum apa yang perlu dijawab]

**Langkah 2: Cari Dasar Hukum**
[Identifikasi Pasal dan UU yang relevan dari konteks atau pengetahuan hukum]

**Langkah 3: Analisis Penerapan**
[Bagaimana hukum diterapkan pada situasi ini? Apa implikasinya?]

**Langkah 4: Pertimbangkan Preseden**
[Apakah ada kasus serupa di database? Apa pembelajaran dari kasus tersebut?]

**Langkah 5: Evaluasi Alternatif**
[Apakah ada interpretasi atau pendekatan alternatif yang perlu dipertimbangkan?]

**Langkah 6: Kesimpulan**
[Jawaban final dengan confidence level dan alasan]

Mulai analisis step-by-step Anda:
"""
    
    @staticmethod
    def quick_answer_prompt(question, context_cases):
        """
        Quick answer prompt for simple questions
        
        Args:
            question: User's legal question
            context_cases: Relevant cases
        
        Returns:
            Quick answer prompt
        """
        
        if context_cases:
            case = context_cases[0]
            context = f"""
Referensi: Kasus #{case.get('number')}
Pertanyaan serupa: {case.get('pertanyaan', '')[:150]}
Jawaban: {case.get('jawaban', '')[:200]}
Pasal: {', '.join(case.get('pasal', [])[:2])}
"""
        else:
            context = "Tidak ada kasus serupa di database."
        
        return f"""
Berikan jawaban singkat dan jelas untuk pertanyaan hukum ini.

PERTANYAAN: {question}

KONTEKS:
{context}

FORMAT JAWABAN:

**Jawaban Singkat:**
[1-2 kalimat yang langsung menjawab]

**Dasar Hukum:**
[Pasal dan UU yang relevan]

**Catatan:**
[Informasi tambahan penting jika ada]

Jawab dengan singkat dan jelas:
"""
    
    @staticmethod
    def document_analysis_prompt(document_text, question):
        """
        Prompt for analyzing legal documents
        
        Args:
            document_text: Text from uploaded document
            question: Specific question about the document
        
        Returns:
            Document analysis prompt
        """
        
        return f"""
Anda adalah ahli hukum yang diminta menganalisis dokumen legal.

DOKUMEN:
{document_text[:2000]}
[... dokumen dipotong untuk efisiensi ...]

PERTANYAAN TENTANG DOKUMEN:
{question}

INSTRUKSI ANALISIS:
1. Baca dokumen dengan teliti
2. Identifikasi klausul-klausul penting
3. Cari potensi masalah atau risiko
4. Jawab pertanyaan spesifik yang diajukan

FORMAT JAWABAN:

## 📄 RINGKASAN DOKUMEN
[Ringkasan singkat isi dokumen]

## 🔍 ANALISIS KLAUSUL PENTING
[Klausul-klausul yang perlu diperhatikan]

## ⚠️ POTENSI RISIKO
[Risiko atau masalah yang teridentifikasi]

## 💡 JAWABAN PERTANYAAN
[Jawaban spesifik untuk pertanyaan yang diajukan]

## 📋 REKOMENDASI
[Saran perbaikan atau tindakan yang perlu diambil]

Mulai analisis dokumen:
"""
    
    @staticmethod
    def comparative_analysis_prompt(question, answers_from_models):
        """
        Prompt for comparing answers from multiple AI models
        
        Args:
            question: Original question
            answers_from_models: Dict of model_name: answer
        
        Returns:
            Comparative analysis prompt
        """
        
        answers_text = "\n\n".join([
            f"**{model}:**\n{answer[:500]}"
            for model, answer in answers_from_models.items()
        ])
        
        return f"""
Anda diminta membandingkan beberapa jawaban dari AI models berbeda untuk pertanyaan hukum yang sama.

PERTANYAAN ORIGINAL:
{question}

JAWABAN DARI BERBAGAI MODEL:
{answers_text}

TUGAS ANDA:
1. Bandingkan kualitas setiap jawaban
2. Identifikasi perbedaan pendapat jika ada
3. Tentukan jawaban mana yang paling akurat
4. Berikan jawaban final yang menggabungkan yang terbaik

FORMAT ANALISIS:

## 📊 PERBANDINGAN JAWABAN
[Ringkasan perbedaan dan persamaan]

## ✅ KELEBIHAN SETIAP JAWABAN
[Apa yang baik dari masing-masing jawaban]

## ⚠️ KELEMAHAN YANG TERIDENTIFIKASI
[Kesalahan atau kekurangan yang ditemukan]

## 🎯 JAWABAN FINAL (BEST OF ALL)
[Jawaban terbaik yang menggabungkan semua insight]

## 💯 CONFIDENCE LEVEL
[Tingkat keyakinan dengan alasan]

Mulai analisis komparatif:
"""
