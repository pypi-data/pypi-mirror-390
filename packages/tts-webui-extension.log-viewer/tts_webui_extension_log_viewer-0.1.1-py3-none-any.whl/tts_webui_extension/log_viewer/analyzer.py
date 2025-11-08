"""Log analysis functions for pip installation logs."""

import os
from datetime import datetime

try:
    from .utils import get_log_directory, get_pip_install_logs, get_pip_uninstall_logs
except ImportError:
    from utils import get_log_directory, get_pip_install_logs, get_pip_uninstall_logs


def analyze_pip_log(filename):
    """Analyze a pip installation log and return status information."""
    if not filename:
        return "No file selected"
    
    log_dir = get_log_directory()
    filepath = os.path.join(log_dir, filename)
    
    if not os.path.exists(filepath):
        return "File not found"
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Analysis results
        result = []
        result.append(f"# 📊 Analysis: {filename}\n")
        
        # Check for overall success/failure indicators
        errors = []
        warnings = []
        success_indicators = []
        
        lines = content.split('\n')
        
        # Look for error patterns
        error_patterns = [
            "ERROR:",
            "Error:",
            "error:",
            "FAILED",
            "Failed",
            "failed",
            "Could not",
            "could not",
            "Exception:",
            "Traceback",
        ]
        
        warning_patterns = [
            "WARNING:",
            "Warning:",
            "warning:",
            "deprecated",
            "DEPRECATION",
        ]
        
        success_patterns = [
            "Successfully installed",
            "Successfully uninstalled",
            "Requirement already satisfied",
            "finished with status 'done'",
        ]
        
        for line in lines:
            for pattern in error_patterns:
                if pattern in line:
                    errors.append(line.strip())
                    break
            for pattern in warning_patterns:
                if pattern in line:
                    warnings.append(line.strip())
                    break
            for pattern in success_patterns:
                if pattern in line:
                    success_indicators.append(line.strip())
                    break
        
        # Determine overall status
        if errors:
            result.append("## ❌ Status: FAILED\n")
        elif success_indicators:
            result.append("## ✅ Status: SUCCESS\n")
        else:
            result.append("## ❓ Status: UNKNOWN\n")
        
        # Add statistics
        result.append(f"**Total Lines:** {len(lines)}")
        result.append(f"**Errors Found:** {len(set(errors))}")
        result.append(f"**Warnings Found:** {len(set(warnings))}")
        result.append(f"**Success Messages:** {len(set(success_indicators))}\n")
        
        # Show success indicators
        if success_indicators:
            result.append("### ✅ Success Indicators:")
            for msg in list(set(success_indicators))[:5]:  # Show first 5 unique
                result.append(f"- {msg}")
            result.append("")
        
        # Show errors
        if errors:
            result.append("### ❌ Errors Found:")
            for error in list(set(errors))[:10]:  # Show first 10 unique errors
                result.append(f"- {error}")
            result.append("")
        
        # Show warnings
        if warnings:
            result.append("### ⚠️ Warnings Found:")
            for warning in list(set(warnings))[:5]:  # Show first 5 unique warnings
                result.append(f"- {warning}")
            result.append("")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error analyzing file: {str(e)}"


def get_pip_log_summary():
    """Generate a summary of all pip installation logs."""
    install_logs = get_pip_install_logs()
    uninstall_logs = get_pip_uninstall_logs()
    
    result = []
    result.append("# 📦 Pip Logs Summary\n")
    result.append(f"**Installation Logs:** {len(install_logs)}")
    result.append(f"**Uninstallation Logs:** {len(uninstall_logs)}\n")
    
    # Quick status check for recent installs
    result.append("## Recent Installations (Last 10):")
    
    for name, filename in install_logs[:10]:
        log_dir = get_log_directory()
        filepath = os.path.join(log_dir, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
            
            # More accurate status detection
            has_error = any(pattern in content for pattern in ["error:", "failed building", "exception:", "traceback (most"])
            has_success = any(pattern in content for pattern in ["successfully installed", "requirement already satisfied"])
            
            if has_error and not has_success:
                status = "❌"
            elif has_success or "finished with status 'done'" in content:
                status = "✅"
            else:
                status = "❓"
            
            # Get file size
            size_kb = os.path.getsize(filepath) / 1024
            modified = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M")
            
            result.append(f"\n{status} **{name}** - {size_kb:.1f}KB - {modified}")
        except:
            result.append(f"\n❓ **{name}** - Error reading file")
    
    return "\n".join(result)
