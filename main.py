#!/usr/bin/env python
"""
Main entry point for Analytics Microservice v3.
Starts the REST API server.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics_microservice_v3.rest_server import run_server

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    print("Starting Analytics Microservice v3 REST API...")
    run_server()