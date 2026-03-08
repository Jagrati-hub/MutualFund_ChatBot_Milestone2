# Design Document: Category-Attribute Queries

## Overview

This feature extends the existing query handling system to support category-wide attribute queries like "NAV of equity funds" or "expense ratio of debt funds". The design leverages the existing `SCOPE_FUNDS_BY_CATEGORY` data structure to retrieve complete fund lists, then systematically queries the RAG system for each fund's attribute value, ensuring comprehensive and consistent results.

The implementation adds a new query detection and handling path in the RAG engine that:
1. Detects category-attribute query patterns using natural language processing
2. Extracts the category and attribute from the user query
3. Retrieves the complete fund list for that category from `SCOPE_FUNDS_BY_CATEGORY`
4. Queries the RAG system for each fund's attribute value
5. Formats and returns results showing all funds with their attribute values

This approach ensures users receive complete information for all funds in a category, addressing the current limitation where category-wide attribute queries return incomplete or inconsistent results.

## Architecture

### High-Level Flow

```
User Query
    ↓
validate_query() [existing guardrails]
    ↓
_handle_category_attribute_query() [NEW]
    ↓
├─ Detect category-attribute pattern
├─ Extract category & attribute
├─ Get fund list from SCOPE_FUNDS_BY_CATEGORY
├─ For each fund: query RAG for attribute
└─ Format & return results
    ↓
Return to user
```

### Integration Points

1. **RAG Engine (`src/rag_engine.py`)**: Add new `_handle_category_attribute_query()` function that intercepts category-attribute queries before RAG retrieval, similar to existing `_handle_category_query()`

2. **Shared Data (`src/shared.py`)**: Use existing `SCOPE_FUNDS_BY_CATEGORY` dictionary to get complete fund lists

3. **Query Processing Flow**: Insert new handler in `answer()` function after `_handle_category_query()` but before general RAG retrieval

### Design Decisions

**Decision 1: Pattern-Based Detection vs ML Classification**
- **Choice**: Use pattern-based detection with keyword matching
- **Rationale**: Consistent with existing `_handle_category_query()` approach; simpler, more maintainable, and sufficient for well-defined query patterns
- **Trade-off**: Less flexible than ML but more predictable and debuggable

**Decision 2: Sequential RAG Queries vs Batch Processing**
- **Choice**: Sequential queries for each fund's attribute
- **Rationale**: Existing RAG system doesn't support batch queries; sequential approach is simpler and more reliable
- **Trade-off**: Slower for large categories but ensures accurate per-fund results

**Decision 3: Hardcoded Attribute List vs Dynamic Detection**
- **Choice**: Hardcoded list of recognized attributes (NAV, expense ratio, exit load, returns, AUM, minimum investment, fund manager)
- **Rationale**: Provides clear user feedback when attribute is not recognized; prevents ambiguous queries
- **Trade-off**: Requires updates when new attributes are added, but improves user experience

## Components and Interfaces

### New Component: Category-Attribute Query Handler

**Function**: `_handle_category_attribute_query(query: str) -> Optional[Dict[str, Any]]`

**Location**: `src/rag_engine.py`

**Purpose**: Detect and process category-attribute queries by extracting components, retrieving fund lists, and querying RAG for each fund's attribute value.

**Interface**:
```python
def _handle_category_attribute_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Detects and handles category-attribute queries (e.g., "NAV of equity funds").
    
    Args:
        query: User's natural language query
        
    Returns:
        Dict with keys: blocked, answer, citation_url, last_updated
        None if query is not a category-attribute query
    """
```

**Algorithm**:
1. Normalize query to lowercase
2. Check for category-attribute patterns:
   - "[attribute] of [category]"
   - "show [attribute] of [category] funds"
   - "[category] [attribute]"
   - "what is the [attribute] for [category] funds"
