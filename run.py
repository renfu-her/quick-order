#!/usr/bin/env python3
"""
Startup Script
"""

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("Quick Orders System Starting...")
    print("Access URL: http://localhost:5000")
    print("Admin Panel: http://localhost:5000/admin")
    print("Default Admin: admin@example.com / admin123")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
