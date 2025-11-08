"""
MHA Flow Launcher
=================

Launcher script for MHA Flow - Opens web interfaces and provides easy access.

Commands:
    mha-flow         : Launch local Streamlit interface
    mha-flow-web     : Open online interface in browser
    mha-demo         : Run demo system
"""

import webbrowser
import os
import sys
import subprocess
from pathlib import Path


def launch_online_interface():
    """
    Open the online MHA Flow web interface in the default browser.
    
    Usage:
        mha-flow-web
    """
    url = "https://mha-flow.streamlit.app/"
    
    print("=" * 70)
    print("🚀 MHA FLOW - Online Web Interface")
    print("=" * 70)
    print(f"\n🌐 Opening: {url}")
    print("\n✨ Features:")
    print("   • 130+ Metaheuristic Algorithms")
    print("   • AI-Powered Algorithm Recommendations")
    print("   • Modern 3-Step Workflow")
    print("   • Real-time Visualizations")
    print("   • Multi-user Support with Authentication")
    print("   • Comprehensive Results Analysis")
    print("\n💡 Tip: If the browser doesn't open automatically, visit:")
    print(f"   {url}")
    print("\n" + "=" * 70)
    
    try:
        webbrowser.open(url)
        print("\n✅ Browser opened successfully!")
    except Exception as e:
        print(f"\n⚠️  Could not open browser automatically: {e}")
        print(f"   Please visit: {url}")
    
    return 0


def launch_local_interface():
    """
    Launch the local Streamlit web interface.
    
    Usage:
        mha-flow
    """
    print("=" * 70)
    print("🚀 MHA FLOW - Local Web Interface")
    print("=" * 70)
    print("\n🔧 Starting local Streamlit server...")
    print("\n✨ Features:")
    print("   • Full offline functionality")
    print("   • All 130+ algorithms available")
    print("   • AI-powered recommendations")
    print("   • User authentication & history")
    print("   • Advanced visualizations")
    print("\n💡 Options:")
    print("   • Use 'mha-flow-web' to open online version instead")
    print("   • Use 'mha-flow-cli' for command-line interface")
    print("\n" + "=" * 70)
    
    # Find the mha_ui_complete.py file
    package_dir = Path(__file__).parent
    ui_file = package_dir / "mha_ui_complete.py"
    
    # Fallback to ui.py if mha_ui_complete.py doesn't exist
    if not ui_file.exists():
        ui_file = package_dir / "ui.py"
    
    # Fallback to frontend.py if neither exists
    if not ui_file.exists():
        ui_file = package_dir / "frontend.py"
    
    if not ui_file.exists():
        print("\n❌ Error: UI file not found!")
        print("   Searched for:")
        print(f"     - {package_dir / 'mha_ui_complete.py'}")
        print(f"     - {package_dir / 'ui.py'}")
        print(f"     - {package_dir / 'frontend.py'}")
        print("\n💡 Solution 1: Use 'mha-flow-web' to access the online interface (recommended)")
        print("💡 Solution 2: Run from source directory:")
        print(f"     cd {package_dir.parent}")
        print(f"     streamlit run {package_dir / 'mha_ui_complete.py'}")
        return 1
    
    try:
        print(f"\n🌟 Launching: {ui_file.name}")
        print("   Press Ctrl+C to stop the server\n")
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(ui_file),
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--theme.base=dark"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 MHA Flow server stopped. Goodbye!")
        return 0
    except FileNotFoundError:
        print("\n❌ Error: Streamlit not installed!")
        print("\n📦 Install with: pip install mha-flow[ui]")
        print("   Or use: pip install streamlit")
        print("\n💡 Alternative: Use 'mha-flow-web' to access the online interface")
        return 1
    except Exception as e:
        print(f"\n❌ Error launching interface: {e}")
        print("\n💡 Alternative: Use 'mha-flow-web' to access the online interface")
        return 1


def launch_web_interface():
    """
    Legacy function - redirects to launch_local_interface for backward compatibility.
    """
    print("⚠️  'mha-web' is deprecated. Use 'mha-flow' or 'mha-flow-web' instead.\n")
    return launch_local_interface()


def run_demo_system():
    """
    Run the MHA Flow demo system.
    
    Usage:
        mha-demo
    """
    print("=" * 70)
    print("🎯 MHA FLOW - Demo System")
    print("=" * 70)
    print("\n🚀 Starting interactive demo...")
    
    try:
        from mha_toolbox.demo_system import MHADemoSystem
        
        demo = MHADemoSystem()
        demo.run_complete_demo()
        
        return 0
        
    except ImportError as e:
        print(f"\n❌ Error: Could not import demo system: {e}")
        print("\n💡 Try: pip install mha-flow[complete]")
        return 1
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        return 1


def show_help():
    """Display help information for MHA Flow commands."""
    print("""
═══════════════════════════════════════════════════════════════════════
                        🚀 MHA FLOW v2.0.4
        Professional Metaheuristic Algorithm Library
═══════════════════════════════════════════════════════════════════════

📖 AVAILABLE COMMANDS:

  mha-flow              Launch local web interface (Streamlit)
  mha-flow-web          Open online interface (https://mha-flow.streamlit.app/)
  mha-flow-cli          Command-line interface for batch processing
  mha-demo              Run interactive demo system

═══════════════════════════════════════════════════════════════════════

🎯 QUICK START:

  1. Local Interface (Offline):
     $ mha-flow
  
  2. Online Interface (No Installation):
     $ mha-flow-web
  
  3. Library Usage (Python):
     >>> from mha_toolbox import MHAToolbox
     >>> toolbox = MHAToolbox()
     >>> result = toolbox.optimize('pso', X, y)

═══════════════════════════════════════════════════════════════════════

✨ FEATURES:

  • 130+ Metaheuristic Algorithms
  • AI-Powered Algorithm Recommendations
  • Modern 3-Step Workflow
  • Real-time Visualizations
  • Multi-user Authentication
  • Comprehensive Results Analysis
  • Feature Selection & Optimization
  • Hyperparameter Tuning

═══════════════════════════════════════════════════════════════════════

📚 DOCUMENTATION:

  GitHub:  https://github.com/Achyut103040/MHA-Algorithm
  Online:  https://mha-flow.streamlit.app/
  PyPI:    https://pypi.org/project/mha-flow/

═══════════════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    # If run directly, show help
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command in ['--help', '-h', 'help']:
            show_help()
        elif command == 'web':
            launch_online_interface()
        elif command == 'local':
            launch_local_interface()
        elif command == 'demo':
            run_demo_system()
        else:
            print(f"Unknown command: {command}")
            show_help()
    else:
        show_help()