3. Extract category using keyword mapping (equity, debt, hybrid, commodities)
4. Extract attribute using keyword mapping (NAV, expense ratio, exit load, returns, AUM, minimum investment, fund manager)
5. If both extracted successfully:
   - Get fund list from `SCOPE_FUNDS_BY_CATEGORY[category]`
   - For each fund, construct query: "What is the [attribute] of [fund name]?"
   - Call existing RAG retrieval for each fund
   - Collect results with fund name associations
6. Format results as structured list
7. Return formatted response with metadata

### Modified Component: Main Query Handler

**Function**: `answer(query: str, config: Optional[RAGConfig] = None) -> Dict[str, Any]`

**Location**: `src/rag_engine.py`

**Modification**: Add call to `_handle_category_attribute_query()` after `_handle_category_query()` check

**Updated Flow**:
```python
def answer(query: str, config: Optional[RAGConfig] = None) -> Dict[str, Any]:
    # ... existing validation ...
    
    # Intercept category listing queries
    intercepted = _handle_category_query(query)
    if intercepted:
        return intercepted
    
    # NEW: Intercept category-attribute queries
    category_attr_result = _handle_category_attribute_query(query)
    if category_attr_result:
        return category_attr_result
    
    # ... existing RAG retrieval ...
```

### Helper Functions

**Function**: `_extract_category(query: str) -> Optional[str]`
- Extracts category name from query using keyword mapping
- Returns internal category key (e.g., "📈 Equity") or None

**Function**: `_extract_attribute(query: str) -> Optional[str]`
- Extracts attribute name from query using keyword mapping
- Returns normalized attribute name or None

**Function**: `_query_fund_attribute(fund_name: str, attribute: str) -> str`
- Constructs specific query for a fund's attribute
- Calls existing RAG retrieval
- Returns attribute value or "Not available"

## Data Models

### Category Mapping

```python
CATEGORY_MAPPING = {
    "equity": "📈 Equity",
    "debt": "🏦 Debt",
    "liquid": "🏦 Debt",
    "hybrid": "⚖️ Hybrid",
    "multi asset": "⚖️ Hybrid",
    "commodity": "🪙 Commodities",
    "commodities": "🪙 Commodities",
    "gold": "🪙 Commodities",
    "silver": "🪙 Commodities",
}
```

### Attribute Mapping

```python
ATTRIBUTE_MAPPING = {
    "nav": ["nav", "net asset value", "current nav", "latest nav"],
    "expense_ratio": ["expense ratio", "expense", "cost", "fee", "charges"],
    "exit_load": ["exit load", "exit fee", "redemption charge", "withdrawal fee"],
    "returns": ["returns", "return", "performance", "gain", "growth"],
    "aum": ["aum", "assets under management", "fund size", "corpus"],
    "minimum_investment": ["minimum investment", "minimum amount", "min investment", "minimum sip"],
    "fund_manager": ["fund manager", "manager", "who manages", "managed by"],
}
```

### Query Result Structure

```python
{
    "blocked": False,
    "answer": str,  # Formatted list of funds with attribute values
    "citation_url": str,  # Groww AMC link
    "last_updated": str  # Timestamp of data
}
```

### Fund Attribute Result

