"""
Minimal RAG - No ChromaDB, just in-memory Python dictionaries
Ultra fast, no dependencies
"""
from typing import List, Dict, Any
import hashlib
from datetime import datetime


class MinimalRAG:
    """
    Minimal in-memory RAG
    - No vector embeddings
    - Simple keyword matching
    - Zero dependencies
    """
    
    def __init__(self):
        # Session storage: {session_id: {doc_id: {chunks, metadata}}}
        self.sessions = {}
    
    def add_documents(
        self,
        session_id: str,
        texts: List[str],
        metadatas: List[Dict[str, Any]] = None
    ) -> int:
        """Add document chunks to session"""
        if not texts:
            return 0
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'chunks': [],
                'metadatas': [],
                'created_at': datetime.now().isoformat()
            }
        
        self.sessions[session_id]['chunks'].extend(texts)
        self.sessions[session_id]['metadatas'].extend(metadatas or [{} for _ in texts])
        
        return len(texts)
    
    def search(
        self,
        session_id: str,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Simple keyword-based search
        No embeddings, just keyword matching
        """
        if session_id not in self.sessions:
            return []
        
        chunks = self.sessions[session_id]['chunks']
        metadatas = self.sessions[session_id]['metadatas']
        
        if not chunks:
            return []
        
        # Simple scoring: count matching keywords
        query_words = set(query.lower().split())
        scores = []
        
        for i, chunk in enumerate(chunks):
            chunk_words = set(chunk.lower().split())
            score = len(query_words & chunk_words)  # Intersection count
            scores.append((score, i, chunk))
        
        # Sort by score descending
        scores.sort(reverse=True, key=lambda x: x[0])
        
        # Return top N
        results = []
        for score, idx, chunk in scores[:n_results]:
            if score > 0:  # Only return if there's at least one match
                results.append({
                    'content': chunk,
                    'metadata': metadatas[idx],
                    'distance': 1.0 - (score / max(len(query_words), 1))  # Fake distance
                })
        
        return results
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get info about session's documents"""
        if session_id not in self.sessions:
            return {'exists': False, 'count': 0}
        
        return {
            'exists': True,
            'count': len(self.sessions[session_id]['chunks']),
            'created_at': self.sessions[session_id].get('created_at')
        }
    
    def clear_session(self, session_id: str):
        """Clear all documents for a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global RAG instance
rag = MinimalRAG()
