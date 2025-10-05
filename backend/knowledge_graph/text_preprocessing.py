"""
Text Preprocessing Module

Handles preprocessing of scientific text for NLP pipeline:
- Text cleaning (citations, figures, URLs)
- Sentence segmentation
- Tokenization
- Lemmatization
- Stopword removal
"""

from typing import List, Dict
import re
import logging

try:  # pragma: no cover - optional dependency
    import spacy  # type: ignore
except ImportError:  # pragma: no cover
    spacy = None  # type: ignore

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    Handles text preprocessing for NLP pipeline.
    """
    
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """
        Initialize text preprocessor.
        
        Args:
            spacy_model: SpaCy model to use for linguistic processing
        """
        self.logger = logging.getLogger(__name__)
        
        self.nlp = None
        if spacy is not None:
            try:
                self.nlp = spacy.load(spacy_model)
                self.logger.info(f"Loaded spaCy model: {spacy_model}")
            except OSError:
                self.logger.warning(f"Model {spacy_model} not found. Installing...")
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", spacy_model], check=False)
                try:
                    self.nlp = spacy.load(spacy_model)
                except Exception as exc:  # pragma: no cover - network issues
                    self.logger.error(f"Failed to load spaCy model after download: {exc}")
                    self.nlp = None
        else:
            self.logger.warning("spaCy not installed; falling back to lightweight preprocessing.")
        
        # Custom stopwords for scientific text
        self.custom_stopwords = {
            'et', 'al', 'fig', 'figure', 'table', 'however', 
            'therefore', 'thus', 'furthermore', 'moreover',
            'respectively', 'approximately', 'supplementary'
        }
    
    def preprocess(self, text: str) -> Dict:
        """
        Preprocess scientific text.
        
        Args:
            text: Raw text from publication
            
        Returns:
            Dictionary with preprocessed text and metadata
        """
        # Clean text
        cleaned = self._clean_text(text)
        
        # Sentence segmentation
        sentences = self._segment_sentences(cleaned)
        
        # Tokenization and linguistic processing
        processed_sentences = []
        for sent in sentences:
            processed = self._process_sentence(sent)
            processed_sentences.append(processed)
        
        flattened_tokens = [token for sent in processed_sentences for token in sent['tokens']]

        return {
            'original_text': text,
            'cleaned_text': cleaned,
            'sentences': [sent['original'] for sent in processed_sentences],
            'sentence_details': processed_sentences,
            'tokens': flattened_tokens,
            'token_count': len(flattened_tokens),
            'sentence_count': len(processed_sentences)
        }

    # Legacy alias
    def preprocess_text(self, text: str) -> Dict:
        return self.preprocess(text)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean raw text.
        
        Steps:
        1. Remove special characters but keep hyphens in compound words
        2. Normalize whitespace
        3. Remove citations [1], [2,3]
        4. Remove figure/table references
        """
        if not text:
            return ""
        
        # Remove citation brackets [1], [2,3], [1-5]
        text = re.sub(r'\[\d+(?:[-,]\s*\d+)*\]', '', text)
        
        # Remove figure/table references
        text = re.sub(
            r'\((?:Fig|Figure|Table|Supplementary)\.\s*\d+[A-Za-z]?\)',
            '',
            text,
            flags=re.IGNORECASE
        )
        
        # Remove URLs
        text = re.sub(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            '',
            text
        )
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _segment_sentences(self, text: str) -> List[str]:
        """
        Segment text into sentences using spaCy.
        
        Args:
            text: Cleaned text
            
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        if self.nlp is not None:
            doc = self.nlp(text)
            return [sent.text for sent in doc.sents]

        # Fallback: naive sentence split on punctuation
        return [sent.strip() for sent in re.split(r'(?<=[.!?])\s+', text) if sent.strip()]
    
    def _process_sentence(self, sentence: str) -> Dict:
        """
        Process individual sentence.
        
        Returns:
            Dictionary with tokens, lemmas, POS tags, etc.
        """
        if self.nlp is not None:
            doc = self.nlp(sentence)

            tokens = []
            lemmas = []
            pos_tags = []

            for token in doc:
                if token.is_stop or token.is_punct:
                    continue

                if token.lemma_.lower() in self.custom_stopwords:
                    continue

                if len(token.text) < 2:
                    continue

                tokens.append(token.text)
                lemmas.append(token.lemma_)
                pos_tags.append(token.pos_)

            return {
                'original': sentence,
                'tokens': tokens,
                'lemmas': lemmas,
                'pos_tags': pos_tags,
                'token_count': len(tokens)
            }

        # Fallback: simple regex-based tokenization
        words = re.findall(r"[A-Za-z][A-Za-z-]+", sentence)
        filtered = [w for w in words if w.lower() not in self.custom_stopwords and len(w) > 1]
        return {
            'original': sentence,
            'tokens': filtered,
            'lemmas': [w.lower() for w in filtered],
            'pos_tags': ["X"] * len(filtered),
            'token_count': len(filtered)
        }
    
    def preprocess_batch(self, papers: List[Dict]) -> List[Dict]:
        """
        Preprocess a batch of papers.
        
        Args:
            papers: List of paper dictionaries with 'title' and 'abstract'
            
        Returns:
            Papers with added 'preprocessed' field
        """
        self.logger.info(f"Preprocessing {len(papers)} papers...")
        
        for i, paper in enumerate(papers):
            try:
                # Combine title and abstract
                text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                
                # Preprocess
                preprocessed = self.preprocess(text)
                paper['preprocessed'] = preprocessed
                
                if (i + 1) % 100 == 0:
                    self.logger.info(f"Preprocessed {i + 1}/{len(papers)} papers")
                    
            except Exception as e:
                self.logger.error(f"Error preprocessing paper {paper.get('pmid', 'unknown')}: {e}")
                paper['preprocessed'] = None
                continue
        
        self.logger.info(f"Preprocessing complete: {len(papers)} papers")
        return papers
    
    def extract_sentences_with_keywords(
        self,
        text: str,
        keywords: List[str]
    ) -> List[str]:
        """
        Extract sentences containing specific keywords.
        
        Useful for focused relationship extraction.
        
        Args:
            text: Input text
            keywords: List of keywords to search for
            
        Returns:
            List of sentences containing keywords
        """
        sentences = self._segment_sentences(text)
        
        matching_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword.lower() in sentence_lower for keyword in keywords):
                matching_sentences.append(sentence)
        
        return matching_sentences
