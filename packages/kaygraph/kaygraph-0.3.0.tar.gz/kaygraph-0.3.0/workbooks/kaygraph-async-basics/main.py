#!/usr/bin/env python3
"""
Main entry point for KayGraph Async Basics tutorial.

This workbook contains two tutorial files:
1. 01_basic_async.py - Introduction to async nodes
2. 02_async_workflow.py - Building async workflows
"""

import subprocess
import sys
import os

def main():
    """Interactive menu for async tutorials."""
    print("⚡ KayGraph Async Basics Tutorial")
    print("=" * 50)
    print("Choose a tutorial:")
    print("1. Basic Async - Introduction to async nodes")
    print("2. Async Workflow - Building async workflows")
    print("3. Run both tutorials in sequence")
    print("4. Exit")
    print("=" * 50)
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n📚 Running Basic Async tutorial...")
            print("-" * 50)
            subprocess.run([sys.executable, "01_basic_async.py"])
            break
        elif choice == "2":
            print("\n🔄 Running Async Workflow tutorial...")
            print("-" * 50)
            subprocess.run([sys.executable, "02_async_workflow.py"])
            break
        elif choice == "3":
            print("\n🎯 Running both tutorials...")
            print("\n📚 Part 1: Basic Async")
            print("-" * 50)
            subprocess.run([sys.executable, "01_basic_async.py"])
            print("\n🔄 Part 2: Async Workflow")
            print("-" * 50)
            subprocess.run([sys.executable, "02_async_workflow.py"])
            break
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Direct execution of specific tutorial
        if sys.argv[1] == "basic":
            subprocess.run([sys.executable, "01_basic_async.py"])
        elif sys.argv[1] == "workflow":
            subprocess.run([sys.executable, "02_async_workflow.py"])
        else:
            print(f"Unknown tutorial: {sys.argv[1]}")
            print("Usage: python main.py [basic|workflow]")
    else:
        main()