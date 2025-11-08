"""Main entry point for the Log Viewer extension."""

import gradio as gr

try:
    from .tab_pip_install import create_pip_install_tab
    from .tab_pip_uninstall import create_pip_uninstall_tab
    from .tab_all_logs import create_all_logs_tab
except ImportError:
    from tab_pip_install import create_pip_install_tab
    from tab_pip_uninstall import create_pip_uninstall_tab
    from tab_all_logs import create_all_logs_tab


def log_viewer_ui():
    """Create the main Log Viewer UI with tabs."""
    gr.Markdown(
        """
    # 📋 Log Viewer
    
    View and manage log files from the TTS Generation WebUI.
    """
    )
    
    with gr.Tabs():
        with gr.Tab("📦 Pip Install Logs"):
            create_pip_install_tab()
        
        with gr.Tab("🗑️ Pip Uninstall Logs"):
            create_pip_uninstall_tab()
        
        with gr.Tab("📁 All Logs"):
            create_all_logs_tab()


def extension__tts_generation_webui():
    """Extension entry point for TTS Generation WebUI."""
    log_viewer_ui()
    
    return {
        "package_name": "tts_webui_extension.log_viewer",
        "name": "Log Viewer",
        "requirements": "git+https://github.com/rsxdalv/tts_webui_extension.log_viewer@main",
        "description": "View, search, and manage log files from the TTS Generation WebUI. Browse installation logs, filter by keywords, and clean up old logs.",
        "extension_type": "interface",
        "extension_class": "settings",
        "author": "rsxdalv",
        "extension_author": "rsxdalv",
        "license": "MIT",
        "website": "https://github.com/rsxdalv/tts-generation-webui",
        "extension_website": "https://github.com/rsxdalv/tts_webui_extension.log_viewer",
        "extension_platform_version": "0.1.0",
    }


if __name__ == "__main__":
    if "demo" in locals():
        locals()["demo"].close()
    with gr.Blocks() as demo:
        with gr.Tab("Log viewer", id="log_viewer"):
            log_viewer_ui()

    demo.launch(server_port=7772)
