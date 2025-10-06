"""
Paper Summarization Module

Uses BART or PEGASUS models for abstractive summarization of research papers.
Generates concise summaries of abstracts and full texts.

Models:
- facebook/bart-large-cnn (BART)
- google/pegasus-xsum (PEGASUS)

Author: Astrobiomers Team
Date: October 2025
"""

import logging
from typing import Dict, Optional, List
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)

# Optional dependencies - graceful degradation
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. Summarization will use fallback method.")
    TRANSFORMERS_AVAILABLE = False


class PaperSummarizer:
    """
    Generate summaries of scientific papers using transformer models.
    
    Supports both BART and PEGASUS models with automatic model selection
    based on content length and type.
    """
    
    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        use_gpu: bool = True,
        max_length: int = 150,
        min_length: int = 50
    ):
        """
        Initialize summarizer with specified model.
        
        Args:
            model_name: HuggingFace model name (bart-large-cnn or pegasus-xsum)
            use_gpu: Use GPU if available
            max_length: Maximum summary length in tokens
            min_length: Minimum summary length in tokens
        """
        self.model_name = model_name
        self.max_length = max_length
        self.min_length = min_length
        self.device = 0 if use_gpu and torch.cuda.is_available() else -1
        
        self.summarizer = None
        self._cache = {}  # Simple in-memory cache
        
        logger.info(f"PaperSummarizer initialized with model: {model_name}")
        logger.info(f"Using device: {'GPU' if self.device == 0 else 'CPU'}")
    
    def _load_model(self):
        """Lazy load the summarization model."""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available. Cannot load model.")
            return False
        
        if self.summarizer is None:
            try:
                logger.info(f"Loading summarization model: {self.model_name}")
                self.summarizer = pipeline(
                    "summarization",
                    model=self.model_name,
                    device=self.device,
                    framework="pt"
                )
                logger.info("✅ Summarization model loaded successfully")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
                return False
        return True
    
    def _get_cache_key(self, text: str, summary_type: str) -> str:
        """Generate cache key for text."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{summary_type}:{text_hash}"
    
    def _truncate_text(self, text: str, max_tokens: int = 1024) -> str:
        """
        Truncate text to fit model's max input length.
        
        Args:
            text: Input text
            max_tokens: Maximum number of tokens (approximate)
        
        Returns:
            Truncated text
        """
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        # Truncate at sentence boundary
        truncated = text[:max_chars]
        last_period = truncated.rfind('.')
        
        if last_period > max_chars * 0.8:  # Keep at least 80% of text
            return truncated[:last_period + 1]
        
        return truncated
    
    def _fallback_summary(self, text: str, num_sentences: int = 3) -> str:
        """
        Simple extractive summarization fallback (when models unavailable).
        
        Takes first N sentences as summary.
        """
        sentences = text.split('. ')
        summary_sentences = sentences[:num_sentences]
        return '. '.join(summary_sentences) + '.'
    
    def summarize_abstract(
        self,
        abstract: str,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Generate a summary of a paper's abstract.
        
        Args:
            abstract: Paper abstract text
            max_length: Override default max length
            min_length: Override default min length
        
        Returns:
            Dict with 'summary', 'model_used', 'length_ratio'
        """
        if not abstract or len(abstract.strip()) < 50:
            return {
                "summary": abstract,
                "model_used": "none",
                "length_ratio": 1.0,
                "error": "Abstract too short to summarize"
            }
        
        # Check cache
        cache_key = self._get_cache_key(abstract, "abstract")
        if cache_key in self._cache:
            logger.info("✅ Returning cached summary")
            return self._cache[cache_key]
        
        # Load model
        if not self._load_model():
            # Fallback to extractive summary
            logger.info("Using fallback extractive summarization")
            summary = self._fallback_summary(abstract, num_sentences=2)
            result = {
                "summary": summary,
                "model_used": "extractive_fallback",
                "length_ratio": len(summary) / len(abstract),
                "original_length": len(abstract),
                "summary_length": len(summary)
            }
            self._cache[cache_key] = result
            return result
        
        try:
            # Truncate if too long
            text = self._truncate_text(abstract, max_tokens=1024)
            
            # Generate summary
            max_len = max_length or self.max_length
            min_len = min_length or self.min_length
            
            logger.info(f"Generating summary (max={max_len}, min={min_len})...")
            
            result = self.summarizer(
                text,
                max_length=max_len,
                min_length=min_len,
                do_sample=False,
                truncation=True
            )
            
            summary = result[0]['summary_text']
            
            result_dict = {
                "summary": summary,
                "model_used": self.model_name,
                "length_ratio": len(summary) / len(abstract),
                "original_length": len(abstract),
                "summary_length": len(summary)
            }
            
            # Cache result
            self._cache[cache_key] = result_dict
            
            logger.info(f"✅ Summary generated ({len(summary)} chars)")
            return result_dict
            
        except Exception as e:
            logger.error(f"❌ Summarization failed: {e}")
            
            # Fallback to extractive
            summary = self._fallback_summary(abstract, num_sentences=2)
            return {
                "summary": summary,
                "model_used": "extractive_fallback",
                "length_ratio": len(summary) / len(abstract),
                "error": str(e)
            }
    
    def summarize_full_text(
        self,
        full_text: str,
        max_length: int = 300,
        min_length: int = 100
    ) -> Dict[str, any]:
        """
        Generate summary of full paper text.
        
        For longer texts, may use chunking strategy.
        
        Args:
            full_text: Complete paper text
            max_length: Maximum summary length
            min_length: Minimum summary length
        
        Returns:
            Dict with summary and metadata
        """
        if not full_text or len(full_text.strip()) < 100:
            return {
                "summary": full_text,
                "model_used": "none",
                "error": "Text too short"
            }
        
        # Check cache
        cache_key = self._get_cache_key(full_text, "fulltext")
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # For very long texts, use chunking + summarize chunks
        if len(full_text) > 4096 * 4:  # ~4096 tokens
            return self._summarize_long_text(full_text, max_length, min_length)
        
        # Standard summarization
        return self.summarize_abstract(full_text, max_length, min_length)
    
    def _summarize_long_text(
        self,
        text: str,
        max_length: int,
        min_length: int
    ) -> Dict[str, any]:
        """
        Summarize very long text using chunking strategy.
        
        1. Split text into chunks
        2. Summarize each chunk
        3. Combine chunk summaries
        4. Summarize the combined summaries
        """
        logger.info("Using chunking strategy for long text")
        
        # Split into chunks (roughly 1024 tokens each)
        chunk_size = 1024 * 4  # ~1024 tokens
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks[:10]):  # Limit to 10 chunks
            try:
                result = self.summarize_abstract(chunk, max_length=150, min_length=50)
                chunk_summaries.append(result['summary'])
            except Exception as e:
                logger.error(f"Failed to summarize chunk {i}: {e}")
                continue
        
        # Combine and summarize
        combined = " ".join(chunk_summaries)
        
        return self.summarize_abstract(combined, max_length, min_length)
    
    def generate_key_points(self, abstract: str, num_points: int = 3) -> List[str]:
        """
        Extract key points from abstract.
        
        Args:
            abstract: Paper abstract
            num_points: Number of key points to extract
        
        Returns:
            List of key point strings
        """
        # Simple approach: take first sentences
        sentences = [s.strip() for s in abstract.split('.') if s.strip()]
        
        # Take most important sentences (first, middle, last)
        if len(sentences) <= num_points:
            return sentences
        
        key_indices = [0, len(sentences)//2, -1]
        return [sentences[i] for i in key_indices[:num_points]]
    
    def clear_cache(self):
        """Clear summary cache."""
        self._cache.clear()
        logger.info("Summary cache cleared")


# Singleton instance
_summarizer_instance = None


def get_summarizer(
    model_name: str = "facebook/bart-large-cnn",
    use_gpu: bool = True
) -> PaperSummarizer:
    """
    Get or create singleton summarizer instance.
    
    Args:
        model_name: Model to use (bart-large-cnn or pegasus-xsum)
        use_gpu: Use GPU if available
    
    Returns:
        PaperSummarizer instance
    """
    global _summarizer_instance
    
    if _summarizer_instance is None:
        _summarizer_instance = PaperSummarizer(
            model_name=model_name,
            use_gpu=use_gpu
        )
    
    return _summarizer_instance


# Quick test function
if __name__ == "__main__":
    # Test summarization
    logging.basicConfig(level=logging.INFO)
    
    test_abstract = """
    Spaceflight exposes astronauts to microgravity and radiation, which can have 
    significant effects on human physiology. Studies have shown that prolonged 
    exposure to microgravity leads to bone density loss, muscle atrophy, and 
    cardiovascular deconditioning. Additionally, cosmic radiation poses risks 
    of DNA damage and increased cancer risk. This research investigates the 
    molecular mechanisms underlying these physiological changes and evaluates 
    potential countermeasures including exercise protocols and pharmaceutical 
    interventions. Our findings suggest that combination therapies targeting 
    multiple pathways may be most effective in mitigating spaceflight-induced 
    health risks.
    """
    
    summarizer = get_summarizer()
    result = summarizer.summarize_abstract(test_abstract)
    
    print("\n" + "="*60)
    print("ORIGINAL ABSTRACT:")
    print("="*60)
    print(test_abstract)
    print("\n" + "="*60)
    print("GENERATED SUMMARY:")
    print("="*60)
    print(result['summary'])
    print("\n" + "="*60)
    print(f"Model: {result['model_used']}")
    print(f"Compression: {result['length_ratio']:.2%}")
    print("="*60)
