"""Command Line Interface for Knowledge Graph Construction"""

import click
import logging
from datetime import datetime
import json
import os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/kg_construction.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Space Biology Knowledge Graph - Construction CLI"""
    pass

@cli.command()
@click.option('--papers', default=1000, help='Number of papers to process')
@click.option('--use-curated/--no-curated', default=True, help='Use curated publications')
@click.option('--use-pubmed/--no-pubmed', default=True, help='Search PubMed')
@click.option('--use-genelab/--no-genelab', default=False, help='Include GeneLab datasets')
@click.option('--incremental', is_flag=True, help='Process only new papers')
@click.option('--start-date', default=None, help='Start date for papers (YYYY/MM/DD)')
@click.option('--end-date', default=None, help='End date for papers (YYYY/MM/DD)')
@click.option('--load-neo4j/--skip-neo4j', default=True, help='Load results into Neo4j')
@click.option('--output-dir', default='data/pipeline_output', help='Output directory')
def build(papers, use_curated, use_pubmed, use_genelab, incremental, start_date, end_date, load_neo4j, output_dir):
    """Build the knowledge graph from scientific literature."""
    from knowledge_graph.pipeline import KnowledgeGraphPipeline
    
    click.echo("=" * 70)
    click.echo("Space Biology Knowledge Graph - Construction Pipeline")
    click.echo("=" * 70)
    click.echo(f"Papers to process: {papers}")
    click.echo(f"Use curated: {use_curated}")
    click.echo(f"Use PubMed: {use_pubmed}")
    click.echo(f"Use GeneLab: {use_genelab}")
    click.echo(f"Incremental mode: {incremental}")
    click.echo(f"Date range: {start_date or 'any'} to {end_date or 'any'}")
    click.echo(f"Load to Neo4j: {load_neo4j}")
    click.echo(f"Output directory: {output_dir}")
    click.echo("=" * 70)
    
    try:
        click.echo("\nInitializing pipeline...")
        pipeline = KnowledgeGraphPipeline()
        
        results = pipeline.run(
            max_papers=papers,
            use_curated=use_curated,
            use_pubmed=use_pubmed,
            use_genelab=use_genelab,
            incremental=incremental,
            start_date=start_date,
            end_date=end_date,
            load_to_neo4j=load_neo4j,
            output_dir=output_dir
        )
        
        click.echo("\n" + "=" * 70)
        click.echo("Pipeline Completed Successfully!")
        click.echo("=" * 70)
        click.echo(f"Status: {results['status']}")
        click.echo(f"Duration: {results.get('total_duration', 0):.2f} seconds")
        click.echo("\nStage Summary:")
        
        for stage, info in results.get('stages', {}).items():
            status_icon = "✓" if info['status'] == 'complete' else "✗"
            click.echo(f"  {status_icon} {stage.replace('_', ' ').title()}: {info.get('duration', 0):.2f}s")
            
            if 'papers_acquired' in info:
                click.echo(f"      Papers: {info['papers_acquired']}")
            if 'total_entities' in info:
                click.echo(f"      Entities: {info['total_entities']}")
            if 'total_relationships' in info:
                click.echo(f"      Relationships: {info['total_relationships']}")
            if 'topics_discovered' in info:
                click.echo(f"      Topics: {info['topics_discovered']}")
            if 'graph_statistics' in info:
                stats = info['graph_statistics']
                click.echo(f"      Graph Nodes: {stats.get('total_nodes', 0)}")
                click.echo(f"      Graph Relationships: {stats.get('total_relationships', 0)}")
        
        click.echo("\n" + "=" * 70)
        click.echo(f"Results saved to: {output_dir}/pipeline_results.json")
        click.echo("=" * 70)
        
    except Exception as e:
        click.echo(f"\nError: {e}", err=True)
        logger.exception("Pipeline failed")
        raise click.Abort()

@cli.command()
def status():
    """Check the status of the knowledge graph and services."""
    click.echo("=" * 70)
    click.echo("Knowledge Graph Status")
    click.echo("=" * 70)
    
    directories = ["data/raw", "data/processed", "data/intermediate", "data/models", "data/logs"]
    
    for directory in directories:
        if os.path.exists(directory):
            click.echo(f"✓ {directory}")
        else:
            click.echo(f"✗ {directory} (missing)")
    
    click.echo("\n" + "=" * 70)

if __name__ == '__main__':
    cli()
