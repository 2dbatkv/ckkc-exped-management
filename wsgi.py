#!/usr/bin/env python3
"""
WSGI entry point for production deployment
Used by Gunicorn and other WSGI servers
"""

from app import app, init_connection_pool

# Initialize the database connection pool when the WSGI app starts
init_connection_pool()

# This is what Gunicorn will import
application = app

if __name__ == "__main__":
    # For testing wsgi.py directly
    application.run()
