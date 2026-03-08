# Bugfix Requirements Document

## Introduction

Users are experiencing inconsistent results when querying for category-wise mutual fund listings. The system should consistently categorize all 32 Groww Mutual Fund schemes across 4 categories (Equity: 21, Debt: 6, Hybrid: 3, Commodities: 2), but currently returns different schemes in different categories on repeated queries. This bug undermines user trust and data integrity, as the same query produces varying results instead of deterministic, consistent categorization.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a user asks for "category wise listing" or similar queries THEN the system returns different schemes appearing in different categories on different queries

1.2 WHEN a user asks for category-wise segregation multiple times THEN the system shows inconsistent results with varying fund distributions across categories

1.3 WHEN a user queries for a specific category (e.g., "list equity funds") THEN the system may return different funds or counts on repeated queries

### Expected Behavior (Correct)

2.1 WHEN a user asks for "category wise listing" or similar queries THEN the system SHALL always return the exact same 32 schemes distributed as: 21 Equity, 6 Debt, 3 Hybrid, 2 Commodities

2.2 WHEN a user asks for category-wise segregation multiple times THEN the system SHALL return identical results every time with consistent fund distributions

2.3 WHEN a user queries for a specific category (e.g., "list equity funds") THEN the system SHALL always return the same funds and count for that category

2.4 WHEN the system processes category queries THEN the system SHALL bypass RAG retrieval and use the hardcoded SCOPE_FUNDS_BY_CATEGORY data structure to ensure 100% consistency

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a user asks non-category questions about specific funds (e.g., "What is the NAV of Groww Liquid Fund?") THEN the system SHALL CONTINUE TO use RAG retrieval for those queries

3.2 WHEN a user asks for fund details, performance, or features THEN the system SHALL CONTINUE TO retrieve information from the vector store

3.3 WHEN the system validates queries for PII or advice keywords THEN the system SHALL CONTINUE TO apply guardrails before processing

3.4 WHEN the system formats answers THEN the system SHALL CONTINUE TO remove filler phrases and format responses appropriately
