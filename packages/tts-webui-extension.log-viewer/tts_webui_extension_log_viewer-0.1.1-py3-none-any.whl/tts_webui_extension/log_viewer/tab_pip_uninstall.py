"""UI for Pip Uninstall Logs tab."""

import gradio as gr

try:
    from .utils import get_pip_uninstall_logs, get_log_file_info, read_log_file
    from .analyzer import analyze_pip_log
except ImportError:
    from utils import get_pip_uninstall_logs, get_log_file_info, read_log_file
    from analyzer import analyze_pip_log


def create_pip_uninstall_tab():
    """Create the Pip Uninstall Logs tab UI."""
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Uninstallation Logs")
            uninstall_count = gr.Markdown(f"**Total Uninstall Logs:** {len(get_pip_uninstall_logs())}")
            refresh_uninstall_btn = gr.Button("🔄 Refresh", size="sm")
            
            # Get initial choices - use cleaned names for display, filenames as values
            initial_uninstall_logs = get_pip_uninstall_logs()
            pip_uninstall_dropdown = gr.Dropdown(
                label="Select Uninstallation Log",
                choices=[(name, fname) for name, fname in initial_uninstall_logs],
                value=None,
                interactive=True,
            )
            uninstall_info = gr.Markdown("No file selected")
        
        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.Tab("📊 Analysis"):
                    uninstall_analysis = gr.Markdown("Select a log file to see analysis")
                
                with gr.Tab("📄 Raw Log"):
                    with gr.Row():
                        uninstall_search = gr.Textbox(
                            label="Search",
                            placeholder="Enter text to filter...",
                            scale=3,
                        )
                        uninstall_max_lines = gr.Number(
                            label="Max Lines",
                            value=1000,
                            minimum=100,
                            maximum=10000,
                            step=100,
                            scale=1,
                        )
                        uninstall_view_btn = gr.Button("👁️ View", scale=1)
                    
                    uninstall_content = gr.Textbox(
                        label="Log Content",
                        lines=25,
                        max_lines=25,
                        show_copy_button=True,
                        interactive=False,
                    )
    
    # Event handlers
    def refresh_uninstall():
        logs = get_pip_uninstall_logs()
        count = f"**Total Uninstall Logs:** {len(logs)}"
        choices = [(name, fname) for name, fname in logs]
        return gr.update(choices=choices, value=None), count, "No file selected", "Select a log file to see analysis"
    
    refresh_uninstall_btn.click(
        fn=refresh_uninstall,
        inputs=[],
        outputs=[pip_uninstall_dropdown, uninstall_count, uninstall_info, uninstall_analysis],
    )
    
    def update_uninstall_info_and_analyze(filename):
        if filename:
            info = get_log_file_info(filename)
            analysis = analyze_pip_log(filename)
            return info, analysis
        return "No file selected", "Select a log file to see analysis"
    
    pip_uninstall_dropdown.change(
        fn=update_uninstall_info_and_analyze,
        inputs=[pip_uninstall_dropdown],
        outputs=[uninstall_info, uninstall_analysis],
    )
    
    uninstall_view_btn.click(
        fn=read_log_file,
        inputs=[pip_uninstall_dropdown, uninstall_search, uninstall_max_lines],
        outputs=[uninstall_content],
    )
    
    uninstall_search.submit(
        fn=read_log_file,
        inputs=[pip_uninstall_dropdown, uninstall_search, uninstall_max_lines],
        outputs=[uninstall_content],
    )
