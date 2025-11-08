#!/usr/bin/env python3
"""
Main entry point for KayGraph visualization tools.

Choose which visualization to run:
1. trace_execution.py - Trace and debug graph execution
2. visualize.py - Visualize graph structure
"""

import sys
import os
import subprocess

def main():
    """Interactive menu for visualization tools."""
    print("🎨 KayGraph Visualization Tools")
    print("=" * 50)
    print("Choose a visualization tool:")
    print("1. Trace Execution - Debug graph execution flow")
    print("2. Visualize Graph - Generate graph structure diagram")
    print("3. Exit")
    print("=" * 50)
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🔍 Running execution tracer...")
            subprocess.run([sys.executable, "trace_execution.py"])
            break
        elif choice == "2":
            print("\n📊 Running graph visualizer...")
            subprocess.run([sys.executable, "visualize.py"])
            break
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
def trace():
    """Direct entry point for trace execution."""
    subprocess.run([sys.executable, "trace_execution.py"])

def visualize():
    """Direct entry point for graph visualization."""
    subprocess.run([sys.executable, "visualize.py"])

if __name__ == "__main__":
    # Check if called with specific command
    if len(sys.argv) > 1:
        if sys.argv[1] == "trace":
            trace()
        elif sys.argv[1] == "visualize":
            visualize()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python main.py [trace|visualize]")
    else:
        main()