
import os
import psutil
from typing import Dict, Optional

from swe_tools.instance import mcp

@mcp.tool(
    name="read_process_logs",
    description="""Reads the combined stdout and stderr log file for a background process, given its unique run_id.

This tool is essential for monitoring the status and output of any command started with `run_in_background=True`.
It allows the AI to check for successful startup, diagnose errors, or track the progress of a long-running job without interrupting it."""
)
def read_process_logs(run_id: str) -> Dict[str, str]:
    """
    Reads the combined log file for a background process.

    Args:
        run_id: The unique ID of the run, returned by `run_shell_command`.

    Returns:
        A dictionary containing the logs.
    """
    logs_dir = ".logs"
    log_path = os.path.join(logs_dir, f"{run_id}.log")

    try:
        with open(log_path, 'r') as f:
            return {"log_content": f.read()}
    except FileNotFoundError:
        return {"error": f"Log file not found: {log_path}"}
    except Exception as e:
        return {"error": f"Error reading log file: {e}"}

@mcp.tool(
    name="stop_process",
    description="""Terminates a background process and its children using its PID.

This tool is crucial for cleaning up and stopping long-running services (like web servers) that were started in the background.
It ensures that processes do not continue running after they are no longer needed."""
)
def stop_process(pid: int) -> Dict[str, str]:
    """
    Terminates a process and its children using its PID.

    Args:
        pid: The process ID to terminate.

    Returns:
        A dictionary with a status message.
    """
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.terminate()
        parent.terminate()
        gone, still_alive = psutil.wait_procs(children + [parent], timeout=3)
        
        if not still_alive:
            return {"status": "Success", "message": f"Process {pid} and its children terminated."}
        else:
            for p in still_alive:
                p.kill()
            return {"status": "Success", "message": f"Process {pid} and its children forcefully killed."}

    except psutil.NoSuchProcess:
        return {"status": "Error", "message": f"Process with PID {pid} not found."}
    except Exception as e:
        return {"status": "Error", "message": f"Failed to terminate process {pid}: {e}"}

@mcp.tool(
    name="list_background_processes",
    description="""Lists all currently running background processes that were started by `run_shell_command`.

This tool is useful for getting an overview of all active background jobs, allowing the AI to track and manage them effectively."""
)
def list_background_processes() -> Dict[str, list]:
    """
    Scans the .logs directory to find active processes.
    """
    logs_dir = ".logs"
    mapping_file = os.path.join(logs_dir, ".process_mapping")
    if not os.path.exists(mapping_file):
        return {"processes": []}

    processes = []
    with open(mapping_file, "r") as f:
        for line in f:
            try:
                run_id, pid_str, command = line.strip().split(",", 2)
                pid = int(pid_str)
                if psutil.pid_exists(pid):
                    processes.append({
                        "run_id": run_id,
                        "pid": pid,
                        "command": command,
                        "status": "Running"
                    })
            except (ValueError, psutil.NoSuchProcess):
                continue # Skip processes that are no longer running or have invalid format
    return {"processes": processes}
