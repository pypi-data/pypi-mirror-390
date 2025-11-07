"""
MHA Toolbox - Web UI Entry Point
Launches the web interface for beginners and visual users
"""

def launch_ui():
    """Launch the web interface"""
    try:
        from mha_web_interface import app
        print("🚀 Starting MHA Toolbox Web Interface...")
        print("📊 Open your browser at: http://localhost:5000")
        print("\n✨ Features:")
        print("   - Visual algorithm selection")
        print("   - Dataset upload & management")
        print("   - Real-time optimization tracking")
        print("   - Result export & visualization")
        print("   - Algorithm recommendation engine")
        print("\n💡 For library usage, see: from mha_toolbox import optimize")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("\n📦 UI dependencies missing. Install with:")
        print("   pip install mha-toolbox[ui]")
        print("\nOr install dependencies manually:")
        print("   pip install flask plotly dash")
        return None

if __name__ == "__main__":
    launch_ui()
