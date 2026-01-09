"""
Entry point để chạy Gradio UI
"""
import os
from src.ui.gradio_app import create_gradio_interface

if __name__ == "__main__":
    # Create outputs directory if not exists
    os.makedirs("outputs", exist_ok=True)

    # Create Gradio interface
    app = create_gradio_interface()

    # Launch
    print("🚀 Launching Gradio App (Refactored with Service Layer)...")
    print("📍 Open http://localhost:7860 in your browser")
    print("\n" + "=" * 70)

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
