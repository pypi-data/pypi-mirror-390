#!/usr/bin/env python3
"""
LegalMind REST API Server
FastAPI implementation with all features
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from legalmind.core_enhanced import LegalMindEnhanced

# Initialize FastAPI
app = FastAPI(
    title="LegalMind API",
    description="AI-Powered Legal Assistant with Enhanced Features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system instance
system: Optional[LegalMindEnhanced] = None

# Request/Response Models
class QuestionRequest(BaseModel):
    question: str = Field(..., description="Legal question to ask")
    include_wisdom: bool = Field(True, description="Include Maya Wisdom")
    use_enhanced_search: bool = Field(True, description="Use TF-IDF search")
    prompt_type: str = Field('legal_analysis', description="Prompt type: legal_analysis, chain_of_thought, quick_answer")
    ai_provider: Optional[str] = Field(None, description="AI provider: mock, openai, deepseek, qodo")
    api_key: Optional[str] = Field(None, description="API key for the provider")

class QuestionResponse(BaseModel):
    success: bool
    data: dict
    message: Optional[str] = None
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str
    cases_loaded: int
    ai_provider: str
    enhanced: bool
    timestamp: str

class StatsResponse(BaseModel):
    success: bool
    data: dict
    timestamp: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global system
    print("\n" + "="*60)
    print("🚀 Starting LegalMind API Server...")
    print("="*60)
    
    system = LegalMindEnhanced(ai_provider='mock')
    
    print("="*60)
    print("✅ LegalMind API Server ready!")
    print("📡 Listening on http://0.0.0.0:8000")
    print("📚 Docs: http://0.0.0.0:8000/docs")
    print("="*60 + "\n")

# Root endpoint
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "LegalMind API",
        "version": "2.0.0",
        "description": "AI-Powered Legal Assistant",
        "features": [
            "126 MayaLaw cases",
            "TF-IDF search",
            "Advanced prompts",
            "Maya Wisdom",
            "4 AI providers"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "ask": "/api/v1/ask",
            "stats": "/api/v1/stats",
            "cases": "/api/v1/cases"
        },
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    stats = system.get_stats()
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        cases_loaded=stats['data']['total_cases'],
        ai_provider=stats['system']['ai_provider'],
        enhanced=True,
        timestamp=datetime.now().isoformat()
    )

# Ask question
@app.post("/api/v1/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask legal question
    
    - **question**: Legal question to ask
    - **include_wisdom**: Include Maya Wisdom in response
    - **use_enhanced_search**: Use TF-IDF search algorithm
    - **prompt_type**: Type of prompt (legal_analysis, chain_of_thought, quick_answer)
    """
    try:
        # Use provided AI provider if specified
        if request.ai_provider and request.api_key:
            temp_system = LegalMindEnhanced(
                ai_provider=request.ai_provider,
                api_key=request.api_key
            )
            result = temp_system.ask(
                request.question,
                include_wisdom=request.include_wisdom,
                use_enhanced_search=request.use_enhanced_search,
                prompt_type=request.prompt_type
            )
        else:
            result = system.ask(
                request.question,
                include_wisdom=request.include_wisdom,
                use_enhanced_search=request.use_enhanced_search,
                prompt_type=request.prompt_type
            )
        
        # Clean up full_content from cases
        for case in result.get('cases', []):
            case.pop('full_content', None)
        
        return QuestionResponse(
            success=True,
            data=result,
            message="Question answered successfully",
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )

# Get statistics
@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_statistics():
    """Get system statistics"""
    try:
        stats = system.get_stats()
        
        return StatsResponse(
            success=True,
            data=stats,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting statistics: {str(e)}"
        )

# List cases
@app.get("/api/v1/cases")
async def list_cases(
    limit: int = Query(10, ge=1, le=100, description="Number of cases to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List available cases
    
    - **limit**: Number of cases to return (1-100)
    - **offset**: Offset for pagination
    """
    try:
        all_cases = system.system.data_loader.cases
        total = len(all_cases)
        
        # Paginate
        cases = all_cases[offset:offset+limit]
        
        # Clean up for response
        cleaned_cases = []
        for case in cases:
            cleaned_cases.append({
                'id': case['id'],
                'number': case['number'],
                'file': case['file'],
                'pertanyaan': case['pertanyaan'][:200] if case['pertanyaan'] else "",
                'pasal': case.get('pasal', [])[:3],
                'uu': case.get('uu', [])[:2]
            })
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(cleaned_cases),
            "cases": cleaned_cases,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing cases: {str(e)}"
        )

# Search cases
@app.get("/api/v1/search")
async def search_cases(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(3, ge=1, le=10, description="Number of results")
):
    """
    Search cases
    
    - **query**: Search query
    - **top_k**: Number of results to return (1-10)
    """
    try:
        results = system.enhanced_search.search(query, top_k=top_k)
        
        # Clean up for response
        cleaned_results = []
        for result in results:
            cleaned_results.append({
                'id': result['id'],
                'number': result['number'],
                'pertanyaan': result['pertanyaan'][:200],
                'similarity_score': result.get('similarity_score', 0),
                'search_method': result.get('search_method', 'unknown')
            })
        
        return {
            "success": True,
            "query": query,
            "count": len(cleaned_results),
            "results": cleaned_results,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching cases: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
