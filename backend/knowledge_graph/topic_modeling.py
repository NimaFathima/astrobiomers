"""
Topic Modeling Module for Space Biology Knowledge Graph

Uses BERTopic for discovering research themes and organizing papers.

Key Features:
- Biomedical sentence embeddings (PubMedBERT)
- UMAP dimensionality reduction
- HDBSCAN clustering
- Dynamic topic generation
- Temporal analysis (topic evolution)

Author: Space Biology KG Team
Date: October 2025
"""

import logging
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import numpy as np
from datetime import datetime

# BERTopic and dependencies
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
import umap
import hdbscan

logger = logging.getLogger(__name__)


class TopicModeler:
    """
    Discover and analyze research topics in space biology literature.
    
    Uses BERTopic with biomedical embeddings for topic discovery.
    """
    
    def __init__(self, config=None):
        """Initialize topic modeler."""
        from knowledge_graph.config import config as default_config
        
        self.config = config or default_config
        
        self.model = None
        self.embedding_model = None
        self.topics_info = None
        
        logger.info("TopicModeler initialized")
    
    def _load_embedding_model(self):
        """Load sentence transformer model for embeddings."""
        if self.embedding_model is None:
            logger.info("Loading sentence embedding model...")
            
            # Use biomedical PubMedBERT model
            model_name = self.config.SENTENCE_TRANSFORMER_MODEL
            self.embedding_model = SentenceTransformer(model_name)
            
            logger.info(f"Loaded embedding model: {model_name}")
    
    def fit_topics(
        self,
        papers: List[Dict],
        n_topics: Optional[int] = None,
        min_topic_size: int = 10
    ) -> BERTopic:
        """
        Fit BERTopic model on paper abstracts.
        
        Args:
            papers: List of papers with 'abstract', 'pmid', 'title'
            n_topics: Number of topics (None for automatic)
            min_topic_size: Minimum papers per topic
        
        Returns:
            Fitted BERTopic model
        """
        logger.info(f"Fitting topic model on {len(papers)} papers...")
        
        # Extract abstracts
        abstracts = [
            f"{p.get('title', '')} {p.get('abstract', '')}"
            for p in papers
            if p.get('abstract')
        ]
        
        if len(abstracts) < min_topic_size:
            logger.warning(f"Not enough papers ({len(abstracts)}) for topic modeling")
            return None
        
        # Load embedding model
        self._load_embedding_model()
        
        # Configure UMAP for dimensionality reduction
        umap_model = umap.UMAP(
            n_neighbors=15,
            n_components=5,
            min_dist=0.0,
            metric='cosine',
            random_state=42
        )
        
        # Configure HDBSCAN for clustering
        hdbscan_model = hdbscan.HDBSCAN(
            min_cluster_size=min_topic_size,
            min_samples=5,
            metric='euclidean',
            cluster_selection_method='eom',
            prediction_data=True
        )
        
        # Configure vectorizer for topic representation
        # Use space biology terms for better topic labels
        vectorizer_model = CountVectorizer(
            ngram_range=(1, 3),
            stop_words='english',
            min_df=2
        )
        
        # Create BERTopic model
        self.model = BERTopic(
            embedding_model=self.embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer_model,
            top_n_words=10,
            n_gram_range=(1, 3),
            min_topic_size=min_topic_size,
            nr_topics=n_topics,
            calculate_probabilities=True,
            verbose=True
        )
        
        # Fit the model
        logger.info("Generating embeddings...")
        topics, probs = self.model.fit_transform(abstracts)
        
        # Get topic info
        self.topics_info = self.model.get_topic_info()
        
        logger.info(f"Discovered {len(set(topics)) - 1} topics (excluding outliers)")
        logger.info(f"Top 5 topics:\n{self.topics_info.head()}")
        
        return self.model
    
    def assign_topics_to_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Assign topics to papers using fitted model.
        
        Args:
            papers: List of papers with 'abstract', 'pmid'
        
        Returns:
            Papers with added 'topic_id', 'topic_label', 'topic_probability'
        """
        if self.model is None:
            logger.error("Model not fitted. Call fit_topics() first.")
            return papers
        
        logger.info(f"Assigning topics to {len(papers)} papers...")
        
        abstracts = [
            f"{p.get('title', '')} {p.get('abstract', '')}"
            for p in papers
        ]
        
        # Transform to get topics
        topics, probs = self.model.transform(abstracts)
        
        # Add topic information to papers
        for i, paper in enumerate(papers):
            topic_id = topics[i]
            paper['topic_id'] = topic_id
            paper['topic_probability'] = float(probs[i][topic_id]) if topic_id != -1 else 0.0
            
            # Get topic label (top words)
            if topic_id != -1:
                topic_words = self.model.get_topic(topic_id)
                paper['topic_label'] = ', '.join([word for word, _ in topic_words[:5]])
            else:
                paper['topic_label'] = 'Outlier'
        
        logger.info("Topic assignment complete")
        return papers
    
    def get_topic_details(self, topic_id: int) -> Dict:
        """Get detailed information about a specific topic."""
        if self.model is None:
            return {}
        
        topic_words = self.model.get_topic(topic_id)
        
        return {
            'topic_id': topic_id,
            'words': [word for word, _ in topic_words],
            'word_scores': [float(score) for _, score in topic_words],
            'size': len(self.model.get_topic_info().loc[
                self.model.get_topic_info()['Topic'] == topic_id
            ])
        }
    
    def get_papers_by_topic(self, papers: List[Dict], topic_id: int) -> List[Dict]:
        """Get all papers assigned to a specific topic."""
        return [
            p for p in papers
            if p.get('topic_id') == topic_id
        ]
    
    def analyze_temporal_topics(
        self,
        papers: List[Dict],
        time_field: str = 'publication_year'
    ) -> Dict:
        """
        Analyze how topics evolve over time.
        
        Args:
            papers: List of papers with topics assigned
            time_field: Field containing temporal information
        
        Returns:
            Dictionary with temporal analysis results
        """
        if self.model is None:
            logger.error("Model not fitted.")
            return {}
        
        logger.info("Analyzing temporal topic evolution...")
        
        # Group papers by year and topic
        year_topic_counts = defaultdict(lambda: defaultdict(int))
        
        for paper in papers:
            year = paper.get(time_field)
            topic = paper.get('topic_id', -1)
            
            if year and topic != -1:
                year_topic_counts[year][topic] += 1
        
        # Calculate topic trends
        trends = {}
        
        for topic_id in range(max(p.get('topic_id', -1) for p in papers) + 1):
            if topic_id == -1:
                continue
            
            years = sorted(year_topic_counts.keys())
            counts = [year_topic_counts[year].get(topic_id, 0) for year in years]
            
            # Calculate trend (simple linear regression)
            if len(years) > 1:
                trend = self._calculate_trend(years, counts)
            else:
                trend = 0.0
            
            topic_details = self.get_topic_details(topic_id)
            
            trends[topic_id] = {
                'topic_label': ', '.join(topic_details['words'][:5]),
                'years': years,
                'counts': counts,
                'trend': trend,
                'total_papers': sum(counts),
                'status': 'emerging' if trend > 0.5 else 'declining' if trend < -0.5 else 'stable'
            }
        
        logger.info(f"Analyzed {len(trends)} topics over time")
        return trends
    
    def _calculate_trend(self, years: List[int], counts: List[int]) -> float:
        """Calculate simple linear trend coefficient."""
        n = len(years)
        
        if n < 2:
            return 0.0
        
        # Convert to numpy arrays
        x = np.array(years)
        y = np.array(counts)
        
        # Calculate slope
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    def find_similar_papers(
        self,
        query_paper: Dict,
        papers: List[Dict],
        top_k: int = 10
    ) -> List[Tuple[Dict, float]]:
        """
        Find papers similar to a query paper using embeddings.
        
        Args:
            query_paper: Paper with 'abstract'
            papers: List of papers to search
            top_k: Number of similar papers to return
        
        Returns:
            List of (paper, similarity_score) tuples
        """
        self._load_embedding_model()
        
        # Get query embedding
        query_text = f"{query_paper.get('title', '')} {query_paper.get('abstract', '')}"
        query_embedding = self.embedding_model.encode([query_text])[0]
        
        # Get embeddings for all papers
        paper_texts = [
            f"{p.get('title', '')} {p.get('abstract', '')}"
            for p in papers
        ]
        paper_embeddings = self.embedding_model.encode(paper_texts)
        
        # Calculate cosine similarities
        similarities = np.dot(paper_embeddings, query_embedding) / (
            np.linalg.norm(paper_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [
            (papers[i], float(similarities[i]))
            for i in top_indices
        ]
        
        return results
    
    def get_topic_statistics(self, papers: List[Dict]) -> Dict:
        """Get statistics about topic distribution."""
        if not papers:
            return {}
        
        topic_counts = defaultdict(int)
        total_papers = 0
        
        for paper in papers:
            topic = paper.get('topic_id', -1)
            if topic != -1:
                topic_counts[topic] += 1
                total_papers += 1
        
        stats = {
            'total_papers': len(papers),
            'papers_with_topics': total_papers,
            'outliers': len(papers) - total_papers,
            'num_topics': len(topic_counts),
            'topic_distribution': dict(topic_counts),
            'largest_topic': max(topic_counts.items(), key=lambda x: x[1]) if topic_counts else None,
            'smallest_topic': min(topic_counts.items(), key=lambda x: x[1]) if topic_counts else None
        }
        
        return stats
    
    def visualize_topics(self, output_path: str = 'topic_visualization.html'):
        """
        Create interactive visualization of topics.
        
        Args:
            output_path: Path to save HTML visualization
        """
        if self.model is None:
            logger.error("Model not fitted.")
            return
        
        try:
            # Create visualization
            fig = self.model.visualize_topics()
            fig.write_html(output_path)
            logger.info(f"Topic visualization saved to {output_path}")
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
    
    def save_model(self, path: str):
        """Save the fitted model to disk."""
        if self.model is None:
            logger.error("No model to save.")
            return
        
        self.model.save(path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load a fitted model from disk."""
        self.model = BERTopic.load(path)
        self._load_embedding_model()
        self.topics_info = self.model.get_topic_info()
        logger.info(f"Model loaded from {path}")


if __name__ == '__main__':
    # Test topic modeling
    logging.basicConfig(level=logging.INFO)
    
    # Sample papers for testing
    sample_papers = [
        {
            'pmid': '12345',
            'title': 'Muscle atrophy in spaceflight',
            'abstract': 'Microgravity causes skeletal muscle atrophy through protein degradation pathways...',
            'publication_year': 2020
        },
        {
            'pmid': '12346',
            'title': 'Bone loss during long-duration missions',
            'abstract': 'Astronauts experience significant bone mineral density loss during spaceflight...',
            'publication_year': 2021
        },
        {
            'pmid': '12347',
            'title': 'Radiation effects on DNA',
            'abstract': 'Cosmic radiation induces DNA damage and mutations in space travelers...',
            'publication_year': 2022
        }
    ]
    
    modeler = TopicModeler()
    
    # Fit topics (would need more papers for real use)
    # model = modeler.fit_topics(sample_papers, min_topic_size=2)
    
    # This is just a demo - real usage requires more papers
    print("TopicModeler initialized successfully")
    print("For real usage, provide at least 50-100 papers for meaningful topics")
