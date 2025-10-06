#!/usr/bin/env python3
"""
WSGI Entry Point for Production Deployment
This file is used by Gunicorn to serve the Flask application
"""

from application import create_app

# Create application instance without debug mode for production
app = create_app()

if __name__ == '__main__':
    # This should not be used in production - only for testing
    app.run(debug=False, host='0.0.0.0', port=5000)
