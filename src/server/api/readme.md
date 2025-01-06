# Memobase Backend API

Memobase is a user memory system designed for LLM Applications. It provides a FastAPI-based server that manages user profiles, memories, and various types of data blobs. Details of developing it in [here](./DEVELOPMENT.md).

## Core Components

### 1. API Layer (`api.py`)
- FastAPI application with versioned endpoints (`/api/v1`)
- Implements authentication middleware
- Main endpoints:
  - Health check
  - User management (CRUD operations)
  - Blob management
  - User profile management
  - Buffer management

### 2. Database Models (`models/`)
- Uses SQLAlchemy ORM
- Key models:
  - `User`: Core user entity
  - `GeneralBlob`: Stores various types of data
  - `BufferZone`: Temporary storage for processing
  - `UserProfile`: User memory profiles
- Supported Blob Types:
  - Chat
  - Document
  - Image
  - Code
  - Transcript

### 3. Controllers (`controllers/`)
- Business logic implementation
- Main modules:
  - `user`: User management
  - `blob`: Blob data handling
  - `buffer`: Buffer zone operations
  - `profile`: User profile management
- Modal processing:
  - Chat processing
  - Profile merging and extraction

### 4. Connectors (`connectors.py`)
- Database connection management (PostgreSQL)
- Redis connection handling
- Health check implementations
- Connection pooling configuration

### 5. Environment & Configuration (`env.py`)
- Configuration management
- Logger setup
- Token encoder initialization
- Environment variables handling

### 6. LLM Integration (`llms/`)
- OpenAI API integration
- Token management
- Async completion handling
- Response formatting

### 7. Prompts System (`prompts/`)
- Template management for LLM interactions
- Profile extraction and merging logic
- Multilingual support (English/Chinese)
- Summary generation

## Key Features

### Memory Management
- Long-term user profile storage
- Automatic memory merging and updating
- Buffer system for temporary storage
- Token-aware content management

### Authentication
- Bearer token authentication
- Configurable access control
- Middleware-based security

### Data Processing
- Async operation support
- Batch processing capabilities
- Automatic profile summarization
- Multi-modal data handling

## Dependencies
- FastAPI: Web framework
- SQLAlchemy: Database ORM
- Redis: Caching and temporary storage
- Pydantic: Data validation
- Tiktoken: Token management
- Rich: Enhanced logging

## Configuration
Key configuration options in `config.yaml`:
- System prompt
- Buffer flush interval
- Token size limits
- LLM settings
- Language preferences
- Model selection

## Development Guidelines
1. Use async/await for database operations
2. Implement proper error handling using Promise pattern
3. Follow token limits for profile management
4. Use proper typing with Pydantic models
5. Implement health checks for services
6. Handle multilingual support where needed

## Error Handling
- Uses custom Promise pattern
- HTTP status codes mapping
- Structured error responses
- Validation error handling

This documentation provides a high-level overview of the Memobase system. For specific implementation details, refer to the individual module documentation and code comments.
