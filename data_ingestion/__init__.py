"""
Data Ingestion Module for Analytics Microservice v3.

Provides intelligent data ingestion with chain-of-thought reasoning
for CSV data analysis and visualization generation.

Key Components:
- database/: PostgreSQL integration for session storage
- upload/: CSV file handling and validation
- tools/: MCP-style tools for data operations
- agent/: Chain-of-thought reasoning engine
- models/: Pydantic models for requests/responses

API Prefix: /api/v1/data/
"""

__version__ = "1.0.0"
