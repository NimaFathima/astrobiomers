"""Test RAG Service"""
import sys
sys.path.insert(0, 'C:\\Users\\mi\\Downloads\\ASTROBIOMERS\\backend')

from api.services.rag_service import KnowledgeGraphRAG

print("Initializing RAG service...")
rag = KnowledgeGraphRAG()

print(f"✅ RAG service initialized")
print(f"   LLM Provider: {rag.llm_provider or 'None (fallback mode)'}")
print(f"   Has LLM: {rag.llm_client is not None}")

print("\nTesting question...")
result = rag.answer_question(
    "What are the effects of microgravity?",
    max_papers=3
)

print(f"\n{'='*60}")
print(f"Question: {result['question']}")
print(f"{'='*60}")
print(f"\nAnswer:\n{result['answer']}")
print(f"\n{'='*60}")
print(f"Sources: {len(result['sources'])} papers")
print(f"Entities: {result['metadata']['entity_count']}")
print(f"Papers in graph: {result['metadata']['paper_count']}")
print(f"{'='*60}")
