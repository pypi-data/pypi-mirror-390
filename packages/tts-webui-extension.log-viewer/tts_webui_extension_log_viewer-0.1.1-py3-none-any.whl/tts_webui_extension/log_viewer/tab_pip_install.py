"""UI for Pip Install Logs tab."""

import gradio as gr

try:
    from .utils import get_pip_install_logs, get_log_file_info, read_log_file
    from .analyzer import analyze_pip_log, get_pip_log_summary
except ImportError:
    from utils import get_pip_install_logs, get_log_file_info, read_log_file
    from analyzer import analyze_pip_log, get_pip_log_summary


def create_pip_install_tab():
    """Create the Pip Install Logs tab UI."""
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Installation Logs")
            pip_summary = gr.Markdown(get_pip_log_summary())
            refresh_pip_btn = gr.Button("🔄 Refresh", size="sm")
            
            # Get initial choices - use cleaned names for display, filenames as values
            initial_pip_logs = get_pip_install_logs()
            pip_install_dropdown = gr.Dropdown(
                label="Select Installation Log",
                choices=[(name, fname) for name, fname in initial_pip_logs],
                value=None,
                interactive=True,
            )
            pip_info = gr.Markdown("No file selected")
        
        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.Tab("📊 Analysis"):
                    pip_analysis = gr.Markdown("Select a log file to see analysis")
                
                with gr.Tab("📄 Raw Log"):
                    with gr.Row():
                        pip_search = gr.Textbox(
                            label="Search",
                            placeholder="Enter text to filter...",
                            scale=3,
                        )
                        pip_max_lines = gr.Number(
                            label="Max Lines",
                            value=1000,
                            minimum=100,
                            maximum=10000,
                            step=100,
                            scale=1,
                        )
                        pip_view_btn = gr.Button("👁️ View", scale=1)
                    
                    pip_content = gr.Textbox(
                        label="Log Content",
                        lines=25,
                        max_lines=25,
                        show_copy_button=True,
                        interactive=False,
                    )
    
    # Event handlers
    def refresh_pip():
        logs = get_pip_install_logs()
        summary = get_pip_log_summary()
        choices = [(name, fname) for name, fname in logs]
        return gr.update(choices=choices, value=None), summary, "No file selected", "Select a log file to see analysis"
    
    refresh_pip_btn.click(
        fn=refresh_pip,
        inputs=[],
        outputs=[pip_install_dropdown, pip_summary, pip_info, pip_analysis],
    )
    
    def update_pip_info_and_analyze(filename):
        if filename:
            info = get_log_file_info(filename)
            analysis = analyze_pip_log(filename)
            return info, analysis
        return "No file selected", "Select a log file to see analysis"
    
    pip_install_dropdown.change(
        fn=update_pip_info_and_analyze,
        inputs=[pip_install_dropdown],
        outputs=[pip_info, pip_analysis],
    )
    
    pip_view_btn.click(
        fn=read_log_file,
        inputs=[pip_install_dropdown, pip_search, pip_max_lines],
        outputs=[pip_content],
    )
    
    pip_search.submit(
        fn=read_log_file,
        inputs=[pip_install_dropdown, pip_search, pip_max_lines],
        outputs=[pip_content],
    )
