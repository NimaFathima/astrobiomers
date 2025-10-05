# Contributing to ASTROBIOMERS

Thank you for your interest in contributing to the Space Biology Knowledge Engine! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## How to Contribute

### 1. Report Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, etc.)
- Screenshots if applicable

### 2. Suggest Features

We welcome feature suggestions! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Proposed implementation (if you have ideas)
- Mockups or examples (if applicable)

### 3. Submit Code

#### Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/ASTROBIOMERS.git
cd ASTROBIOMERS

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/ASTROBIOMERS.git
```

#### Create a Branch
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bug fix branch
git checkout -b fix/bug-description
```

#### Make Changes

1. Write clear, commented code
2. Follow the code style guidelines (below)
3. Add tests for new functionality
4. Update documentation as needed

#### Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

#### Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots/demos if applicable
- Checklist of completed items

## Code Style Guidelines

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions and classes

```python
def extract_entities(text: str, confidence_threshold: float = 0.8) -> List[Dict]:
    """
    Extract named entities from text.
    
    Args:
        text: Input text to process
        confidence_threshold: Minimum confidence score for entities
        
    Returns:
        List of entity dictionaries with type, text, and confidence
    """
    # Implementation here
    pass
```

**Formatting:**
```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

### JavaScript/React (Frontend)

- Use ES6+ features
- Prefer functional components with hooks
- Use meaningful variable names
- Add PropTypes or TypeScript types
- Maximum line length: 100 characters

```javascript
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * GraphViewer component for visualizing knowledge graph
 */
function GraphViewer({ entityId, onNodeClick }) {
  const [graphData, setGraphData] = useState(null);
  
  useEffect(() => {
    // Load graph data
  }, [entityId]);
  
  return (
    <div className="graph-viewer">
      {/* Implementation */}
    </div>
  );
}

GraphViewer.propTypes = {
  entityId: PropTypes.string.isRequired,
  onNodeClick: PropTypes.func
};

export default GraphViewer;
```

**Formatting:**
```bash
# Format code
npm run format

# Lint
npm run lint
```

### Git Commit Messages

Use clear, descriptive commit messages:

```
feat: add graph visualization component

- Implement Cytoscape.js integration
- Add zoom and pan controls
- Support filtering by entity type
- Add node click handlers

Closes #123
```

## Testing Guidelines

### Backend Tests

```python
# tests/test_ner.py
import pytest
from knowledge_graph.ner import BiomedicalNER

def test_extract_genes():
    ner = BiomedicalNER()
    text = "MYOD1 and MYF5 are muscle-specific genes."
    
    entities = ner.extract_entities(text)
    
    assert len(entities) >= 2
    assert any(e['text'] == 'MYOD1' for e in entities)
    assert any(e['text'] == 'MYF5' for e in entities)
```

Run tests:
```bash
cd backend
pytest
pytest --cov=. --cov-report=html
```

### Frontend Tests

```javascript
// components/__tests__/GraphViewer.test.jsx
import { render, screen } from '@testing-library/react';
import GraphViewer from '../GraphViewer';

test('renders graph viewer', () => {
  render(<GraphViewer entityId="test-id" />);
  expect(screen.getByTestId('graph-container')).toBeInTheDocument();
});
```

Run tests:
```bash
cd frontend
npm test
npm test -- --coverage
```

## Documentation

- Update README.md if adding major features
- Add docstrings/JSDoc comments to all public functions
- Update API documentation for new endpoints
- Add examples for new features

## Review Process

1. **Automated Checks**: CI/CD will run tests and linting
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, your PR will be merged

## Areas Needing Contribution

### High Priority
- [ ] Complete NER pipeline with custom space biology model
- [ ] Implement graph visualization with Cytoscape.js
- [ ] Build RAG pipeline for AI assistant
- [ ] Add user authentication and authorization

### Medium Priority
- [ ] Create additional data source integrators (NASA GeneLab, ArXiv)
- [ ] Implement advanced graph analytics
- [ ] Add export functionality (CSV, JSON, PDF)
- [ ] Improve UI/UX with user testing feedback

### Documentation
- [ ] API usage examples
- [ ] Video tutorials
- [ ] Architecture decision records
- [ ] Performance optimization guide

## Questions?

- Create an issue for questions
- Join our discussions
- Reach out to maintainers

Thank you for contributing to ASTROBIOMERS! 🚀