```python
{
    "fund_name": str,
    "attribute_value": str,  # Extracted from RAG response or "Not available"
    "raw_response": str  # Full RAG response for debugging
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing the acceptance criteria, several redundancies were identified:
- Requirements 2.1 and 2.2 are subsumed by 1.2 and 1.3, which already test extraction of both category and attribute
- Requirements 3.2-3.5 can be combined into a single property that validates fund counts for all categories
- Requirement 2.4 overlaps with 6.1 and 6.2, which provide more specific error handling tests

The following properties represent the unique, non-redundant validation requirements:

### Property 1: Category-Attribute Query Detection

*For any* user query containing both a valid category keyword (equity, debt, hybrid, commodities) and a valid attribute keyword (NAV, expense ratio, exit load, returns, AUM, minimum investment, fund manager), the Query_Handler should identify it as a category-attribute query.

**Validates: Requirements 1.1**

### Property 2: Pattern-Based Extraction for "show [attribute] of [category] funds"

*For any* query following the pattern "show [attribute] of [category] funds" with valid category and attribute values, the Query_Handler should correctly extract both the category name and the attribute name.

**Validates: Requirements 1.2**

### Property 3: Pattern-Based Extraction for "[attribute] of [category]"

*For any* query following the pattern "[attribute] of [category]" with valid category and attribute values, the Query_Handler should correctly extract both the category name and the attribute name.

**Validates: Requirements 1.3**

### Property 4: Complete Fund List Retrieval

*For any* valid category, when the Query_Handler retrieves the fund list, it should return exactly the same funds and count as defined in SCOPE_FUNDS_BY_CATEGORY for that category.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 5: RAG Query for Each Fund

*For any* fund list and attribute, the Query_Handler should invoke the RAG system exactly once for each fund in the list to retrieve the attribute value.

**Validates: Requirements 4.1**

### Property 6: Fund-Attribute Association Preservation

*For any* fund and its retrieved attribute value, the formatted results should contain both the fund name and its corresponding attribute value in association.

**Validates: Requirements 4.2**

### Property 7: Unavailable Attribute Handling

*For any* fund where the RAG system fails to return an attribute value, the results should include that fund with a "not available" or equivalent indicator.

**Validates: Requirements 4.3**

### Property 8: Complete Results Formatting

*For any* set of fund-attribute pairs retrieved, the formatted response should include all fund names with their corresponding attribute values.

**Validates: Requirements 5.1**

### Property 9: Consistent Result Ordering

*For any* category-attribute query, when executed multiple times with the same inputs, the results should appear in the same order (alphabetically by fund name).

**Validates: Requirements 5.2**

### Property 10: Response Header Completeness

*For any* category-attribute query, the formatted response should include both the category name and the attribute name in the header section.

**Validates: Requirements 5.3**

### Property 11: Fund Count Indication

*For any* category-attribute query, the formatted response should indicate the total count of funds, which should match the number of funds in that category from SCOPE_FUNDS_BY_CATEGORY.

**Validates: Requirements 5.4**

### Property 12: Invalid Category Error Handling

*For any* query with an unrecognized category name, the Query_Handler should return an error message that lists all valid category names (equity, debt, hybrid, commodities).

**Validates: Requirements 6.1**

### Property 13: Invalid Attribute Error Handling

*For any* query with an unrecognized attribute name, the Query_Handler should return an error message that suggests common attribute names.

**Validates: Requirements 6.2**

### Property 14: RAG Failure Error Handling

*For any* query where the RAG system fails to respond, the Query_Handler should return an error message indicating the data source is unavailable.

**Validates: Requirements 6.3**

## Error Handling

### Error Categories

1. **Query Parsing Errors**
   - Invalid or unrecognized category name
   - Invalid or unrecognized attribute name
   - Ambiguous query that matches multiple patterns
   - Response: Return error message with helpful suggestions

2. **Data Retrieval Errors**
   - RAG system unavailable or timeout
   - Individual fund attribute query failure
   - Response: Mark specific funds as "not available" or return system error

3. **Validation Errors**
   - Query blocked by existing guardrails
   - Response: Return blocked status with reason

### Error Response Format

All errors maintain the standard response structure:
```python
{
    "blocked": bool,  # True for validation errors, False for other errors
    "answer": str,    # Error message with helpful context
    "citation_url": str,  # Groww AMC link
    "last_updated": None  # No timestamp for errors
}
```

### Error Messages

**Invalid Category**:
```
I couldn't identify the fund category in your query. Please specify one of these categories:
- Equity
- Debt
- Hybrid
- Commodities

