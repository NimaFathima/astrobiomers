"""
Entity Resolution Module for Space Biology Knowledge Graph

Links extracted entities to standard databases:
- Genes/Proteins: MyGene.info, UniProt
- Diseases: Mondo, Disease Ontology
- Chemicals: PubChem, ChEMBL
- Species: NCBI Taxonomy
- Cell Types: Cell Ontology

Author: Space Biology KG Team
Date: October 2025
"""

import logging
import requests
from typing import List, Dict, Optional, Set
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


class EntityResolver:
    """
    Resolve entities to standardized database identifiers.
    
    Provides cross-references and canonical names.
    """
    
    def __init__(self, config=None):
        """Initialize entity resolver."""
        from knowledge_graph.config import config as default_config
        
        self.config = config or default_config
        
        # API endpoints
        self.mygene_url = "https://mygene.info/v3"
        self.uniprot_url = "https://www.uniprot.org/uniprot"
        self.ncbi_taxonomy_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.pubchem_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        
        # Caching
        self.gene_cache = {}
        self.taxonomy_cache = {}
        self.chemical_cache = {}
        
        logger.info("EntityResolver initialized")
    
    def resolve_entities_batch(self, entities: List[Dict]) -> List[Dict]:
        """
        Resolve a batch of entities to database IDs.
        
        Args:
            entities: List of entities with 'text', 'type'
        
        Returns:
            Entities with added database IDs and metadata
        """
        logger.info(f"Resolving {len(entities)} entities...")
        
        resolved = []
        
        # Group by entity type for efficient batch processing
        by_type = defaultdict(list)
        for entity in entities:
            by_type[entity['type']].append(entity)
        
        # Resolve each type
        for entity_type, type_entities in by_type.items():
            if entity_type in ['GENE', 'PROTEIN']:
                resolved.extend(self._resolve_genes_batch(type_entities))
            elif entity_type == 'DISEASE':
                resolved.extend(self._resolve_diseases_batch(type_entities))
            elif entity_type == 'CHEMICAL':
                resolved.extend(self._resolve_chemicals_batch(type_entities))
            elif entity_type == 'ORGANISM':
                resolved.extend(self._resolve_organisms_batch(type_entities))
            elif entity_type == 'CELL_TYPE':
                resolved.extend(self._resolve_cell_types_batch(type_entities))
            else:
                # Keep unresolved entities
                resolved.extend(type_entities)
        
        logger.info(f"Resolved {len(resolved)} entities")
        return resolved
    
    def _resolve_genes_batch(self, genes: List[Dict]) -> List[Dict]:
        """Resolve genes using MyGene.info API."""
        logger.info(f"Resolving {len(genes)} genes...")
        
        resolved = []
        
        # Extract unique gene symbols
        gene_symbols = list(set([g['text'] for g in genes]))
        
        # Query MyGene.info in batches
        batch_size = 100
        for i in range(0, len(gene_symbols), batch_size):
            batch = gene_symbols[i:i+batch_size]
            
            # Check cache first
            cached_results = {}
            uncached = []
            
            for symbol in batch:
                if symbol in self.gene_cache:
                    cached_results[symbol] = self.gene_cache[symbol]
                else:
                    uncached.append(symbol)
            
            # Query API for uncached
            if uncached:
                try:
                    response = requests.post(
                        f"{self.mygene_url}/query",
                        json={
                            'q': uncached,
                            'scopes': 'symbol,alias',
                            'fields': 'symbol,name,entrezgene,uniprot,ensembl.gene,summary',
                            'species': 'human,mouse,rat'
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        results = response.json()
                        
                        for result in results:
                            if 'notfound' not in result:
                                query = result.get('query', '')
                                self.gene_cache[query] = result
                                cached_results[query] = result
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error querying MyGene.info: {e}")
        
        # Add resolved info to genes
        for gene in genes:
            gene_symbol = gene['text']
            
            if gene_symbol in cached_results:
                info = cached_results[gene_symbol]
                
                gene['entrez_id'] = info.get('entrezgene')
                gene['official_symbol'] = info.get('symbol')
                gene['gene_name'] = info.get('name')
                gene['uniprot_id'] = info.get('uniprot', {}).get('Swiss-Prot')
                gene['ensembl_id'] = info.get('ensembl', {}).get('gene')
                gene['summary'] = info.get('summary', '')[:500]  # Truncate
                gene['resolved'] = True
            else:
                gene['resolved'] = False
            
            resolved.append(gene)
        
        return resolved
    
    def _resolve_diseases_batch(self, diseases: List[Dict]) -> List[Dict]:
        """
        Resolve diseases using pattern matching.
        
        Note: Full disease resolution would require Mondo/DO API or local files.
        This is a simplified version using common patterns.
        """
        logger.info(f"Resolving {len(diseases)} diseases...")
        
        # Common disease mappings (simplified)
        disease_map = {
            'muscle atrophy': {'mondo_id': 'MONDO:0005015', 'doid': 'DOID:767'},
            'bone loss': {'mondo_id': 'MONDO:0005298', 'doid': 'DOID:11476'},
            'osteoporosis': {'mondo_id': 'MONDO:0005298', 'doid': 'DOID:11476'},
            'cardiovascular disease': {'mondo_id': 'MONDO:0005267', 'doid': 'DOID:1287'},
            'immune dysfunction': {'mondo_id': 'MONDO:0005046', 'doid': 'DOID:2914'},
            'cancer': {'mondo_id': 'MONDO:0004992', 'doid': 'DOID:162'},
            'radiation sickness': {'mondo_id': 'MONDO:0006639', 'doid': 'DOID:0080054'}
        }
        
        for disease in diseases:
            disease_text = disease['text'].lower()
            
            # Try exact match
            if disease_text in disease_map:
                disease['mondo_id'] = disease_map[disease_text]['mondo_id']
                disease['doid'] = disease_map[disease_text]['doid']
                disease['resolved'] = True
            else:
                # Try partial match
                found = False
                for key, value in disease_map.items():
                    if key in disease_text or disease_text in key:
                        disease['mondo_id'] = value['mondo_id']
                        disease['doid'] = value['doid']
                        disease['resolved'] = True
                        found = True
                        break
                
                if not found:
                    disease['resolved'] = False
        
        return diseases
    
    def _resolve_chemicals_batch(self, chemicals: List[Dict]) -> List[Dict]:
        """
        Resolve chemicals using PubChem.
        
        Note: This is rate-limited. For production, consider local ChEMBL database.
        """
        logger.info(f"Resolving {len(chemicals)} chemicals...")
        
        for chemical in chemicals:
            chem_name = chemical['text']
            
            # Check cache
            if chem_name in self.chemical_cache:
                cached = self.chemical_cache[chem_name]
                chemical.update(cached)
                chemical['resolved'] = True
                continue
            
            try:
                # Query PubChem
                response = requests.get(
                    f"{self.pubchem_url}/compound/name/{chem_name}/JSON",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    compound = data.get('PC_Compounds', [{}])[0]
                    
                    if compound:
                        cid = compound.get('id', {}).get('id', {}).get('cid')
                        
                        chemical['pubchem_cid'] = cid
                        chemical['resolved'] = True
                        
                        # Cache result
                        self.chemical_cache[chem_name] = {
                            'pubchem_cid': cid,
                            'resolved': True
                        }
                else:
                    chemical['resolved'] = False
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Could not resolve chemical {chem_name}: {e}")
                chemical['resolved'] = False
        
        return chemicals
    
    def _resolve_organisms_batch(self, organisms: List[Dict]) -> List[Dict]:
        """Resolve organisms using NCBI Taxonomy."""
        logger.info(f"Resolving {len(organisms)} organisms...")
        
        # Common organism mappings
        organism_map = {
            'human': {'taxid': '9606', 'scientific_name': 'Homo sapiens'},
            'humans': {'taxid': '9606', 'scientific_name': 'Homo sapiens'},
            'homo sapiens': {'taxid': '9606', 'scientific_name': 'Homo sapiens'},
            'mouse': {'taxid': '10090', 'scientific_name': 'Mus musculus'},
            'mice': {'taxid': '10090', 'scientific_name': 'Mus musculus'},
            'mus musculus': {'taxid': '10090', 'scientific_name': 'Mus musculus'},
            'rat': {'taxid': '10116', 'scientific_name': 'Rattus norvegicus'},
            'rats': {'taxid': '10116', 'scientific_name': 'Rattus norvegicus'},
            'rattus norvegicus': {'taxid': '10116', 'scientific_name': 'Rattus norvegicus'},
            'arabidopsis': {'taxid': '3702', 'scientific_name': 'Arabidopsis thaliana'},
            'drosophila': {'taxid': '7227', 'scientific_name': 'Drosophila melanogaster'},
            'c. elegans': {'taxid': '6239', 'scientific_name': 'Caenorhabditis elegans'},
            'e. coli': {'taxid': '562', 'scientific_name': 'Escherichia coli'}
        }
        
        for organism in organisms:
            org_text = organism['text'].lower()
            
            if org_text in organism_map:
                organism['ncbi_taxid'] = organism_map[org_text]['taxid']
                organism['scientific_name'] = organism_map[org_text]['scientific_name']
                organism['resolved'] = True
            else:
                organism['resolved'] = False
        
        return organisms
    
    def _resolve_cell_types_batch(self, cell_types: List[Dict]) -> List[Dict]:
        """
        Resolve cell types using pattern matching.
        
        Note: Full resolution would use Cell Ontology (CL).
        """
        logger.info(f"Resolving {len(cell_types)} cell types...")
        
        # Common cell type mappings
        cell_type_map = {
            'muscle cell': 'CL:0000187',
            'skeletal muscle': 'CL:0000188',
            'cardiac muscle': 'CL:0000746',
            'osteoblast': 'CL:0000062',
            'osteoclast': 'CL:0000092',
            'bone cell': 'CL:0001035',
            'immune cell': 'CL:0000738',
            't cell': 'CL:0000084',
            'b cell': 'CL:0000236',
            'macrophage': 'CL:0000235',
            'neuron': 'CL:0000540',
            'endothelial cell': 'CL:0000115'
        }
        
        for cell_type in cell_types:
            cell_text = cell_type['text'].lower()
            
            if cell_text in cell_type_map:
                cell_type['cl_id'] = cell_type_map[cell_text]
                cell_type['resolved'] = True
            else:
                # Try partial match
                found = False
                for key, value in cell_type_map.items():
                    if key in cell_text or cell_text in key:
                        cell_type['cl_id'] = value
                        cell_type['resolved'] = True
                        found = True
                        break
                
                if not found:
                    cell_type['resolved'] = False
        
        return cell_types
    
    def get_resolution_statistics(self, entities: List[Dict]) -> Dict:
        """Get statistics about entity resolution."""
        stats = {
            'total_entities': len(entities),
            'resolved': 0,
            'unresolved': 0,
            'by_type': defaultdict(lambda: {'total': 0, 'resolved': 0})
        }
        
        for entity in entities:
            entity_type = entity.get('type', 'UNKNOWN')
            is_resolved = entity.get('resolved', False)
            
            stats['by_type'][entity_type]['total'] += 1
            
            if is_resolved:
                stats['resolved'] += 1
                stats['by_type'][entity_type]['resolved'] += 1
            else:
                stats['unresolved'] += 1
        
        # Calculate percentages
        if stats['total_entities'] > 0:
            stats['resolution_rate'] = stats['resolved'] / stats['total_entities']
        else:
            stats['resolution_rate'] = 0.0
        
        # Convert defaultdict to dict
        stats['by_type'] = dict(stats['by_type'])
        
        return stats
    
    def create_entity_mapping(self, entities: List[Dict]) -> Dict[str, List[str]]:
        """
        Create mapping from entity text to database IDs.
        
        Returns:
            Dictionary mapping entity text -> list of IDs
        """
        mapping = defaultdict(list)
        
        for entity in entities:
            if not entity.get('resolved'):
                continue
            
            text = entity['text']
            entity_type = entity.get('type')
            
            # Add relevant IDs based on type
            if entity_type in ['GENE', 'PROTEIN']:
                if entity.get('entrez_id'):
                    mapping[text].append(f"ENTREZ:{entity['entrez_id']}")
                if entity.get('uniprot_id'):
                    mapping[text].append(f"UNIPROT:{entity['uniprot_id']}")
                if entity.get('ensembl_id'):
                    mapping[text].append(f"ENSEMBL:{entity['ensembl_id']}")
            
            elif entity_type == 'DISEASE':
                if entity.get('mondo_id'):
                    mapping[text].append(entity['mondo_id'])
                if entity.get('doid'):
                    mapping[text].append(entity['doid'])
            
            elif entity_type == 'CHEMICAL':
                if entity.get('pubchem_cid'):
                    mapping[text].append(f"PUBCHEM:{entity['pubchem_cid']}")
            
            elif entity_type == 'ORGANISM':
                if entity.get('ncbi_taxid'):
                    mapping[text].append(f"TAXID:{entity['ncbi_taxid']}")
            
            elif entity_type == 'CELL_TYPE':
                if entity.get('cl_id'):
                    mapping[text].append(entity['cl_id'])
        
        return dict(mapping)


if __name__ == '__main__':
    # Test entity resolution
    logging.basicConfig(level=logging.INFO)
    
    resolver = EntityResolver()
    
    # Test entities
    test_entities = [
        {'text': 'IGF-1', 'type': 'GENE'},
        {'text': 'mTOR', 'type': 'GENE'},
        {'text': 'TP53', 'type': 'GENE'},
        {'text': 'muscle atrophy', 'type': 'DISEASE'},
        {'text': 'osteoporosis', 'type': 'DISEASE'},
        {'text': 'human', 'type': 'ORGANISM'},
        {'text': 'mouse', 'type': 'ORGANISM'},
        {'text': 'skeletal muscle', 'type': 'CELL_TYPE'}
    ]
    
    # Resolve
    resolved = resolver.resolve_entities_batch(test_entities)
    
    print("\nResolved Entities:")
    for entity in resolved:
        print(f"\n{entity['text']} ({entity['type']})")
        print(f"  Resolved: {entity.get('resolved', False)}")
        
        if entity.get('entrez_id'):
            print(f"  Entrez ID: {entity['entrez_id']}")
        if entity.get('uniprot_id'):
            print(f"  UniProt ID: {entity['uniprot_id']}")
        if entity.get('mondo_id'):
            print(f"  Mondo ID: {entity['mondo_id']}")
        if entity.get('ncbi_taxid'):
            print(f"  NCBI Taxonomy ID: {entity['ncbi_taxid']}")
        if entity.get('cl_id'):
            print(f"  Cell Ontology ID: {entity['cl_id']}")
    
    # Get statistics
    stats = resolver.get_resolution_statistics(resolved)
    print(f"\n\nResolution Statistics:")
    print(f"  Total: {stats['total_entities']}")
    print(f"  Resolved: {stats['resolved']}")
    print(f"  Resolution rate: {stats['resolution_rate']:.1%}")
    print(f"  By type: {stats['by_type']}")
