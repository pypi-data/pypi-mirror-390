#!/usr/bin/env python3
"""
Main entry point for Human-in-the-Loop examples.

Choose which interface to use:
1. CLI - Command-line interface
2. Web - Web-based interface (FastAPI)
3. Async - Asynchronous example
"""

import sys
import os
import subprocess

def main():
    """Interactive menu for HITL interfaces."""
    print("🤝 KayGraph Human-in-the-Loop Examples")
    print("=" * 50)
    print("Choose an interface:")
    print("1. CLI - Command-line approval workflow")
    print("2. Web - Browser-based approval (FastAPI)")
    print("3. Async - Asynchronous HITL example")
    print("4. Exit")
    print("=" * 50)
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n💻 Running CLI interface...")
            subprocess.run([sys.executable, "main_cli.py"])
            break
        elif choice == "2":
            print("\n🌐 Starting web interface...")
            print("Open http://localhost:8000 in your browser")
            subprocess.run([sys.executable, "main_web.py"])
            break
        elif choice == "3":
            print("\n⚡ Running async example...")
            subprocess.run([sys.executable, "main_async.py"])
            break
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

def cli():
    """Direct entry point for CLI interface."""
    subprocess.run([sys.executable, "main_cli.py"])

def web():
    """Direct entry point for web interface."""
    subprocess.run([sys.executable, "main_web.py"])

def async_example():
    """Direct entry point for async example."""
    subprocess.run([sys.executable, "main_async.py"])

if __name__ == "__main__":
    # Check if called with specific command
    if len(sys.argv) > 1:
        if sys.argv[1] == "cli":
            cli()
        elif sys.argv[1] == "web":
            web()
        elif sys.argv[1] == "async":
            async_example()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python main.py [cli|web|async]")
    else:
        main()