# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2024-11-09

### BREAKING CHANGES
- **Migrated from Databases to TablesDB service** - Appwrite has deprecated the Databases service in favor of TablesDB
- All database operations now use the new TablesDB API:
  - `collection_id` → `table_id`
  - `document_id` → `row_id`
  - `create_document()` → `create_row()`
  - `list_documents()` → `list_rows()`
  - `get_document()` → `get_row()`
  - `update_document()` → `update_row()`
  - `delete_document()` → `delete_row()`
  - `create_collection()` → `create_table()`
  - `list_collections()` → `list_tables()`
  - `document_security` → `row_security`
  - `attributes` → `columns` (in index creation)

### Migration Guide
The DatabaseManager maintains backward-compatible method names (e.g., `create_document`, `list_documents`) but internally uses the new TablesDB API. Your existing code will continue to work, but you're now using tables and rows instead of collections and documents.

## [1.0.1] - 2024-11-09

### Fixed
- Fixed `body_text` property to use `context.req.body_text` instead of `context.req.body`
- Fixed `body_json` property to use Appwrite's built-in `context.req.body_json` instead of manually parsing with `json.loads()`
- This ensures compatibility with Appwrite's Python SDK API

## [1.0.0] - 2024-11-08

### Added
- Initial release of SecureAPI-Py
- Core SecureAPI class with request/response handling
- DatabaseManager for Appwrite database operations
- Router system for handling multiple endpoints
- Middleware system with built-in middleware:
  - Authentication middleware
  - CORS middleware
  - Rate limiting middleware
  - Request logging middleware
- Validator modules (basic and enhanced)
- Security module for JWT validation
- Custom error classes for better error handling
- Performance monitoring with timers
- Request context storage
- Pretty-print JSON logging
- Helper properties for common Appwrite patterns
- Comprehensive documentation and examples
