"""
Enhanced Data Acquisition Module for NASA Space Biology Resources

Integrates multiple NASA data sources:
1. PubMed/PMC - General scientific literature
2. NASA GeneLab - Omics datasets from spaceflight experiments
3. NASA OSDR - Open Science Data Repository
4. NASA Task Book - Research project metadata
5. NASA NSLSL - Space Life Sciences Laboratory data
6. Space Biology Publications - Curated PMC collection (jgalazka)
"""

from Bio import Entrez
import time
import logging
from typing import List, Dict, Optional
import json
import requests
import pandas as pd
from datetime import datetime
from .config import config
import io

logger = logging.getLogger(__name__)


class SpaceBiologyPublications:
    """
    Handles acquisition of curated Space Biology publications from the
    jgalazka/SB_publications GitHub repository.
    
    This is a curated list of 608+ open access Space Biology publications
    since 2010 with full text available in PubMed Central.
    
    Reference: https://github.com/jgalazka/SB_publications
    """
    
    def __init__(self, csv_url: str = None):
        """
        Initialize Space Biology Publications client.
        
        Args:
            csv_url: URL to the SB_publications CSV file
        """
        self.csv_url = csv_url or config.sb_publications_csv_url
        self.logger = logging.getLogger(__name__)
    
    def fetch_curated_publications(self) -> List[Dict]:
        """
        Fetch the curated list of Space Biology publications.
        
        Returns:
            List of publication dictionaries with title and PMC links
        """
        self.logger.info("Fetching curated Space Biology publications from GitHub...")
        
        try:
            # Download CSV
            response = requests.get(self.csv_url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV
            df = pd.read_csv(io.StringIO(response.text))
            
            publications = []
            for _, row in df.iterrows():
                # Extract PMC ID from URL
                pmc_url = row.iloc[1] if len(row) > 1 else ""
                pmc_id = self._extract_pmc_id(pmc_url)
                
                pub = {
                    'title': row.iloc[0] if len(row) > 0 else "",
                    'pmc_url': pmc_url,
                    'pmc_id': pmc_id,
                    'source': 'SB_publications_curated',
                    'full_text_available': True,
                    'curated': True,
                    'publication_year_min': 2010  # All papers are from 2010+
                }
                publications.append(pub)
            
            self.logger.info(f"Retrieved {len(publications)} curated Space Biology publications")
            return publications
            
        except Exception as e:
            self.logger.error(f"Error fetching curated publications: {e}")
            return []
    
    def _extract_pmc_id(self, pmc_url: str) -> Optional[str]:
        """Extract PMC ID from PMC URL."""
        if not pmc_url or not isinstance(pmc_url, str):
            return None
        
        # URL format: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/
        import re
        match = re.search(r'PMC(\d+)', pmc_url)
        if match:
            return f"PMC{match.group(1)}"
        return None
    
    def get_pmc_ids(self) -> List[str]:
        """
        Get list of PMC IDs from curated publications.
        
        Returns:
            List of PMC IDs
        """
        publications = self.fetch_curated_publications()
        return [pub['pmc_id'] for pub in publications if pub.get('pmc_id')]


class NASATaskBook:
    """
    Handles acquisition of research project metadata from NASA Task Book.
    
    The Task Book contains information about NASA-funded space biology
    research projects, including objectives, methods, and results.
    
    Reference: https://taskbook.nasaprs.com/tbp/
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize NASA Task Book client.
        
        Args:
            base_url: Base URL for Task Book
        """
        self.base_url = base_url or config.taskbook_url
        self.logger = logging.getLogger(__name__)
    
    def search_projects(
        self,
        keyword: str = None,
        division: str = "Space Biology",
        status: str = "Active"
    ) -> List[Dict]:
        """
        Search Task Book for research projects.
        
        Args:
            keyword: Search keyword (e.g., "microgravity", "muscle")
            division: NASA division (default: Space Biology)
            status: Project status (Active, Completed, All)
            
        Returns:
            List of project metadata
        """
        self.logger.info(f"Searching NASA Task Book for projects: {keyword}")
        
        # Note: Task Book may require web scraping or specific API access
        # This is a placeholder structure for project metadata
        
        projects = []
        
        # Example project structure based on Task Book format
        project_template = {
            'task_id': '',
            'title': '',
            'principal_investigator': '',
            'organization': '',
            'division': division,
            'status': status,
            'start_date': '',
            'end_date': '',
            'description': '',
            'objectives': [],
            'keywords': [],
            'publications': [],
            'source': 'NASA_TaskBook'
        }
        
        self.logger.warning("Task Book integration requires authentication/API access")
        self.logger.info("Using placeholder structure - implement web scraping if needed")
        
        return projects
    
    def get_project_publications(self, task_id: str) -> List[str]:
        """
        Get publication PMIDs associated with a Task Book project.
        
        Args:
            task_id: Task Book project ID
            
        Returns:
            List of PMIDs
        """
        # Placeholder for Task Book -> PubMed linking
        return []


class NASAOSDR:
    """
    Handles acquisition from NASA Open Science Data Repository (OSDR).
    
    OSDR provides access to spaceflight and space-relevant datasets,
    including omics, imaging, and physiological data.
    
    Reference: https://www.nasa.gov/osdr/
    """
    
    def __init__(self, api_url: str = None):
        """
        Initialize NASA OSDR client.
        
        Args:
            api_url: Base URL for OSDR API
        """
        self.base_url = api_url or config.osdr_api_url
        self.logger = logging.getLogger(__name__)
    
    def search_datasets(
        self,
        query: str = None,
        data_type: str = None,
        organism: str = None
    ) -> List[Dict]:
        """
        Search OSDR for datasets.
        
        Args:
            query: Search query
            data_type: Type of data (e.g., "transcriptomics", "proteomics")
            organism: Organism name
            
        Returns:
            List of dataset metadata
        """
        self.logger.info(f"Searching NASA OSDR: {query}")
        
        search_url = f"{self.base_url}/search"
        
        params = {}
        if query:
            params['q'] = query
        if data_type:
            params['data_type'] = data_type
        if organism:
            params['organism'] = organism
        
        try:
            response = requests.get(search_url, params=params, timeout=30)
            
            # OSDR may have different API structure - adapt as needed
            if response.status_code == 200:
                data = response.json()
                datasets = data.get('datasets', [])
                
                self.logger.info(f"Found {len(datasets)} datasets in OSDR")
                return datasets
            else:
                self.logger.warning(f"OSDR returned status {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching OSDR: {e}")
            return []
    
    def get_dataset_metadata(self, dataset_id: str) -> Dict:
        """
        Get detailed metadata for an OSDR dataset.
        
        Args:
            dataset_id: OSDR dataset ID
            
        Returns:
            Dataset metadata dictionary
        """
        metadata_url = f"{self.base_url}/datasets/{dataset_id}"
        
        try:
            response = requests.get(metadata_url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching OSDR dataset {dataset_id}: {e}")
            return {}
    
    def link_to_publications(self, dataset_id: str) -> List[str]:
        """
        Get publication PMIDs associated with an OSDR dataset.
        
        Args:
            dataset_id: OSDR dataset ID
            
        Returns:
            List of PMIDs
        """
        metadata = self.get_dataset_metadata(dataset_id)
        
        # Extract PMIDs from metadata
        pmids = []
        if 'publications' in metadata:
            for pub in metadata['publications']:
                if 'pmid' in pub:
                    pmids.append(pub['pmid'])
        
        return pmids


class NASANSLSL:
    """
    Handles acquisition from NASA Space Life Sciences Laboratory (NSLSL).
    
    NSLSL at Kennedy Space Center provides data from ground-based
    space biology research and flight preparation.
    
    Reference: https://public.ksc.nasa.gov/nslsl/
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize NASA NSLSL client.
        
        Args:
            base_url: Base URL for NSLSL
        """
        self.base_url = base_url or config.nslsl_url
        self.logger = logging.getLogger(__name__)
    
    def get_facility_info(self) -> Dict:
        """
        Get information about NSLSL facilities and capabilities.
        
        Returns:
            Facility information
        """
        self.logger.info("Fetching NSLSL facility information")
        
        # NSLSL may require web scraping or specific access
        facility_info = {
            'name': 'NASA Space Life Sciences Laboratory',
            'location': 'Kennedy Space Center, Florida',
            'capabilities': [
                'Cell culture',
                'Molecular biology',
                'Microbiology',
                'Plant biology',
                'Hardware testing'
            ],
            'source': 'NSLSL'
        }
        
        return facility_info
    
    def search_experiments(self, keyword: str = None) -> List[Dict]:
        """
        Search for experiments conducted at NSLSL.
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of experiment metadata
        """
        self.logger.info(f"Searching NSLSL experiments: {keyword}")
        
        # Placeholder - requires implementation based on NSLSL data structure
        experiments = []
        
        return experiments


class IntegratedDataAcquisition:
    """
    Unified interface for acquiring data from all NASA Space Biology sources.
    
    This class coordinates data acquisition across multiple repositories:
    - PubMed/PMC
    - NASA GeneLab
    - NASA OSDR
    - NASA Task Book
    - NASA NSLSL
    - Curated Space Biology Publications
    """
    
    def __init__(self):
        """Initialize all data acquisition clients."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize clients
        from .data_acquisition import PubMedAcquisition, GeneLabAcquisition
        
        self.pubmed = PubMedAcquisition()
        self.genelab = GeneLabAcquisition()
        self.sb_publications = SpaceBiologyPublications()
        self.taskbook = NASATaskBook()
        self.osdr = NASAOSDR()
        self.nslsl = NASANSLSL()
        
        self.logger.info("Initialized integrated data acquisition system")
    
    def acquire_all_sources(
        self,
        use_curated: bool = True,
        use_pubmed: bool = True,
        use_genelab: bool = True,
        use_osdr: bool = True,
        max_papers: int = 1000
    ) -> Dict:
        """
        Acquire data from all available sources.
        
        Args:
            use_curated: Include curated Space Biology publications
            use_pubmed: Include PubMed search
            use_genelab: Include GeneLab datasets
            use_osdr: Include OSDR datasets
            max_papers: Maximum papers from PubMed search
            
        Returns:
            Dictionary with data from all sources
        """
        results = {
            'curated_publications': [],
            'pubmed_papers': [],
            'genelab_datasets': [],
            'osdr_datasets': [],
            'total_publications': 0,
            'acquisition_timestamp': datetime.utcnow().isoformat()
        }
        
        # 1. Curated Space Biology Publications (highest priority)
        if use_curated:
            self.logger.info("Acquiring curated Space Biology publications...")
            curated = self.sb_publications.fetch_curated_publications()
            results['curated_publications'] = curated
            self.logger.info(f"✓ Acquired {len(curated)} curated publications")
        
        # 2. PubMed search (for additional papers)
        if use_pubmed:
            self.logger.info("Searching PubMed for space biology papers...")
            pmids = self.pubmed.search_space_biology_papers(max_results=max_papers)
            
            # Exclude PMIDs already in curated list
            curated_pmids = set()
            for pub in results['curated_publications']:
                if pub.get('pmc_id'):
                    # Would need to map PMC -> PMID
                    pass
            
            # Fetch details for new papers
            new_pmids = list(set(pmids) - curated_pmids)[:max_papers]
            if new_pmids:
                papers = self.pubmed.fetch_paper_details(new_pmids)
                results['pubmed_papers'] = papers
                self.logger.info(f"✓ Acquired {len(papers)} additional PubMed papers")
        
        # 3. GeneLab datasets
        if use_genelab:
            self.logger.info("Fetching GeneLab datasets...")
            datasets = self.genelab.list_all_datasets()
            results['genelab_datasets'] = datasets
            self.logger.info(f"✓ Found {len(datasets)} GeneLab datasets")
        
        # 4. OSDR datasets
        if use_osdr:
            self.logger.info("Fetching OSDR datasets...")
            datasets = self.osdr.search_datasets(query="spaceflight")
            results['osdr_datasets'] = datasets
            self.logger.info(f"✓ Found {len(datasets)} OSDR datasets")
        
        # Calculate totals
        results['total_publications'] = (
            len(results['curated_publications']) +
            len(results['pubmed_papers'])
        )
        
        self.logger.info(f"Total publications acquired: {results['total_publications']}")
        
        return results
    
    def get_priority_papers(self, limit: int = 100) -> List[Dict]:
        """
        Get highest priority papers for knowledge graph construction.
        
        Priority order:
        1. Curated Space Biology publications (full text available)
        2. Recent high-impact PubMed papers
        3. Papers linked to GeneLab/OSDR datasets
        
        Args:
            limit: Maximum number of papers to return
            
        Returns:
            List of paper dictionaries
        """
        self.logger.info(f"Acquiring top {limit} priority papers...")
        
        papers = []
        
        # Start with curated publications
        curated = self.sb_publications.fetch_curated_publications()
        papers.extend(curated[:limit])
        
        # If we need more, search PubMed
        if len(papers) < limit:
            remaining = limit - len(papers)
            pmids = self.pubmed.search_space_biology_papers(max_results=remaining)
            additional = self.pubmed.fetch_paper_details(pmids[:remaining])
            papers.extend(additional)
        
        self.logger.info(f"✓ Acquired {len(papers)} priority papers")
        
        return papers[:limit]


# Export classes
__all__ = [
    'SpaceBiologyPublications',
    'NASATaskBook',
    'NASAOSDR',
    'NASANSLSL',
    'IntegratedDataAcquisition'
]
