# Dog Shelter Application

## Organizational Standards

### Code Quality
- All functions must have docstrings following Google style
- Maximum function length: 50 lines
- Use descriptive variable names (no single letters except loop counters)

### Python Backend
- Use type hints for all function parameters and return values
- Follow PEP 8 strictly
- All database queries must use SQLAlchemy ORM (no raw SQL)
- All routes require corresponding unit tests in `test_*.py`

### Frontend
- Use Svelte components with TypeScript
- All API calls must include error handling
- Use arrow functions consistently
- Accessibility: All interactive elements need aria-labels

### Testing
- Test coverage must exceed 80%
- Mock all external dependencies
- Tests should follow AAA pattern (Arrange, Act, Assert)