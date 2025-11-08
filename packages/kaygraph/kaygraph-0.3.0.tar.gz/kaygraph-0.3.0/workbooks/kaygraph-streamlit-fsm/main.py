#!/usr/bin/env python3
"""
Main entry point for Streamlit FSM app.

This is a wrapper to maintain consistency with other workbooks.
The actual Streamlit app is in app.py.
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit app."""
    print("🚀 Launching KayGraph Streamlit FSM Demo...")
    print("=" * 50)
    print("This will open a web browser with the FSM interface.")
    print("Press Ctrl+C to stop the server.")
    print("=" * 50)
    
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")
    
    # Run streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print("\n\n✅ Streamlit server stopped.")
    except Exception as e:
        print(f"\n❌ Error running Streamlit: {e}")
        print("\nMake sure Streamlit is installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()