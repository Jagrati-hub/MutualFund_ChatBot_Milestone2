# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Fault Condition** - Category Query Pattern Matching Inconsistency
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate incomplete pattern matching causes non-deterministic results
  - **Scoped PBT Approach**: Test category query variations that should be caught but currently fall through to RAG
  - Test that queries like "segregate by category", "categorize funds", "break down by category", "organize by category" are intercepted by `_handle_category_query()`
  - Test that intercepted queries return deterministic results from `SCOPE_FUNDS_BY_CATEGORY` (21 Equity, 6 Debt, 3 Hybrid, 2 Commodities)
  - Test that the same query returns identical results on repeated calls (no variation in fund distribution)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves pattern matching is incomplete)
  - Document counterexamples found (e.g., "segregate by category" falls through to RAG, returns different results on repeated queries)
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Non-Category Query Behavior
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-category queries (fund-specific questions)
  - Test that queries like "What is the NAV of Groww Liquid Fund?" continue to use RAG retrieval
  - Test that queries about fund details, performance, or features continue to retrieve from vector store
  - Test that PII and advice keyword guardrails continue to be applied
  - Test that response formatting (removing filler phrases) continues to work
  - Write property-based tests capturing observed behavior patterns for non-category queries
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3. Fix for category query pattern matching inconsistency

  - [x] 3.1 Implement the fix in `_handle_category_query()`
    - Expand pattern matching to catch all category-related query variations
    - Add patterns for: "segregate", "categorize", "break down", "organize", "group", "separate", "divide", "split", "classify"
    - Add patterns for: "distribution", "breakdown", "composition", "allocation"
    - Add patterns for: "how are funds", "what categories", "fund categories", "types of funds"
    - Ensure all matched queries route to hardcoded `SCOPE_FUNDS_BY_CATEGORY` data structure
    - Maintain existing fund-specific intent check to preserve RAG behavior for non-category queries
    - _Bug_Condition: Category queries using natural language variations not matched by current patterns fall through to RAG, causing non-deterministic results_
    - _Expected_Behavior: All category-related queries are intercepted and return deterministic results from SCOPE_FUNDS_BY_CATEGORY (21 Equity, 6 Debt, 3 Hybrid, 2 Commodities)_
    - _Preservation: Non-category queries (fund details, NAV, performance) continue using RAG retrieval; guardrails and formatting continue to work_
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4_

  - [x] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Category Query Pattern Matching Consistency
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms all category query variations are intercepted
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed - all patterns matched, deterministic results)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Non-Category Query Behavior
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions - non-category queries still use RAG)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 4. Checkpoint - Ensure all tests pass
  - All 7 tests pass successfully
  - Bug condition exploration tests confirm pattern matching is working correctly
  - Preservation tests confirm no regressions in non-category query behavior
  - All guardrails (PII, advice) continue to work
  - Response formatting continues to work
  - Date appending logic now always appends date (uses current date as fallback)
