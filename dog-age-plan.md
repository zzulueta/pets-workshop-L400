## Implementation Plan: Dog Human Age Endpoint

### Phase 1: Backend Implementation

#### 1.1 Create the API Endpoint
**File**: `server/app.py`

- Add new route `GET /api/dogs/<int:id>/human-age`
- Query dog by ID from database
- Calculate human age using the formula:
  - First 2 years: 10.5 human years each
  - Years after 2: 4 human years each
- Return JSON with dog_name, dog_age, and human_age
- Handle 404 for non-existent dogs
- Follow type hints requirement from `copilot-instructions.md`

#### 1.2 Add Unit Tests
**File**: `server/test_app.py`

Create tests following AAA pattern:
- `test_get_dog_human_age_young_dog` - Test human age calculation for dog 1 year old (boundary)
- `test_get_dog_human_age_exactly_two_years` - Test dog exactly 2 years (boundary)
- `test_get_dog_human_age_three_years` - Test dog just over boundary (3 years)
- `test_get_dog_human_age_older_dog` - Test dog older than 2 years (5 years)
- `test_get_dog_human_age_zero_years` - Test newborn dog (edge case: 0 years)
- `test_get_dog_human_age_very_old_dog` - Test very old dog (edge case: 20 years)
- `test_get_dog_human_age_not_found` - Test 404 error when dog is not found
- `test_get_dog_human_age_zero_id` - Test behavior with zero dog ID (edge case)
- `test_get_dog_human_age_large_id` - Test with very large dog ID (boundary test)
- `test_get_dog_human_age_response_structure` - Test response has correct keys and types
- Mock all database calls as per instructions

### Phase 2: Frontend Implementation

#### 2.1 Update Dog Details Component
**File**: `client/src/components/DogDetails.svelte`

- Add `human_age` field to Dog interface
- Create async function to fetch human age data
- Display human age in the dog details card
- Add error handling for API calls
- Use arrow functions (per `copilot-instructions.md`)
- Add aria-labels for accessibility

#### 2.2 UI Design
- Add human age display in the existing grid layout
- Use slate color theme to match existing design
- Add transition effects for consistency
- Include icon or badge to highlight the human age feature

### Phase 3: Testing

#### 3.1 Backend Tests
**File**: `server/test_app.py`
- Run with `python -m unittest`
- Ensure >80% coverage requirement
- Mock all database dependencies

#### 3.2 End-to-End Tests
**File**: `client/e2e-tests/dog-details.spec.ts`
- Add test for human age display
- Test error handling when endpoint fails
- Verify correct calculation display
- Run with `npm run test:e2e`

### Phase 4: Validation

- Test the endpoint manually at `http://localhost:5100/api/dogs/<id>/human-age`
- Verify frontend display at `http://localhost:4321/dog/<id>`
- Run all tests: `python -m unittest` and `npm run test:e2e`
- Check test coverage meets 80% threshold

### Implementation Order

1. Backend endpoint + unit tests (ensure tests pass first)
2. Frontend component updates
3. Frontend e2e tests
4. Manual validation
5. Final testing and coverage check

### Key Requirements from Instructions

From `copilot-instructions.md`:
- ✅ Type hints for all function parameters and return values
- ✅ Mock all database calls in tests
- ✅ Use arrow functions in TypeScript
- ✅ Add aria-labels for accessibility
- ✅ 80%+ test coverage
- ✅ AAA pattern (Arrange, Act, Assert)
- ✅ Google-style docstrings

This plan ensures all organizational standards are met while implementing a complete, tested feature across the full stack.