Example: "Show NAV of equity funds"
```

**Invalid Attribute**:
```
I couldn't identify which fund attribute you're asking about. Common attributes include:
- NAV (Net Asset Value)
- Expense Ratio
- Exit Load
- Returns
- AUM (Assets Under Management)
- Minimum Investment
- Fund Manager

Example: "What is the expense ratio of debt funds?"
```

**RAG System Unavailable**:
```
⚠️ Unable to retrieve fund data at this time. The data source is temporarily unavailable. Please try again in a few moments.
```

**Partial Results**:
When some funds return data but others fail:
```
Here are the [attribute] values for [category] funds (showing [X] of [Y] funds):

[List of successful results]

Note: Data unavailable for [N] funds: [fund names]
```

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of each query pattern
- Edge cases (empty results, single fund categories)
- Error conditions (invalid inputs, RAG failures)
- Integration with existing components

**Property-Based Tests** focus on:
- Universal properties across all valid inputs
- Pattern detection across many query variations
- Extraction correctness for all category-attribute combinations
- Result completeness and consistency

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with reference to design document property
- Tag format: `# Feature: category-attribute-queries, Property {number}: {property_text}`

**Test Generators**:
```python
# Generate valid categories
@st.composite
def valid_category(draw):
    return draw(st.sampled_from(["equity", "debt", "hybrid", "commodities"]))

# Generate valid attributes
@st.composite
def valid_attribute(draw):
    return draw(st.sampled_from([
        "nav", "expense ratio", "exit load", "returns", 
        "aum", "minimum investment", "fund manager"
    ]))

# Generate category-attribute queries
@st.composite
def category_attribute_query(draw):
    category = draw(valid_category())
    attribute = draw(valid_attribute())
    pattern = draw(st.sampled_from([
        f"{attribute} of {category}",
        f"show {attribute} of {category} funds",
        f"what is the {attribute} for {category} funds",
        f"{category} {attribute}"
    ]))
    return pattern, category, attribute
```

### Unit Test Coverage

1. **Query Detection Tests**
   - Test each specific query pattern with known inputs
   - Test boundary cases (single word queries, very long queries)
   - Test queries that should NOT be detected as category-attribute queries

2. **Extraction Tests**
   - Test extraction with each category name
   - Test extraction with each attribute name
   - Test extraction with synonyms and variations

3. **Integration Tests**
   - Test full flow from query to formatted response
   - Test with mocked RAG responses
   - Test error handling paths

4. **Regression Tests**
   - Ensure existing category query handling still works
   - Ensure non-category queries still route to RAG
   - Ensure guardrails still function correctly

### Property-Based Test Coverage

Each correctness property maps to one property-based test:

1. **Property 1**: Generate queries with random valid category-attribute combinations, verify detection
2. **Property 2**: Generate queries following "show [attr] of [cat] funds" pattern, verify extraction
3. **Property 3**: Generate queries following "[attr] of [cat]" pattern, verify extraction
4. **Property 4**: For each category, verify retrieved fund list matches SCOPE_FUNDS_BY_CATEGORY
5. **Property 5**: Generate random fund lists, verify RAG called once per fund
6. **Property 6**: Generate random fund-attribute pairs, verify association in results
7. **Property 7**: Simulate RAG failures, verify "not available" indicators
8. **Property 8**: Generate random result sets, verify all funds appear in formatted output
9. **Property 9**: Execute same query multiple times, verify consistent ordering
10. **Property 10**: Generate random queries, verify header contains category and attribute
11. **Property 11**: Generate random queries, verify count matches SCOPE_FUNDS_BY_CATEGORY
12. **Property 12**: Generate invalid categories, verify error message lists valid categories
13. **Property 13**: Generate invalid attributes, verify error message suggests valid attributes
14. **Property 14**: Simulate RAG failures, verify appropriate error message

### Test Execution

Run property-based tests with:
```bash
pytest test_category_attribute_queries.py -v --hypothesis-show-statistics
```

Each property test should run minimum 100 iterations to ensure comprehensive input coverage.
