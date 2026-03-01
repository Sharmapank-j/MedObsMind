# Contributing to MedObsMind

Thank you for your interest in contributing to MedObsMind! This document provides guidelines for contributing to the project.

## Code of Conduct

MedObsMind is committed to providing a welcoming and inclusive environment. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title** - Descriptive summary of the issue
- **Steps to reproduce** - Detailed steps to reproduce the behavior
- **Expected behavior** - What you expected to happen
- **Actual behavior** - What actually happened
- **Environment** - OS, Python version, browser, etc.
- **Screenshots** - If applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** - Descriptive summary of the enhancement
- **Use case** - Why is this enhancement needed?
- **Proposed solution** - How would you implement it?
- **Alternatives** - What alternatives have you considered?

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow coding standards** (see below)
3. **Write tests** for new features
4. **Update documentation** as needed
5. **Ensure tests pass** before submitting
6. **Write clear commit messages**

## Development Setup

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload
```

### Android App

```bash
# Ensure Android SDK is installed
./gradlew assembleDebug
./gradlew installDebug
```

### Web Frontend

```bash
# Simple HTTP server for development
python -m http.server 8080
# Visit http://localhost:8080/index.html
```

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small (<50 lines)
- Use meaningful variable names

**Example:**
```python
from typing import Optional

async def calculate_news2_score(
    respiratory_rate: int,
    spo2: int,
    temperature: float,
    systolic_bp: int,
    heart_rate: int,
    consciousness_level: str,
    on_supplemental_oxygen: bool = False
) -> dict:
    """
    Calculate NEWS2 (National Early Warning Score 2).
    
    Args:
        respiratory_rate: Breaths per minute
        spo2: Oxygen saturation percentage
        temperature: Body temperature in Celsius
        systolic_bp: Systolic blood pressure in mmHg
        heart_rate: Heart rate in beats per minute
        consciousness_level: AVPU scale (A, V, P, U)
        on_supplemental_oxygen: Whether patient is on supplemental O2
    
    Returns:
        Dictionary with total_score, risk_level, and component_scores
    """
    # Implementation...
```

### Kotlin/Java (Android)

- Follow [Kotlin style guide](https://kotlinlang.org/docs/coding-conventions.html)
- Use MVVM architecture pattern
- Implement dependency injection where appropriate
- Write unit tests for ViewModels
- Use meaningful resource names

### JavaScript/HTML/CSS (Web)

- Use ES6+ features
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use semantic HTML5
- Follow BEM naming convention for CSS
- Ensure accessibility (WCAG AA compliance)

## Testing

### Python Tests

```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Writing Tests

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_patient():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/patients", json={
            "mrn": "TEST001",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "male"
        })
        assert response.status_code == 201
        assert response.json()["mrn"] == "TEST001"
```

## Medical Safety Guidelines

**Important:** MedObsMind is a medical decision support system. All contributions must prioritize patient safety.

### Critical Rules

1. **No Autonomous Decisions** - AI suggestions must always be advisory, never prescriptive
2. **Human Override** - Clinicians must always be able to override AI recommendations
3. **Explainability** - All AI decisions must show reasoning and evidence
4. **Testing** - Medical algorithms must be thoroughly tested
5. **Validation** - Follow clinical guidelines (e.g., Royal College of Physicians for NEWS2)
6. **Documentation** - Document all clinical reasoning and sources

### Medical Algorithm Development

When implementing medical algorithms:

1. **Cite sources** - Reference clinical guidelines or papers
2. **Follow standards** - Use established scoring systems (NEWS2, MEWS, qSOFA)
3. **Test thoroughly** - Include edge cases and boundary conditions
4. **Peer review** - Have medical professional review clinical logic
5. **Audit trail** - Log all calculations and decisions

## Documentation

### Code Documentation

- Use docstrings for all public functions and classes
- Include parameter types and return types
- Provide usage examples for complex functions
- Update README.md when adding major features

### API Documentation

- FastAPI automatically generates OpenAPI docs at `/docs`
- Include example requests and responses in docstrings
- Document error codes and responses
- Keep API versioned (e.g., `/api/v1/`)

## Git Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features (e.g., `feature/vitals-api`)
- `bugfix/*` - Bug fixes (e.g., `bugfix/news2-calculation`)
- `hotfix/*` - Emergency production fixes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(vitals): add vitals recording API endpoint

- Implement POST /api/v1/vitals
- Add automatic NEWS2 calculation
- Include validation for vital sign ranges

Closes #123
```

## Review Process

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commit messages are clear
- [ ] Changes are focused (single concern)

### Review Criteria

1. **Functionality** - Does it work as intended?
2. **Medical Safety** - Does it follow safety guidelines?
3. **Code Quality** - Is it clean, maintainable, readable?
4. **Tests** - Are there adequate tests?
5. **Documentation** - Is it properly documented?
6. **Performance** - Are there any performance concerns?
7. **Security** - Are there any security issues?

## Community

### Getting Help

- **GitHub Issues** - For bugs and feature requests
- **Discussions** - For questions and general discussion
- **Email** - ethics@medobsmind.com for governance/ethics questions

### Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project website (when launched)

## License

By contributing to MedObsMind, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Questions?

If you have questions about contributing, please:
1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Email the maintainers

Thank you for contributing to MedObsMind and helping improve healthcare through technology! 🏥💙
