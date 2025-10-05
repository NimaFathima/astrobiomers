# Database Schema Design

## Overview

The Space Biology Knowledge Engine uses a multi-database architecture, with each database optimized for its specific use case.

## 1. Neo4j (Knowledge Graph)

### Node Labels and Properties

```cypher
// Complete schema definition

CREATE CONSTRAINT gene_id IF NOT EXISTS FOR (g:Gene) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT protein_id IF NOT EXISTS FOR (p:Protein) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT organism_id IF NOT EXISTS FOR (o:Organism) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT publication_id IF NOT EXISTS FOR (pub:Publication) REQUIRE pub.id IS UNIQUE;
CREATE CONSTRAINT stressor_id IF NOT EXISTS FOR (s:Stressor) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT experiment_id IF NOT EXISTS FOR (e:Experiment) REQUIRE e.id IS UNIQUE;

CREATE INDEX gene_symbol IF NOT EXISTS FOR (g:Gene) ON (g.symbol);
CREATE INDEX protein_name IF NOT EXISTS FOR (p:Protein) ON (p.name);
CREATE INDEX organism_name IF NOT EXISTS FOR (o:Organism) ON (o.scientific_name);
CREATE INDEX publication_pmid IF NOT EXISTS FOR (pub:Publication) ON (pub.pmid);
CREATE INDEX publication_date IF NOT EXISTS FOR (pub:Publication) ON (pub.publication_date);
```

## 2. PostgreSQL (Relational Data)

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    affiliation VARCHAR(255),
    orcid VARCHAR(19),
    role VARCHAR(50) DEFAULT 'researcher',
    reputation_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### Workspaces Table
```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
```

### Workspace Members Table
```sql
CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- owner, editor, viewer
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);
```

### Annotations Table
```sql
CREATE TABLE annotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id VARCHAR(255) NOT NULL, -- Neo4j entity ID
    entity_type VARCHAR(50) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    annotation_type VARCHAR(50) DEFAULT 'note', -- note, correction, question
    confidence_rating INTEGER CHECK (confidence_rating BETWEEN 1 AND 5),
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_annotations_entity ON annotations(entity_id);
CREATE INDEX idx_annotations_user ON annotations(user_id);
CREATE INDEX idx_annotations_created ON annotations(created_at);
```

### Contributions Table
```sql
CREATE TABLE contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    contribution_type VARCHAR(50) NOT NULL, -- entity, relationship, correction
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected
    data JSONB NOT NULL,
    justification TEXT,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contributions_user ON contributions(user_id);
CREATE INDEX idx_contributions_status ON contributions(status);
CREATE INDEX idx_contributions_type ON contributions(contribution_type);
```

### Bookmarks Table
```sql
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL, -- publication, entity, query
    item_id VARCHAR(255) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, item_id)
);

CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);
```

### Search History Table
```sql
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    query_type VARCHAR(50), -- semantic, keyword, graph
    filters JSONB,
    results_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_search_history_user ON search_history(user_id);
CREATE INDEX idx_search_history_created ON search_history(created_at);
```

### Activity Log Table
```sql
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activity_log_user ON activity_log(user_id);
CREATE INDEX idx_activity_log_action ON activity_log(action);
CREATE INDEX idx_activity_log_created ON activity_log(created_at);
```

### Discussions Table
```sql
CREATE TABLE discussions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    parent_id UUID REFERENCES discussions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_discussions_entity ON discussions(entity_id);
CREATE INDEX idx_discussions_parent ON discussions(parent_id);
CREATE INDEX idx_discussions_user ON discussions(user_id);
```

### API Keys Table
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    permissions JSONB,
    rate_limit INTEGER DEFAULT 100, -- requests per minute
    last_used TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
```

## 3. Vector Database Schema (Pinecone/Weaviate)

### Weaviate Schema Example

```python
# Weaviate class definition for publications
publication_class = {
    "class": "Publication",
    "description": "Scientific publications in space biology",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {
            "model": "ada-002",
            "type": "text"
        }
    },
    "properties": [
        {
            "name": "pmid",
            "dataType": ["string"],
            "description": "PubMed ID",
            "indexInverted": True
        },
        {
            "name": "title",
            "dataType": ["text"],
            "description": "Publication title",
            "indexInverted": True
        },
        {
            "name": "abstract",
            "dataType": ["text"],
            "description": "Publication abstract",
            "indexInverted": True
        },
        {
            "name": "authors",
            "dataType": ["string[]"],
            "description": "List of authors"
        },
        {
            "name": "publication_date",
            "dataType": ["date"],
            "description": "Date of publication"
        },
        {
            "name": "journal",
            "dataType": ["string"],
            "description": "Journal name"
        },
        {
            "name": "entities",
            "dataType": ["string[]"],
            "description": "Extracted entity IDs"
        },
        {
            "name": "mesh_terms",
            "dataType": ["string[]"],
            "description": "MeSH terms"
        }
    ]
}

