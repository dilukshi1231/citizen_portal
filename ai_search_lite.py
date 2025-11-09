"""
Lightweight AI Search Engine - Uses ONLY Gemini API
No heavy dependencies (sentence-transformers, torch, etc.)
Install: pip install google-generativeai
"""

import os
import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv
import json

load_dotenv()

class LiteAISearchEngine:
    def __init__(self):
        """Initialize with only Gemini (no local models)"""
        print("🔧 Initializing Lightweight AI Search Engine...")
        
        # Configure Gemini
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Store documents in memory (no FAISS needed)
        self.documents = []
        
        print("✅ Lightweight AI initialized (Gemini only)")
    
    def add_documents(self, documents: List[Dict]):
        """Store documents in memory"""
        self.documents.extend(documents)
        print(f"✅ Added {len(documents)} documents. Total: {len(self.documents)}")
    
    def search(self, query: str, k: int = 5, language: str = 'en') -> List[Dict]:
        """
        Simple keyword search (fast, no embeddings needed)
        For production, you can upgrade to Gemini Embeddings API
        """
        query_lower = query.lower()
        results = []
        
        # Score documents by keyword matching
        for doc in self.documents:
            if language and doc.get('language') != language:
                continue
            
            text_lower = doc['text'].lower()
            score = sum(1 for word in query_lower.split() if word in text_lower)
            
            if score > 0:
                doc_copy = doc.copy()
                doc_copy['similarity_score'] = score / len(query_lower.split())
                results.append(doc_copy)
        
        # Sort by score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:k]
    
    def generate_answer(self, query: str, context_docs: List[Dict], language: str = 'en') -> Dict:
        """Generate answer using Gemini"""
        if not context_docs:
            return {
                "answer": "I couldn't find relevant information. Please try rephrasing your question.",
                "sources": [],
                "confidence": 0.0,
                "language": language
            }
        
        # Prepare context
        context = "\n\n".join([
            f"[{doc['ministry']} - {doc['service']}]\n{doc['text']}"
            for doc in context_docs[:3]
        ])
        
        prompt = f"""You are a helpful assistant for Sri Lankan government services.

Context Information:
{context}

User Question: {query}

Instructions:
1. Answer based ONLY on the context provided
2. Mention the source ministry and service
3. Keep answer clear and concise
4. If context doesn't have the answer, say so politely
5. Respond in {self._get_language_name(language)}

Answer:"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text
            
            sources = [
                {
                    "ministry": doc['ministry'],
                    "service": doc['service'],
                    "score": doc.get('similarity_score', 0)
                }
                for doc in context_docs[:3]
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.85,
                "language": language,
                "model": "gemini-pro-lite"
            }
        
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "language": language,
                "error": str(e)
            }
    
    def _get_language_name(self, code: str) -> str:
        """Convert language code to name"""
        return {
            'en': 'English',
            'si': 'Sinhala',
            'ta': 'Tamil'
        }.get(code, 'English')
    
    def save_documents(self, filepath: str = 'data/documents.json'):
        """Save documents to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        print(f"✅ Documents saved to {filepath}")
    
    def load_documents(self, filepath: str = 'data/documents.json'):
        """Load documents from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            print(f"✅ Loaded {len(self.documents)} documents from {filepath}")
        except FileNotFoundError:
            print("⚠️  No saved documents found")


# Example usage
if __name__ == "__main__":
    print("\n🚀 Testing Lightweight AI Search\n")
    
    # Initialize (fast - no model downloads!)
    search_engine = LiteAISearchEngine()
    
    # Sample documents
    docs = [
        {
            "text": "To apply for IT certificate, fill online form and upload NIC. Processing: 5-7 days.",
            "ministry": "Ministry of IT",
            "service": "IT Certificates",
            "language": "en"
        },
        {
            "text": "Passport renewal: Visit immigration with current passport, NIC, 2 photos. Fee: Rs.3000. Time: 2-3 weeks.",
            "ministry": "Ministry of Immigration",
            "service": "Passport Services",
            "language": "en"
        }
    ]
    
    search_engine.add_documents(docs)
    
    # Test search
    query = "How to renew passport?"
    results = search_engine.search(query, k=2)
    
    print(f"🔍 Query: {query}")
    print(f"📋 Found {len(results)} results\n")
    
    # Generate answer
    answer = search_engine.generate_answer(query, results)
    print(f"🤖 Answer:\n{answer['answer']}\n")
    print(f"Model: {answer['model']}")