"""
RAG (Retrieval Augmented Generation) Service for MedObsMind

Provides context-aware responses by retrieving relevant medical guidelines,
protocols, and knowledge before LLM generation.

Knowledge Base:
- ICMR guidelines
- AIIMS protocols
- Indian drug formularies
- Clinical scoring systems
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Retrieved document chunk."""
    content: str
    source: str
    relevance_score: float
    metadata: Dict


class RAGService:
    """
    Retrieval Augmented Generation service.
    
    Uses vector embeddings to retrieve relevant medical knowledge
    before LLM generation, reducing hallucinations and providing
    source citations.
    """
    
    def __init__(
        self,
        vector_store_path: str = "data/vector_store",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        top_k: int = 3
    ):
        """
        Initialize RAG service.
        
        Args:
            vector_store_path: Path to Chroma/FAISS vector store
            embedding_model: Sentence transformer model for embeddings
            top_k: Number of documents to retrieve
        """
        self.vector_store_path = vector_store_path
        self.embedding_model_name = embedding_model
        self.top_k = top_k
        
        # Initialize (would load actual vector store in production)
        logger.info(f"RAG service initialized with {embedding_model}")
    
    def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None,
        top_k: Optional[int] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents for query.
        
        Args:
            query: Search query
            filters: Optional filters (source_type, date, etc.)
            top_k: Override default top_k
        
        Returns:
            List of relevant documents with scores
        """
        k = top_k or self.top_k
        
        # In production, would use actual vector store (Chroma/FAISS)
        # For now, return mock documents
        logger.info(f"Retrieving top {k} documents for: {query}")
        
        # Mock retrieval - replace with actual vector search
        documents = self._mock_retrieval(query, k)
        
        return documents
    
    def augment_prompt(
        self,
        base_prompt: str,
        query: str,
        include_sources: bool = True
    ) -> str:
        """
        Augment prompt with retrieved context.
        
        Args:
            base_prompt: Original prompt
            query: Query for retrieval
            include_sources: Whether to include source citations
        
        Returns:
            Augmented prompt with context
        """
        # Retrieve relevant documents
        documents = self.retrieve(query)
        
        # Format context
        context = self._format_context(documents, include_sources)
        
        # Augment prompt
        augmented = f"""### Context (from medical guidelines):
{context}

