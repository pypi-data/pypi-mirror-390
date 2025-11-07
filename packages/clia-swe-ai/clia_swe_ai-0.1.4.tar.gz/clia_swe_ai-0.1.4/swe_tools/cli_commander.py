

import subprocess
import os
import sys
import uuid
from typing import Optional, Dict, Any, Union

from swe_tools.instance import mcp

@mcp.tool(
    name="run_shell_command",
    description="""Executes a shell command, either synchronously (waiting for completion) or asynchronously (running in the background).

When run in the background, it redirects stdout and stderr to log files and returns the process ID (PID) and log paths, allowing for monitoring of long-running processes like servers or build jobs.

When run synchronously, it waits for the command to finish (with a timeout) and returns all output directly. This is suitable for short, quick commands."""
)
def run_shell_command(
    command: str,
    working_directory: Optional[str] = None,
    timeout: int = 60,
    run_in_background: bool = False
) -> Union[str, Dict[str, Any]]:
    """
    Executes a shell command either synchronously or in the background.

    Args:
        command: The command to execute.
        working_directory: The directory to run the command in.
        timeout: Timeout in seconds for synchronous commands.
        run_in_background: If True, runs the command in the background and returns process info.

    Returns:
        If run_in_background is True, a dictionary with PID and log paths.
        Otherwise, a string with the command's output.
    """
    if not command:
        return {"status": "Error", "message": "No command provided."}

    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'

    if run_in_background:
        try:
            logs_dir = os.path.join(os.getcwd(), '.logs')
            os.makedirs(logs_dir, exist_ok=True)

            run_id = str(uuid.uuid4())
            log_path = os.path.join(logs_dir, f"{run_id}.log")
            mapping_file = os.path.join(logs_dir, ".process_mapping")

            # Use shell redirection for robust logging
            redirected_command = f"{command} > {log_path} 2>&1"

            popen_kwargs = {
                "shell": True,
                "stdin": subprocess.DEVNULL,
                "cwd": working_directory,
                "env": env,
            }
            if sys.platform == 'win32':
                popen_kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                popen_kwargs['start_new_session'] = True

            process = subprocess.Popen(redirected_command, **popen_kwargs)

            # Store the process mapping
            mapping_file = os.path.join(logs_dir, ".process_mapping")
            with open(mapping_file, "a") as f:
                f.write(f"{run_id},{process.pid},{command}\n")

            return {
                "status": "Running in background",
                "pid": process.pid,
                "run_id": run_id,
                "log_path": log_path,
                "command": command
            }
        except Exception as e:
            return {"status": "Error", "message": f"Failed to start background process: {e}"}

    else:  # Synchronous execution
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                text=True,
                cwd=working_directory,
                env=env,
            )

            stdout, stderr = process.communicate(timeout=timeout)
            return_code = process.returncode

            output = [
                f"Status: {'Success' if return_code == 0 else 'Failure'}",
                f"Return Code: {return_code}",
                "--- stdout ---",
                stdout.strip() if stdout else "(empty)",
                "--- stderr ---",
                stderr.strip() if stderr else "(empty)"
            ]
            return "\n".join(output)

        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            timeout_output = [
                "Status: Failure",
                "Return Code: -1 (Terminated due to timeout)",
                f"Error: Command '{command}' timed out after {timeout} seconds and was terminated.",
                "--- stdout (captured before timeout) ---",
                stdout.strip() if stdout else "No stdout captured.",
                "--- stderr (captured before timeout) ---",
                stderr.strip() if stderr else "No stderr captured."
            ]
            return "\n".join(timeout_output)

        except Exception as e:
            return f"Error executing command '{command}': {e}"
