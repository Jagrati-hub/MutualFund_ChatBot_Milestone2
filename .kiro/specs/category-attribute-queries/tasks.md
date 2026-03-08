# Implementation Plan: Category-Attribute Queries

## Overview

This implementation adds category-attribute query handling to the RAG engine, enabling users to query specific attributes (NAV, expense ratio, etc.) for all funds in a category. The implementation follows a pattern-based detection approach, leveraging the existing SCOPE_FUNDS_BY_CATEGORY data structure to ensure complete fund coverage.

## Tasks

- [x] 1. Set up category and attribute mapping data structures
  - Create CATEGORY_MAPPING dictionary with category keywords mapped to internal category keys
  - Create ATTRIBUTE_MAPPING dictionary with attribute keywords and their synonyms
  - Add these constants to src/rag_engine.py
  - _Requirements: 1.4, 2.3_

- [ ] 2. Implement helper functions for extraction
  - [x] 2.1 Implement _extract_category() function
    - Parse query to identify category keywords using CATEGORY_MAPPING
    - Return internal category key (e.g., "📈 Equity") or None
    - Handle case-insensitive matching
    - _Requirements: 2.1, 1.4_
  
  - [x] 2.2 Implement _extract_attribute() function
    - Parse query to identify attribute keywords using ATTRIBUTE_MAPPING
    - Return normalized attribute name or None
    - Handle synonyms and variations
    - _Requirements: 2.2, 2.3_

- [ ] 3. Implement core category-attribute query handler
  - [x] 3.1 Create _handle_category_attribute_query() function skeleton
    - Define function signature with query parameter
    - Return Optional[Dict[str, Any]]
    - Add docstring explaining purpose and return structure
    - _Requirements: 1.1_
  
  - [x] 3.2 Implement query pattern detection
    - Normalize query to lowercase
    - Check for patterns: "[attribute] of [category]", "show [attribute] of [category] funds", "[category] [attribute]", "what is the [attribute] for [category] funds"
    - Call _extract_category() and _extract_attribute()
    - Return None if not a category-attribute query
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ]* 3.3 Write property test for query detection
    - **Property 1: Category-Attribute Query Detection**
    - **Validates: Requirements 1.1**
    - Generate queries with valid category-attribute combinations
    - Verify detection returns non-None result
  
  - [ ]* 3.4 Write property tests for extraction patterns
    - **Property 2: Pattern-Based Extraction for "show [attribute] of [category] funds"**
    - **Property 3: Pattern-Based Extraction for "[attribute] of [category]"**
    - **Validates: Requirements 1.2, 1.3**
    - Generate queries following each pattern
    - Verify correct category and attribute extraction

- [ ] 4. Implement fund list retrieval and RAG querying
  - [~] 4.1 Add fund list retrieval logic
    - Get fund list from SCOPE_FUNDS_BY_CATEGORY using extracted category
    - Handle case where category not found in dictionary
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 4.2 Write property test for complete fund list retrieval
    - **Property 4: Complete Fund List Retrieval**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
    - For each valid category, verify retrieved fund list matches SCOPE_FUNDS_BY_CATEGORY
  
  - [~] 4.3 Implement _query_fund_attribute() helper function
    - Construct query: "What is the [attribute] of [fund name]?"
    - Call existing RAG retrieval mechanism
    - Extract attribute value from response
    - Return value or "Not available" if extraction fails
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [~] 4.4 Add loop to query each fund's attribute
    - Iterate through fund list
    - Call _query_fund_attribute() for each fund
    - Collect results with fund name associations
    - Handle individual query failures gracefully
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ]* 4.5 Write property tests for RAG querying
    - **Property 5: RAG Query for Each Fund**
    - **Property 6: Fund-Attribute Association Preservation**
    - **Property 7: Unavailable Attribute Handling**
    - **Validates: Requirements 4.1, 4.2, 4.3**
    - Verify RAG called once per fund
    - Verify fund-attribute associations preserved
    - Test handling of unavailable attributes

- [ ] 5. Implement result formatting
  - [~] 5.1 Create result formatting logic
    - Sort results alphabetically by fund name
    - Format as structured list with fund names and attribute values
    - Include header with category name and attribute name
    - Include total fund count
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [ ]* 5.2 Write property tests for result formatting
    - **Property 8: Complete Results Formatting**
    - **Property 9: Consistent Result Ordering**
    - **Property 10: Response Header Completeness**
    - **Property 11: Fund Count Indication**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
    - Verify all funds appear in formatted output
    - Verify consistent ordering across multiple executions
    - Verify header contains category and attribute
    - Verify fund count matches SCOPE_FUNDS_BY_CATEGORY
  
  - [~] 5.3 Return formatted response with metadata
    - Create response dictionary with keys: blocked, answer, citation_url, last_updated
    - Set blocked=False for successful queries
    - Include Groww AMC citation URL
    - Add timestamp for last_updated
    - _Requirements: 5.1_

- [ ] 6. Implement error handling
  - [~] 6.1 Add invalid category error handling
    - Detect when category extraction returns None
    - Return error message listing valid category names (equity, debt, hybrid, commodities)
    - Use standard response structure
    - _Requirements: 6.1_
  
  - [~] 6.2 Add invalid attribute error handling
    - Detect when attribute extraction returns None
    - Return error message suggesting common attribute names
    - Use standard response structure
    - _Requirements: 6.2_
  
  - [~] 6.3 Add RAG system failure handling
    - Detect when RAG system is unavailable
    - Return error message indicating data source unavailable
    - Handle partial results (some funds succeed, others fail)
    - _Requirements: 6.3_
  
  - [ ]* 6.4 Write property tests for error handling
    - **Property 12: Invalid Category Error Handling**
    - **Property 13: Invalid Attribute Error Handling**
    - **Property 14: RAG Failure Error Handling**
    - **Validates: Requirements 6.1, 6.2, 6.3**
    - Generate invalid categories and verify error messages
    - Generate invalid attributes and verify error messages
    - Simulate RAG failures and verify error handling

- [ ] 7. Integrate with existing answer() function
  - [x] 7.1 Add call to _handle_category_attribute_query() in answer()
    - Insert after _handle_category_query() check
    - Insert before general RAG retrieval
    - Return result if category-attribute query detected
    - _Requirements: 1.1_
  
  - [~] 7.2 Verify integration doesn't break existing functionality
    - Test that category queries still work
    - Test that non-category queries still route to RAG
    - Test that guardrails still function correctly
    - _Requirements: 1.1_

- [~] 8. Checkpoint - Ensure all tests pass
  - Run all property-based tests with minimum 100 iterations
  - Run all unit tests
  - Verify no regressions in existing functionality
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests use hypothesis library with minimum 100 iterations
- Implementation leverages existing SCOPE_FUNDS_BY_CATEGORY data structure
- Pattern-based detection approach consistent with existing _handle_category_query()
- All 14 correctness properties from design document are covered in property tests