{base_prompt}"""
        
        return augmented
    
    def get_guideline(
        self,
        topic: str,
        guideline_type: str = "icmr"
    ) -> Optional[Dict]:
        """
        Get specific clinical guideline.
        
        Args:
            topic: Topic (e.g., "sepsis", "diabetic_ketoacidosis")
            guideline_type: Type (icmr, aiims, isccm)
        
        Returns:
            Guideline document or None
        """
        query = f"{guideline_type} guideline for {topic}"
        documents = self.retrieve(query, filters={"type": guideline_type}, top_k=1)
        
        if documents:
            return {
                "content": documents[0].content,
                "source": documents[0].source,
                "metadata": documents[0].metadata
            }
        
        return None
    
    def get_drug_info(
        self,
        drug_name: str,
        info_type: str = "dosage"
    ) -> Optional[Dict]:
        """
        Get drug information from Indian formulary.
        
        Args:
            drug_name: Drug name (generic)
            info_type: Type of info (dosage, contraindications, interactions)
        
        Returns:
            Drug information or None
        """
        query = f"{drug_name} {info_type} india"
        documents = self.retrieve(query, filters={"type": "drug_formulary"}, top_k=1)
        
        if documents:
            return {
                "drug": drug_name,
                "info": documents[0].content,
                "source": documents[0].source
            }
        
        return None
    
    def get_scoring_system(
        self,
        score_name: str
    ) -> Optional[Dict]:
        """
        Get clinical scoring system details.
        
        Args:
            score_name: Score name (NEWS2, qSOFA, SOFA, APACHE, etc.)
        
        Returns:
            Scoring system details or None
        """
        query = f"{score_name} clinical score calculation"
        documents = self.retrieve(query, filters={"type": "scoring_system"}, top_k=1)
        
        if documents:
            return {
                "name": score_name,
                "description": documents[0].content,
                "source": documents[0].source
            }
        
        return None
    
    # Internal methods
    
    def _format_context(self, documents: List[Document], include_sources: bool) -> str:
        """Format retrieved documents as context."""
        if not documents:
            return "No specific guidelines retrieved."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source_info = f" (Source: {doc.source})" if include_sources else ""
            context_parts.append(f"{i}. {doc.content}{source_info}")
        
        return "\n".join(context_parts)
    
    def _mock_retrieval(self, query: str, top_k: int) -> List[Document]:
        """
        Mock document retrieval.
        
        In production, replace with actual vector store search.
        """
        # Mock knowledge base
        mock_kb = {
            "sepsis": Document(
                content="According to ICMR 2023 guidelines, sepsis is defined as life-threatening organ dysfunction caused by dysregulated host response to infection. Initial management includes: (1) Blood cultures before antibiotics, (2) Broad-spectrum antibiotics within 1 hour, (3) IV fluid resuscitation 30 ml/kg, (4) Lactate measurement, (5) Monitor urine output.",
                source="ICMR Sepsis Management Guidelines 2023",
                relevance_score=0.95,
                metadata={"type": "guideline", "year": 2023}
            ),
            "news2": Document(
                content="NEWS2 (National Early Warning Score 2) is a clinical score for detecting clinical deterioration. Score ≥7 indicates High Risk (urgent clinical review within 1 hour by senior clinician). Score 5-6 indicates Medium Risk (review by ward-based clinician). Score 0-4 indicates Low Risk (routine monitoring).",
                source="Royal College of Physicians 2017",
                relevance_score=0.98,
                metadata={"type": "scoring_system", "year": 2017}
            ),
            "qsofa": Document(
                content="qSOFA (Quick Sequential Organ Failure Assessment) identifies patients at risk of sepsis outside ICU. Criteria: (1) Respiratory rate ≥22/min, (2) Altered mental status (GCS <15), (3) Systolic blood pressure ≤100 mmHg. Score ≥2 suggests sepsis with 3-14× higher mortality.",
                source="JAMA 2016, validated in India",
                relevance_score=0.96,
                metadata={"type": "scoring_system", "year": 2016}
            )
        }
        
        # Simple keyword matching (replace with actual embeddings)
        query_lower = query.lower()
        matched_docs = []
        
        for key, doc in mock_kb.items():
            if key in query_lower or any(word in query_lower for word in key.split("_")):
                matched_docs.append(doc)
        
        # Return top_k documents
        return matched_docs[:top_k] if matched_docs else []
    
    def add_documents(
        self,
        documents: List[Dict],
        source: str
    ) -> int:
        """
        Add new documents to knowledge base.
        
        Args:
            documents: List of document dicts with 'content' and 'metadata'
            source: Source identifier
        
        Returns:
            Number of documents added
        """
        logger.info(f"Adding {len(documents)} documents from {source}")
        
        # In production, would:
        # 1. Generate embeddings
        # 2. Add to vector store
        # 3. Update index
        
        return len(documents)
    
    def update_knowledge_base(
        self,
        guideline_path: str,
        guideline_type: str
    ) -> bool:
        """
        Update knowledge base with new guidelines.
        
        Args:
            guideline_path: Path to guideline PDF/document
            guideline_type: Type (icmr, aiims, isccm)
        
        Returns:
            Success status
        """
        logger.info(f"Updating knowledge base: {guideline_type} from {guideline_path}")
        
        # In production, would:
        # 1. Parse PDF/document
        # 2. Chunk into segments
        # 3. Generate embeddings
        # 4. Add to vector store
        
        return True


# Example usage
if __name__ == "__main__":
    # Initialize service
    rag = RAGService()
    
    # Retrieve documents
    docs = rag.retrieve("sepsis management guidelines")
    print(f"Retrieved {len(docs)} documents")
    for doc in docs:
        print(f"- {doc.source}: {doc.content[:100]}...")
    
    # Get specific guideline
    guideline = rag.get_guideline("sepsis", "icmr")
    if guideline:
        print(f"\nGuideline: {guideline['source']}")
    
    # Augment prompt
    base_prompt = "Explain sepsis management"
    augmented = rag.augment_prompt(base_prompt, "sepsis management")
    print(f"\nAugmented prompt:\n{augmented}")
