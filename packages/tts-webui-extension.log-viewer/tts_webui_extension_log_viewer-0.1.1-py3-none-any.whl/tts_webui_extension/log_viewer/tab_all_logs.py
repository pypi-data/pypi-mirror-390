"""UI for All Logs tab."""

import gradio as gr

try:
    from .utils import (
        list_log_files,
        get_log_stats,
        get_log_file_info,
        read_log_file,
        delete_log_file,
        delete_all_logs,
    )
except ImportError:
    from utils import (
        list_log_files,
        get_log_stats,
        get_log_file_info,
        read_log_file,
        delete_log_file,
        delete_all_logs,
    )


def create_all_logs_tab():
    """Create the All Logs tab UI."""
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Log Files")
            log_stats = gr.Markdown(get_log_stats())
            refresh_btn = gr.Button("🔄 Refresh List", size="sm")
            log_dropdown = gr.Dropdown(
                label="Select Log File",
                choices=list_log_files(),
                value=None,
                interactive=True,
            )
            log_info = gr.Markdown("No file selected")
            
            with gr.Row():
                delete_btn = gr.Button("🗑️ Delete Selected", size="sm", variant="stop")
                delete_all_btn = gr.Button("🗑️ Delete All", size="sm", variant="stop")
        
        with gr.Column(scale=3):
            gr.Markdown("### Log Content")
            
            with gr.Row():
                search_box = gr.Textbox(
                    label="Search",
                    placeholder="Enter text to filter log entries...",
                    scale=3,
                )
                max_lines = gr.Number(
                    label="Max Lines",
                    value=1000,
                    minimum=100,
                    maximum=10000,
                    step=100,
                    scale=1,
                )
                view_btn = gr.Button("👁️ View", scale=1)
            
            log_content = gr.Textbox(
                label="Log Content",
                lines=25,
                max_lines=25,
                show_copy_button=True,
                interactive=False,
            )
            
            status_text = gr.Textbox(label="Status", visible=False)
    
    # Event handlers
    def refresh_all():
        files = list_log_files()
        stats = get_log_stats()
        return gr.update(choices=files, value=None), stats, "No file selected", ""
    
    refresh_btn.click(
        fn=refresh_all,
        inputs=[],
        outputs=[log_dropdown, log_stats, log_info, log_content],
    )
    
    def update_log_info_and_content(filename, search_term, max_lines_val):
        if filename:
            info = get_log_file_info(filename)
            content = read_log_file(filename, search_term, max_lines_val)
            return info, content
        return "No file selected", ""
    
    log_dropdown.change(
        fn=update_log_info_and_content,
        inputs=[log_dropdown, search_box, max_lines],
        outputs=[log_info, log_content],
    )
    
    view_btn.click(
        fn=read_log_file,
        inputs=[log_dropdown, search_box, max_lines],
        outputs=[log_content],
    )
    
    search_box.submit(
        fn=read_log_file,
        inputs=[log_dropdown, search_box, max_lines],
        outputs=[log_content],
    )
    
    def handle_delete(filename):
        status, files = delete_log_file(filename)
        stats = get_log_stats()
        return status, files, stats, "No file selected", ""
    
    delete_btn.click(
        fn=handle_delete,
        inputs=[log_dropdown],
        outputs=[status_text, log_dropdown, log_stats, log_info, log_content],
    ).then(
        fn=lambda x: gr.update(visible=True) if x else gr.update(visible=False),
        inputs=[status_text],
        outputs=[status_text],
    )
    
    def handle_delete_all():
        status, files = delete_all_logs()
        stats = get_log_stats()
        return status, files, stats, "No file selected", ""
    
    delete_all_btn.click(
        fn=handle_delete_all,
        inputs=[],
        outputs=[status_text, log_dropdown, log_stats, log_info, log_content],
    ).then(
        fn=lambda x: gr.update(visible=True) if x else gr.update(visible=False),
        inputs=[status_text],
        outputs=[status_text],
    )
