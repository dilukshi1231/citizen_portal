"""
AI-Powered Semantic Search Engine
Handles document ingestion, embedding generation, and intelligent search
"""

import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import pickle
import openai
from dotenv import load_dotenv

load_dotenv()

class AISearchEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the AI search engine
        
        Args:
            model_name: HuggingFace model for embeddings (384-dimensional)
        """
        print("🔧 Initializing AI Search Engine...")
        
        # Load embedding model (runs locally, no API needed)
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # all-MiniLM-L6-v2 produces 384-dim vectors
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Store document metadata
        self.documents = []
        self.doc_metadata = []
        
        # OpenAI API key for answer generation
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        print("✅ AI Search Engine initialized successfully")
    
    def add_documents(self, documents: List[Dict], batch_size=32):
        """
        Add documents to the search index
        
        Args:
            documents: List of dicts with 'text', 'ministry', 'service', 'language', etc.
            batch_size: Number of documents to process at once
        """
        print(f"📚 Adding {len(documents)} documents to index...")
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            
            # Extract text content
            texts = [doc['text'] for doc in batch]
            
            # Generate embeddings
            embeddings = self.model.encode(texts, show_progress_bar=True)
            
            # Add to FAISS index
            self.index.add(embeddings.astype('float32'))
            
            # Store metadata
            self.documents.extend(texts)
            self.doc_metadata.extend(batch)
        
        print(f"✅ Added {len(documents)} documents. Total indexed: {self.index.ntotal}")
    
    def search(self, query: str, k: int = 5, language: Optional[str] = None) -> List[Dict]:
        """
        Semantic search for relevant documents
        
        Args:
            query: User's search query
            k: Number of top results to return
            language: Optional language filter ('en', 'si', 'ta')
        
        Returns:
            List of relevant documents with similarity scores
        """
        # Generate query embedding
        query_embedding = self.model.encode([query])
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), k * 2)
        
        # Retrieve documents with metadata
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.doc_metadata):
                doc = self.doc_metadata[idx].copy()
                doc['similarity_score'] = float(1 / (1 + dist))  # Convert distance to similarity
                
                # Apply language filter if specified
                if language and doc.get('language') != language:
                    continue
                
                results.append(doc)
                
                if len(results) >= k:
                    break
        
        return results
    
    def generate_answer(self, query: str, context_docs: List[Dict], language: str = 'en') -> Dict:
        """
        Generate AI answer using retrieved context
        
        Args:
            query: User's question
            context_docs: Retrieved relevant documents
            language: Response language
        
        Returns:
            Dict with answer, sources, and confidence
        """
        # Prepare context from retrieved documents
        context = "\n\n".join([
            f"[{doc['ministry']} - {doc['service']}]\n{doc['text']}"
            for doc in context_docs[:3]  # Use top 3 most relevant
        ])
        
        # Create prompt for LLM
        system_prompt = f"""You are a helpful assistant for Sri Lankan government services.
Answer questions based ONLY on the provided context.
Always cite the source (ministry and service) in your answer.
If the context doesn't contain the answer, say so politely.
Respond in {self._get_language_name(language)}."""

        user_prompt = f"""Context:
{context}

Question: {query}

Please provide a clear, helpful answer with source citations."""

        try:
            # Call OpenAI API (you can switch to Claude/Anthropic if preferred)
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Extract sources
            sources = [
                {
                    "ministry": doc['ministry'],
                    "service": doc['service'],
                    "score": doc['similarity_score']
                }
                for doc in context_docs[:3]
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": np.mean([doc['similarity_score'] for doc in context_docs[:3]]),
                "language": language
            }
        
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return {
                "answer": "I apologize, but I'm having trouble generating an answer right now. Please try again later.",
                "sources": [],
                "confidence": 0.0,
                "language": language,
                "error": str(e)
            }
    
    def _get_language_name(self, code: str) -> str:
        """Convert language code to full name"""
        lang_map = {
            'en': 'English',
            'si': 'Sinhala',
            'ta': 'Tamil'
        }
        return lang_map.get(code, 'English')
    
    def save_index(self, filepath: str = 'data/faiss_index'):
        """Save FAISS index and metadata to disk"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{filepath}.index")
        
        # Save metadata
        with open(f"{filepath}_metadata.pkl", 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'doc_metadata': self.doc_metadata
            }, f)
        
        print(f"✅ Index saved to {filepath}")
    
    def load_index(self, filepath: str = 'data/faiss_index'):
        """Load FAISS index and metadata from disk"""
        # Load FAISS index
        self.index = faiss.read_index(f"{filepath}.index")
        
        # Load metadata
        with open(f"{filepath}_metadata.pkl", 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.doc_metadata = data['doc_metadata']
        
        print(f"✅ Index loaded from {filepath}. Total documents: {self.index.ntotal}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize search engine
    search_engine = AISearchEngine()
    
    # Sample documents (in production, load from MongoDB)
    sample_docs = [
        {
            "text": "To apply for an IT certificate, fill the online form and upload your NIC. Visit the digital portal, register and submit your application.",
            "ministry": "Ministry of IT & Digital Affairs",
            "service": "IT Certificates",
            "language": "en",
            "downloads": ["/forms/it_cert.pdf"],
            "location": "https://maps.google.com/?q=Ministry+of+IT"
        },
        {
            "text": "Complete the school registration form and submit required documents including birth certificate and proof of residence to the education ministry portal.",
            "ministry": "Ministry of Education",
            "service": "Schools",
            "language": "en",
            "downloads": ["/forms/school_reg.pdf"],
            "location": "https://maps.google.com/?q=Ministry+of+Education"
        },
        {
            "text": "For passport renewal, visit the immigration office with your current passport, NIC, and two passport-sized photos. Processing time is 2-3 weeks.",
            "ministry": "Ministry of Immigration",
            "service": "Passport Services",
            "language": "en",
            "downloads": ["/forms/passport_renewal.pdf"],
            "location": "https://maps.google.com/?q=Immigration+Office"
        }
    ]
    
    # Add documents to index
    search_engine.add_documents(sample_docs)
    
    # Test search
    query = "How do I renew my passport?"
    print(f"\n🔍 Searching for: '{query}'")
    results = search_engine.search(query, k=3)
    
    print("\n📋 Search Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['ministry']} - {result['service']}")
        print(f"   Score: {result['similarity_score']:.3f}")
        print(f"   Text: {result['text'][:100]}...")
    
    # Generate AI answer
    print("\n🤖 Generating AI Answer...")
    answer = search_engine.generate_answer(query, results)
    print(f"\nAnswer: {answer['answer']}")
    print(f"Confidence: {answer['confidence']:.2%}")
    
    # Save index
    search_engine.save_index()