"""
Data Acquisition Module

Handles systematic acquisition of scientific publications from:
- PubMed and PubMed Central (via NCBI E-utilities)
- NASA GeneLab
- NASA Open Science Data Repository (OSDR)
"""

from Bio import Entrez
import time
import logging
from typing import List, Dict, Optional
import json
import requests
from datetime import datetime
from .config import config

logger = logging.getLogger(__name__)


class PubMedAcquisition:
    """
    Handles systematic acquisition of publications from PubMed.
    """
    
    def __init__(self, email: str = None, api_key: str = None):
        """
        Initialize PubMed acquisition client.
        
        Args:
            email: Email for NCBI (required)
            api_key: NCBI API key (optional, increases rate limits)
        """
        Entrez.email = email or config.pubmed_email
        if api_key or config.pubmed_api_key:
            Entrez.api_key = api_key or config.pubmed_api_key
        
        self.logger = logging.getLogger(__name__)
        self.rate_limit = config.pubmed_rate_limit
        self.batch_size = config.pubmed_batch_size
        self.base_url = config.PUBMED_EUTILS_BASE
        self.email = Entrez.email
        
    def search_space_biology_papers(
        self, 
        start_date: str = None,
        end_date: str = None,
        max_results: int = None
    ) -> List[str]:
        """
        Search PubMed for space biology papers.
        
        Args:
            start_date: Start date (YYYY/MM/DD)
            end_date: End date (YYYY/MM/DD)
            max_results: Maximum number of results to return
            
        Returns:
            List of PMIDs
        """
        start_date = start_date or config.start_date
        end_date = end_date or config.end_date
        max_results = max_results or config.max_papers_per_run
        
        query = self._build_query(start_date, end_date)
        
        self.logger.info(f"Searching PubMed with query: {query[:200]}...")
        
        try:
            # Initial search to get count and IDs
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="pub_date",
                usehistory="y"  # Use history server for large result sets
            )
            
            record = Entrez.read(handle)
            handle.close()
            
            count = int(record["Count"])
            self.logger.info(f"Found {count} papers matching criteria")
            
            # Get all PMIDs
            pmids = record["IdList"]
            
            # If more results than retmax, fetch in batches using history
            if count > max_results:
                webenv = record["WebEnv"]
                query_key = record["QueryKey"]
                pmids = self._fetch_all_pmids(webenv, query_key, min(count, max_results))
            
            self.logger.info(f"Retrieved {len(pmids)} PMIDs")
            return pmids
            
        except Exception as e:
            self.logger.error(f"Error searching PubMed: {e}")
            raise
    
    def _build_query(self, start_date: str, end_date: str) -> str:
        """Construct comprehensive PubMed query."""
        stressor_query = " OR ".join([
            f'"{term}"[Title/Abstract]' for term in config.space_biology_stressors
        ])
        bio_query = " OR ".join([
            f'"{term}"[Title/Abstract]' for term in config.biological_terms
        ])
        
        query = f"({stressor_query}) AND ({bio_query})"
        query += f' AND ("{start_date}"[Date - Publication] : "{end_date}"[Date - Publication])'
        query += " AND hasabstract AND english[Language]"
        
        return query
    
    def _fetch_all_pmids(self, webenv: str, query_key: str, count: int) -> List[str]:
        """Fetch all PMIDs using history server."""
        all_pmids = []
        
        for start in range(0, count, self.batch_size):
            self.logger.info(f"Fetching PMIDs {start} to {start + self.batch_size}")
            
            try:
                handle = Entrez.esearch(
                    db="pubmed",
                    WebEnv=webenv,
                    query_key=query_key,
                    retstart=start,
                    retmax=self.batch_size
                )
                
                record = Entrez.read(handle)
                handle.close()
                
                all_pmids.extend(record["IdList"])
                
                # Rate limiting
                time.sleep(self.rate_limit)
                
            except Exception as e:
                self.logger.error(f"Error fetching PMIDs batch at {start}: {e}")
                continue
        
        return all_pmids
    
    def fetch_paper_details(self, pmids: List[str]) -> List[Dict]:
        """
        Fetch detailed information for papers.
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of paper dictionaries with metadata
        """
        papers = []
        total_batches = (len(pmids) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(pmids), self.batch_size):
            batch = pmids[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            
            self.logger.info(f"Fetching batch {batch_num}/{total_batches}: {len(batch)} papers")
            
            try:
                handle = Entrez.efetch(
                    db="pubmed",
                    id=",".join(batch),
                    rettype="xml",
                    retmode="xml"
                )
                
                records = Entrez.read(handle)
                handle.close()
                
                # Parse each article
                for article in records['PubmedArticle']:
                    try:
                        paper = self._parse_article(article)
                        papers.append(paper)
                    except Exception as e:
                        self.logger.error(f"Error parsing article: {e}")
                        continue
                
                # Rate limiting
                time.sleep(self.rate_limit)
                
            except Exception as e:
                self.logger.error(f"Error fetching batch {batch_num}: {e}")
                continue
        
        self.logger.info(f"Successfully fetched {len(papers)} papers")
        return papers
    
    def _parse_article(self, article) -> Dict:
        """Extract relevant fields from PubMed article XML."""
        medline = article['MedlineCitation']
        article_data = medline['Article']
        
        # Basic metadata
        pmid = str(medline['PMID'])
        title = article_data.get('ArticleTitle', '')
        
        # Abstract
        abstract = ""
        if 'Abstract' in article_data:
            abstract_texts = article_data['Abstract'].get('AbstractText', [])
            if isinstance(abstract_texts, list):
                abstract = " ".join([str(text) for text in abstract_texts])
            else:
                abstract = str(abstract_texts)
        
        # Authors
        authors = []
        if 'AuthorList' in article_data:
            for author in article_data['AuthorList']:
                if 'LastName' in author and 'ForeName' in author:
                    authors.append(f"{author['ForeName']} {author['LastName']}")
                elif 'CollectiveName' in author:
                    authors.append(author['CollectiveName'])
        
        # Journal
        journal = article_data.get('Journal', {}).get('Title', '')
        
        # Publication date
        pub_date = self._extract_publication_date(article_data)
        
        # DOI
        doi = None
        if 'ELocationID' in article_data:
            for eloc in article_data['ELocationID']:
                if eloc.attributes.get('EIdType') == 'doi':
                    doi = str(eloc)
        
        # Article IDs (PMC, DOI)
        pmc_id = None
        if 'PubmedData' in article and 'ArticleIdList' in article['PubmedData']:
            for article_id in article['PubmedData']['ArticleIdList']:
                if article_id.attributes.get('IdType') == 'pmc':
                    pmc_id = str(article_id)
                elif article_id.attributes.get('IdType') == 'doi' and not doi:
                    doi = str(article_id)
        
        # MeSH terms
        mesh_terms = []
        if 'MeshHeadingList' in medline:
            for mesh in medline['MeshHeadingList']:
                mesh_terms.append(str(mesh['DescriptorName']))
        
        # Keywords
        keywords = []
        if 'KeywordList' in medline:
            for keyword_list in medline['KeywordList']:
                keywords.extend([str(k) for k in keyword_list])
        
        return {
            'pmid': pmid,
            'pmc_id': pmc_id,
            'doi': doi,
            'title': title,
            'abstract': abstract,
            'authors': authors,
            'journal': journal,
            'publication_date': pub_date,
            'publication_year': int(pub_date.split('-')[0]) if pub_date else None,
            'mesh_terms': mesh_terms,
            'keywords': keywords,
            'full_text_available': pmc_id is not None,
            'acquired_at': datetime.utcnow().isoformat()
        }
    
    def _extract_publication_date(self, article_data) -> Optional[str]:
        """Extract and standardize publication date."""
        # Try ArticleDate first
        if 'ArticleDate' in article_data and len(article_data['ArticleDate']) > 0:
            date = article_data['ArticleDate'][0]
            year = date.get('Year', '2000')
            month = date.get('Month', '01').zfill(2)
            day = date.get('Day', '01').zfill(2)
            return f"{year}-{month}-{day}"
        
        # Fall back to JournalIssue PubDate
        if 'Journal' in article_data and 'JournalIssue' in article_data['Journal']:
            pub_date = article_data['Journal']['JournalIssue'].get('PubDate', {})
            year = pub_date.get('Year', '2000')
            
            # Try to get month
            month = pub_date.get('Month', '01')
            # Convert month names to numbers
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            if month in month_map:
                month = month_map[month]
            elif not month.isdigit():
                month = '01'
            
            return f"{year}-{month.zfill(2)}-01"
        
        return None
    
    def download_full_text(self, pmc_id: str, output_dir: str) -> Optional[str]:
        """
        Download full text from PubMed Central.
        
        Args:
            pmc_id: PMC identifier (e.g., "PMC1234567")
            output_dir: Directory to save the text
            
        Returns:
            Path to downloaded file
        """
        try:
            handle = Entrez.efetch(
                db="pmc",
                id=pmc_id,
                rettype="xml",
                retmode="xml"
            )
            
            content = handle.read()
            handle.close()
            
            # Save to file
            import os
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{pmc_id}.xml")
            
            with open(output_path, 'wb') as f:
                f.write(content)
            
            self.logger.info(f"Downloaded full text for {pmc_id}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error downloading {pmc_id}: {e}")
            return None


class GeneLabAcquisition:
    """
    Handles acquisition of omics datasets from NASA GeneLab.
    """
    
    def __init__(self, api_url: str = None):
        """
        Initialize GeneLab acquisition client.
        
        Args:
            api_url: Base URL for GeneLab API
        """
        self.base_url = api_url or config.genelab_api_url
        self.logger = logging.getLogger(__name__)
    
    def search_datasets(
        self, 
        organism: str = None,
        assay_type: str = None,
        factor: str = None
    ) -> List[Dict]:
        """
        Search GeneLab for datasets.
        
        Args:
            organism: Organism name (e.g., "Mus musculus")
            assay_type: Type of assay (e.g., "RNA sequencing")
            factor: Experimental factor (e.g., "Spaceflight")
            
        Returns:
            List of dataset metadata
        """
        search_url = f"{self.base_url}/search"
        
        params = {
            'term': '',
            'type': 'cgene'
        }
        
        # Build search term
        terms = []
        if organism:
            terms.append(f"organism:{organism}")
        if assay_type:
            terms.append(f"assay_type:{assay_type}")
        if factor:
            terms.append(f"factor:{factor}")
        
        params['term'] = " AND ".join(terms) if terms else "spaceflight"
        
        try:
            self.logger.info(f"Searching GeneLab with term: {params['term']}")
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            studies = data.get('studies', [])
            
            self.logger.info(f"Found {len(studies)} GeneLab studies")
            return studies
            
        except Exception as e:
            self.logger.error(f"Error searching GeneLab: {e}")
            return []
    
    def get_dataset_metadata(self, glds_id: str) -> Dict:
        """
        Get detailed metadata for a GeneLab dataset.
        
        Args:
            glds_id: GeneLab dataset ID (e.g., "GLDS-242")
            
        Returns:
            Dataset metadata dictionary
        """
        metadata_url = f"{self.base_url}/glds/metadata/{glds_id}"
        
        try:
            self.logger.info(f"Fetching metadata for {glds_id}")
            response = requests.get(metadata_url, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error fetching metadata for {glds_id}: {e}")
            return {}
    
    def list_all_datasets(self) -> List[Dict]:
        """
        List all available datasets in GeneLab.
        
        Returns:
            List of all dataset metadata
        """
        return self.search_datasets()


# Backward compatibility aliases
class PubMedDataAcquisition(PubMedAcquisition):
    """Alias maintained for legacy imports."""


class NASADataAcquisition(GeneLabAcquisition):
    """Alias maintained for legacy naming conventions."""