# Entity class for semantic search
entity_class = {
    "class": "Entity",
    "description": "Biological entities (genes, proteins, etc.)",
    "vectorizer": "text2vec-openai",
    "properties": [
        {
            "name": "entity_id",
            "dataType": ["string"],
            "description": "Unique entity identifier"
        },
        {
            "name": "entity_type",
            "dataType": ["string"],
            "description": "Type of entity"
        },
        {
            "name": "name",
            "dataType": ["text"],
            "description": "Entity name"
        },
        {
            "name": "description",
            "dataType": ["text"],
            "description": "Entity description"
        },
        {
            "name": "aliases",
            "dataType": ["string[]"],
            "description": "Alternative names"
        },
        {
            "name": "context",
            "dataType": ["text"],
            "description": "Aggregated context from publications"
        }
    ]
}
```

## 4. Elasticsearch Mappings

```json
{
  "mappings": {
    "properties": {
      "pmid": {
        "type": "keyword"
      },
      "doi": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "english",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "abstract": {
        "type": "text",
        "analyzer": "english"
      },
      "full_text": {
        "type": "text",
        "analyzer": "english"
      },
      "authors": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "journal": {
        "type": "keyword"
      },
      "publication_date": {
        "type": "date"
      },
      "keywords": {
        "type": "keyword"
      },
      "mesh_terms": {
        "type": "keyword"
      },
      "extracted_entities": {
        "type": "nested",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "type": {
            "type": "keyword"
          },
          "name": {
            "type": "text"
          }
        }
      },
      "citation_count": {
        "type": "integer"
      },
      "created_at": {
        "type": "date"
      }
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "biomedical_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "stop",
            "snowball",
            "biomedical_synonyms"
          ]
        }
      },
      "filter": {
        "biomedical_synonyms": {
          "type": "synonym",
          "synonyms": [
            "microgravity, weightlessness, zero-g",
            "ISS, International Space Station",
            "radiation, cosmic rays"
          ]
        }
      }
    }
  }
}
```

## 5. Redis Cache Structure

```
# User sessions
session:{user_id} -> JSON {
    user_id, email, role, permissions, expires_at
}
TTL: 24 hours

# Query results cache
query:{query_hash} -> JSON {
    results, count, timestamp
}
TTL: 1 hour

# Entity cache
entity:{entity_id} -> JSON {
    entity data from Neo4j
}
TTL: 6 hours

# Rate limiting
ratelimit:{user_id}:{endpoint} -> counter
TTL: 1 minute

# Leaderboard (sorted sets)
leaderboard:contributions -> ZADD {user_id} {score}
leaderboard:reputation -> ZADD {user_id} {score}
```

## 6. Data Migration Scripts

### Initial Neo4j Data Load
```python
# scripts/migrate_to_neo4j.py

from neo4j import GraphDatabase
import json

class Neo4jMigration:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def create_constraints_and_indexes(self):
        """Create all constraints and indexes."""
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT gene_id IF NOT EXISTS FOR (g:Gene) REQUIRE g.id IS UNIQUE",
                "CREATE CONSTRAINT protein_id IF NOT EXISTS FOR (p:Protein) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT organism_id IF NOT EXISTS FOR (o:Organism) REQUIRE o.id IS UNIQUE",
                "CREATE CONSTRAINT publication_id IF NOT EXISTS FOR (pub:Publication) REQUIRE pub.id IS UNIQUE",
            ]
            
            indexes = [
                "CREATE INDEX gene_symbol IF NOT EXISTS FOR (g:Gene) ON (g.symbol)",
                "CREATE INDEX protein_name IF NOT EXISTS FOR (p:Protein) ON (p.name)",
            ]
            
            for constraint in constraints:
                session.run(constraint)
            
            for index in indexes:
                session.run(index)
    
    def load_ontology_data(self, ontology_file):
        """Load GO terms or other ontology data."""
        with open(ontology_file, 'r') as f:
            terms = json.load(f)
        
        with self.driver.session() as session:
            for term in terms:
                session.run("""
                    MERGE (t:BiologicalProcess {id: $id})
                    SET t.name = $name,
                        t.definition = $definition,
                        t.synonyms = $synonyms
                """, **term)
    
    def close(self):
        self.driver.close()
```

---

This schema provides a complete foundation for all data storage needs of the Space Biology Knowledge Engine.
