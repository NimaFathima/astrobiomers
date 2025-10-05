"""
Setup and Installation Script for Knowledge Graph Construction

This script helps set up the environment for building the Space Biology Knowledge Graph.
It installs required dependencies and downloads necessary models.
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def install_python_packages():
    """Install Python packages from requirements.txt"""
    logger.info("Installing Python packages...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        logger.info("✓ Python packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Failed to install Python packages: {e}")
        return False


def install_spacy_models():
    """Install spaCy models for NLP processing"""
    logger.info("Installing spaCy models...")
    
    models = [
        "en_core_web_sm",  # General English model
        "en_core_web_md",  # Medium English model with word vectors
    ]
    
    for model in models:
        try:
            logger.info(f"  Installing {model}...")
            subprocess.check_call([
                sys.executable, "-m", "spacy", "download", model
            ])
            logger.info(f"  ✓ {model} installed")
        except subprocess.CalledProcessError as e:
            logger.error(f"  ✗ Failed to install {model}: {e}")
            return False
    
    logger.info("✓ spaCy models installed successfully")
    return True


def install_scispacy_models():
    """Install SciSpacy models for biomedical NER"""
    logger.info("Installing SciSpacy models...")
    
    models = {
        "en_ner_bc5cdr_md": "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_ner_bc5cdr_md-0.5.3.tar.gz",
        "en_core_sci_sm": "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz",
    }
    
    for model_name, url in models.items():
        try:
            logger.info(f"  Installing {model_name}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", url
            ])
            logger.info(f"  ✓ {model_name} installed")
        except subprocess.CalledProcessError as e:
            logger.error(f"  ✗ Failed to install {model_name}: {e}")
            return False
    
    logger.info("✓ SciSpacy models installed successfully")
    return True


def download_transformer_models():
    """Pre-download transformer models to cache"""
    logger.info("Pre-downloading transformer models (this may take a while)...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        
        models = [
            "allenai/scibert_scivocab_uncased",  # SciBERT for NER
        ]
        
        for model_name in models:
            logger.info(f"  Downloading {model_name}...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForTokenClassification.from_pretrained(model_name)
            logger.info(f"  ✓ {model_name} downloaded")
        
        logger.info("✓ Transformer models downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to download transformer models: {e}")
        return False


def download_sentence_transformers():
    """Pre-download sentence transformer models for topic modeling"""
    logger.info("Pre-downloading sentence transformer models...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        models = [
            "pritamdeka/S-PubMedBert-MS-MARCO",  # Biomedical sentence embeddings
        ]
        
        for model_name in models:
            logger.info(f"  Downloading {model_name}...")
            model = SentenceTransformer(model_name)
            logger.info(f"  ✓ {model_name} downloaded")
        
        logger.info("✓ Sentence transformer models downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to download sentence transformer models: {e}")
        return False


def create_data_directories():
    """Create necessary data directories"""
    logger.info("Creating data directories...")
    
    directories = [
        "data/raw",
        "data/processed",
        "data/intermediate",
        "data/models",
        "data/logs",
        "data/publications",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"  ✓ Created {directory}")
    
    logger.info("✓ Data directories created successfully")
    return True


def verify_env_file():
    """Verify .env file exists"""
    logger.info("Checking for .env file...")
    
    if os.path.exists(".env"):
        logger.info("✓ .env file found")
        return True
    else:
        logger.warning("✗ .env file not found")
        logger.info("  Please copy .env.example to .env and fill in your API keys:")
        logger.info("    cp .env.example .env")
        return False


def verify_docker():
    """Verify Docker is installed and running"""
    logger.info("Checking Docker installation...")
    
    try:
        subprocess.check_output(["docker", "--version"])
        logger.info("✓ Docker is installed")
        
        # Check if Docker is running
        subprocess.check_output(["docker", "ps"])
        logger.info("✓ Docker is running")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("✗ Docker is not installed or not running")
        logger.info("  Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return False


def main():
    """Main setup function"""
    logger.info("=" * 60)
    logger.info("Space Biology Knowledge Graph - Setup Script")
    logger.info("=" * 60)
    
    steps = [
        ("Verifying environment file", verify_env_file),
        ("Checking Docker", verify_docker),
        ("Installing Python packages", install_python_packages),
        ("Installing spaCy models", install_spacy_models),
        ("Installing SciSpacy models", install_scispacy_models),
        ("Downloading transformer models", download_transformer_models),
        ("Downloading sentence transformers", download_sentence_transformers),
        ("Creating data directories", create_data_directories),
    ]
    
    results = []
    for step_name, step_func in steps:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Step: {step_name}")
        logger.info(f"{'=' * 60}")
        
        result = step_func()
        results.append((step_name, result))
    
    # Summary
    logger.info(f"\n{'=' * 60}")
    logger.info("Setup Summary")
    logger.info(f"{'=' * 60}")
    
    for step_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status:10} {step_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        logger.info("\n" + "=" * 60)
        logger.info("✓ Setup completed successfully!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Start the Docker services:")
        logger.info("   docker-compose up -d")
        logger.info("\n2. Run the knowledge graph construction pipeline:")
        logger.info("   python -m backend.knowledge_graph.cli build")
        logger.info("\n3. Access the application:")
        logger.info("   - Frontend: http://localhost:3000")
        logger.info("   - Backend API: http://localhost:8000")
        logger.info("   - Neo4j Browser: http://localhost:7474")
        logger.info("=" * 60)
    else:
        logger.error("\n" + "=" * 60)
        logger.error("✗ Setup completed with errors")
        logger.error("=" * 60)
        logger.error("Please resolve the errors above and run setup again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
