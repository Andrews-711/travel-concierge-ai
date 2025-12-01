"""
In-memory RAG system using ChromaDB
No persistence - all embeddings stored in memory only
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import hashlib
from datetime import datetime

from app.config import get_settings

settings = get_settings()


class InMemoryRAG:
    """
    Lightweight RAG system
    - In-memory vector store (ChromaDB)
    - Session-based collections
    - No persistence
    """
    
    def __init__(self):
        # Create in-memory ChromaDB client
        self.client = chromadb.Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=None,  # No persistence
            anonymized_telemetry=False
        ))
        
        # Load embedding model
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Session collections (in-memory)
        self.collections = {}
    
    def _get_collection_name(self, session_id: str) -> str:
        """Generate collection name for session"""
        return f"session_{hashlib.md5(session_id.encode()).hexdigest()[:8]}"
    
    def _get_or_create_collection(self, session_id: str):
        """Get or create collection for session"""
        collection_name = self._get_collection_name(session_id)
        
        if collection_name not in self.collections:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"created_at": datetime.now().isoformat()}
            )
            self.collections[collection_name] = collection
        
        return self.collections[collection_name]
    
    def add_documents(
        self,
        session_id: str,
        texts: List[str],
        metadatas: List[Dict[str, Any]] = None
    ) -> int:
        """
        Add document chunks to session collection
        
        Args:
            session_id: Session identifier
            texts: List of text chunks
            metadatas: Optional metadata for each chunk
        
        Returns:
            Number of chunks added
        """
        if not texts:
            return 0
        
        collection = self._get_or_create_collection(session_id)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Generate IDs
        ids = [f"{session_id}_{i}" for i in range(len(texts))]
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas or [{} for _ in texts],
            ids=ids
        )
        
        return len(texts)
    
    def search(
        self,
        session_id: str,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents in session collection
        
        Args:
            session_id: Session identifier
            query: Search query
            n_results: Number of results to return
        
        Returns:
            List of matching documents with metadata
        """
        collection_name = self._get_collection_name(session_id)
        
        if collection_name not in self.collections:
            return []
        
        collection = self.collections[collection_name]
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count())
        )
        
        # Format results
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return documents
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get info about session's documents"""
        collection_name = self._get_collection_name(session_id)
        
        if collection_name not in self.collections:
            return {'exists': False, 'count': 0}
        
        collection = self.collections[collection_name]
        
        return {
            'exists': True,
            'count': collection.count(),
            'metadata': collection.metadata
        }
    
    def clear_session(self, session_id: str):
        """Clear all documents for a session"""
        collection_name = self._get_collection_name(session_id)
        
        if collection_name in self.collections:
            try:
                self.client.delete_collection(collection_name)
                del self.collections[collection_name]
            except:
                pass


# Global RAG instance
rag = InMemoryRAG()
