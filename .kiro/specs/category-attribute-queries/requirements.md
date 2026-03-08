# Requirements Document

## Introduction

This feature enables users to query specific fund attributes (NAV, expense ratio, exit load, returns, etc.) for an entire category of mutual funds and receive comprehensive results for ALL funds within that category. Currently, category-wide attribute queries return incomplete results or inconsistent RAG responses. This feature will ensure complete, consistent results by systematically querying each fund in the requested category.

## Glossary

- **Query_Handler**: The system component that processes user queries for fund attributes
- **Category**: A classification of mutual funds (equity, debt, hybrid, commodities)
- **Attribute**: A specific fund characteristic (NAV, expense ratio, exit load, returns, etc.)
- **RAG**: Retrieval-Augmented Generation system that provides fund data
- **Fund**: A mutual fund investment product within a category

## Requirements

### Requirement 1: Detect Category-Attribute Queries

**User Story:** As a user, I want the system to recognize when I'm asking for an attribute across an entire category, so that I receive complete results for all funds in that category.

#### Acceptance Criteria

1. WHEN a user query contains both a category name and an attribute name, THE Query_Handler SHALL identify the query as a category-attribute query
2. WHEN a user query uses natural language patterns like "show [attribute] of [category] funds", THE Query_Handler SHALL extract the category and attribute
3. WHEN a user query uses patterns like "[attribute] of [category]", THE Query_Handler SHALL extract the category and attribute
4. THE Query_Handler SHALL recognize category names: equity, debt, hybrid, and commodities

### Requirement 2: Extract Query Components

**User Story:** As a user, I want the system to correctly identify which attribute and category I'm asking about, so that I get the right information.

#### Acceptance Criteria

1. WHEN a category-attribute query is detected, THE Query_Handler SHALL extract the category name
2. WHEN a category-attribute query is detected, THE Query_Handler SHALL extract the attribute name
3. THE Query_Handler SHALL recognize common attribute names including NAV, expense ratio, exit load, returns, AUM, minimum investment, and fund manager
4. WHEN the attribute or category cannot be identified, THE Query_Handler SHALL request clarification from the user

### Requirement 3: Retrieve Complete Category Fund List

**User Story:** As a user, I want the system to know all funds in a category, so that no funds are missed in the results.

#### Acceptance Criteria

1. WHEN a category is identified, THE Query_Handler SHALL retrieve the complete list of funds in that category
2. THE Query_Handler SHALL retrieve all 21 equity funds when the equity category is queried
3. THE Query_Handler SHALL retrieve all 6 debt funds when the debt category is queried
4. THE Query_Handler SHALL retrieve all 3 hybrid funds when the hybrid category is queried
5. THE Query_Handler SHALL retrieve all 2 commodities funds when the commodities category is queried

### Requirement 4: Query Attribute for Each Fund

**User Story:** As a user, I want the system to fetch the requested attribute for every fund in the category, so that I receive complete information.

#### Acceptance Criteria

1. WHEN the fund list is retrieved, THE Query_Handler SHALL query the RAG system for the specified attribute for each fund in the list
2. THE Query_Handler SHALL maintain the fund name association with each attribute value
3. WHEN a fund's attribute value is unavailable, THE Query_Handler SHALL record the fund with a "not available" indicator
4. THE Query_Handler SHALL complete all attribute queries before formatting the response

### Requirement 5: Format and Return Results

**User Story:** As a user, I want to see the attribute values for all funds in a clear, organized format, so that I can easily compare them.

#### Acceptance Criteria

1. WHEN all attribute values are retrieved, THE Query_Handler SHALL format the results as a list showing each fund name with its attribute value
2. THE Query_Handler SHALL organize results by fund name in a consistent order
3. THE Query_Handler SHALL include the category name and attribute name in the response header
4. WHEN all funds in a category are included in the results, THE Query_Handler SHALL indicate the total count of funds

### Requirement 6: Handle Query Errors

**User Story:** As a user, I want to receive helpful error messages when something goes wrong, so that I can adjust my query.

#### Acceptance Criteria

1. IF the category name is not recognized, THEN THE Query_Handler SHALL return an error message listing valid category names
2. IF the attribute name is not recognized, THEN THE Query_Handler SHALL return an error message suggesting common attribute names
3. IF the RAG system fails to respond, THEN THE Query_Handler SHALL return an error message indicating the data source is unavailable
4. WHEN a query error occurs, THE Query_Handler SHALL preserve the user's original query context for retry
