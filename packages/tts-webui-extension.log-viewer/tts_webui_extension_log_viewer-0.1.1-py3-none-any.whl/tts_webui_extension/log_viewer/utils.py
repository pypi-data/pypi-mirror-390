"""Utility functions for log file operations."""

import os
import glob
from datetime import datetime
from pathlib import Path


def get_log_directory():
    """Get the path to the logs directory."""
    # Use current working directory of the main Python process
    log_dir = Path.cwd() / "logs"
    return str(log_dir)


def list_log_files():
    """List all log files in the logs directory."""
    log_dir = get_log_directory()
    if not os.path.exists(log_dir):
        return []
    
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    # Sort by modification time (newest first)
    log_files.sort(key=os.path.getmtime, reverse=True)
    
    # Return just the filenames
    return [os.path.basename(f) for f in log_files]


def get_pip_install_logs():
    """Get list of pip installation log files with cleaned names."""
    log_dir = get_log_directory()
    if not os.path.exists(log_dir):
        return []
    
    log_files = glob.glob(os.path.join(log_dir, "pip-install-*.log"))
    log_files.sort(key=os.path.getmtime, reverse=True)
    
    # Clean up the filenames for display
    cleaned = []
    for f in log_files:
        basename = os.path.basename(f)
        # Remove "pip-install-" prefix and ".log" suffix
        name = basename.replace("pip-install-", "").replace(".log", "")
        cleaned.append((name, basename))
    
    return cleaned


def get_pip_uninstall_logs():
    """Get list of pip uninstallation log files with cleaned names."""
    log_dir = get_log_directory()
    if not os.path.exists(log_dir):
        return []
    
    log_files = glob.glob(os.path.join(log_dir, "pip-uninstall-*.log"))
    log_files.sort(key=os.path.getmtime, reverse=True)
    
    cleaned = []
    for f in log_files:
        basename = os.path.basename(f)
        name = basename.replace("pip-uninstall-", "").replace(".log", "")
        cleaned.append((name, basename))
    
    return cleaned


def get_log_file_info(filename):
    """Get information about a log file."""
    if not filename:
        return "No file selected"
    
    log_dir = get_log_directory()
    filepath = os.path.join(log_dir, filename)
    
    if not os.path.exists(filepath):
        return "File not found"
    
    stat = os.stat(filepath)
    size_kb = stat.st_size / 1024
    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    
    return f"**File:** {filename}\n**Size:** {size_kb:.2f} KB\n**Modified:** {modified}"


def read_log_file(filename, search_term="", max_lines=1000):
    """Read and return the contents of a log file."""
    if not filename:
        return "No file selected"
    
    log_dir = get_log_directory()
    filepath = os.path.join(log_dir, filename)
    
    if not os.path.exists(filepath):
        return "File not found"
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        # Apply search filter if provided
        if search_term:
            lines = [line for line in lines if search_term.lower() in line.lower()]
        
        # Limit number of lines
        total_lines = len(lines)
        if total_lines > max_lines:
            lines = lines[-max_lines:]
            content = f"[Showing last {max_lines} of {total_lines} lines]\n\n" + "".join(lines)
        else:
            content = "".join(lines)
        
        if not content.strip():
            if search_term:
                return f"No matches found for '{search_term}'"
            return "Log file is empty"
        
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


def delete_log_file(filename):
    """Delete a log file."""
    if not filename:
        return "No file selected", list_log_files()
    
    log_dir = get_log_directory()
    filepath = os.path.join(log_dir, filename)
    
    if not os.path.exists(filepath):
        return "File not found", list_log_files()
    
    try:
        os.remove(filepath)
        return f"Successfully deleted {filename}", list_log_files()
    except Exception as e:
        return f"Error deleting file: {str(e)}", list_log_files()


def delete_all_logs():
    """Delete all log files."""
    log_dir = get_log_directory()
    if not os.path.exists(log_dir):
        return "Logs directory not found", []
    
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    deleted_count = 0
    errors = []
    
    for filepath in log_files:
        try:
            os.remove(filepath)
            deleted_count += 1
        except Exception as e:
            errors.append(f"{os.path.basename(filepath)}: {str(e)}")
    
    result = f"Deleted {deleted_count} log file(s)"
    if errors:
        result += f"\n\nErrors:\n" + "\n".join(errors)
    
    return result, list_log_files()


def get_log_stats():
    """Get statistics about the logs directory."""
    log_dir = get_log_directory()
    if not os.path.exists(log_dir):
        return "Logs directory not found"
    
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    total_size = sum(os.path.getsize(f) for f in log_files)
    total_size_mb = total_size / (1024 * 1024)
    
    return f"**Total Log Files:** {len(log_files)}\n**Total Size:** {total_size_mb:.2f} MB"
