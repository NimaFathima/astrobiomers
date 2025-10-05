"""
Check pipeline output files
"""
import json
import os

def check_pipeline_output():
    output_dir = "../data/pipeline_output"
    
    files = {
        "raw_papers.json": "Raw papers from PubMed",
        "preprocessed_papers.json": "Preprocessed text",
        "extracted_entities.json": "Extracted entities (NER)",
        "pipeline_results.json": "Final pipeline results"
    }
    
    print("=" * 60)
    print("PIPELINE OUTPUT INSPECTION")
    print("=" * 60)
    
    for filename, description in files.items():
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    print(f"\n✅ {filename}")
                    print(f"   {description}")
                    print(f"   Records: {len(data)}")
                    if data:
                        print(f"   Sample keys: {list(data[0].keys())}")
                elif isinstance(data, dict):
                    print(f"\n✅ {filename}")
                    print(f"   {description}")
                    print(f"   Records: {len(data)}")
                    if data:
                        first_key = list(data.keys())[0]
                        print(f"   Sample keys: {list(data[first_key].keys())}")
            except Exception as e:
                print(f"\n⚠️  {filename}: Error loading - {e}")
        else:
            print(f"\n❌ {filename}: Not found")
    
    # Check extracted entities specifically
    print("\n" + "=" * 60)
    print("ENTITY EXTRACTION DETAILS")
    print("=" * 60)
    
    entities_file = os.path.join(output_dir, "extracted_entities.json")
    if os.path.exists(entities_file):
        with open(entities_file, 'r', encoding='utf-8') as f:
            entities_data = json.load(f)
        
        if entities_data:
            # Get first paper
            first_paper = list(entities_data.values())[0]
            
            print(f"\nSample paper entity types:")
            for entity_type in first_paper.keys():
                count = len(first_paper[entity_type])
                print(f"  {entity_type}: {count} entities")
                if count > 0 and count <= 5:
                    print(f"    Examples: {first_paper[entity_type]}")

if __name__ == "__main__":
    check_pipeline_output()
