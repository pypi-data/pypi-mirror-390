"""PyDM eXecute - Run Python tools and scripts with automatic dependency management."""

import os
import subprocess
import sys
from typing import List, Optional, Union

from rich.console import Console
from rich.theme import Theme

# Custom theme for consistent styling
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green"
})

# Create console with custom theme and settings
console = Console(
    theme=custom_theme,
    highlight=True,
    color_system="auto",
    force_terminal=True,
    width=None  # Auto-detect terminal width
)

def run_command(cmd: Union[str, List[str]], shell: bool = False, show_loading: bool = True) -> int:
    """Run a command and stream its output with rich formatting and colors.
    
    Args:
        cmd: The command to run as a string or list of strings
        shell: Whether to run the command through the shell
        show_loading: Whether to show a loading spinner
        
    Returns:
        int: The exit code of the command
    """
    import signal
    import time
    from threading import Thread, Event
    from queue import Queue, Empty
    from subprocess import CalledProcessError, SubprocessError, TimeoutExpired
    
    def show_loading_status():
        """Show a loading status using a simple spinner to avoid rich conflicts."""
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        idx = 0
        try:
            while not stop_event.is_set() and not process_finished.is_set():
                console.print(f"[cyan]{spinner_chars[idx]} Running...", end="\r")
                idx = (idx + 1) % len(spinner_chars)
                time.sleep(0.1)
        except Exception as e:
            console.print(f"[yellow]Warning: Error in loading thread: {e}")
        finally:
            # Clear the line when done
            console.print(" " * 20, end="\r")
    
    # Store the original signal handlers
    original_sigint = signal.getsignal(signal.SIGINT)
    process = None
    stop_event = Event()
    process_finished = Event()  # Event to signal process completion
    loading_thread = None
    output_thread = None
    
    def handle_interrupt(signum, frame):
        """Handle keyboard interrupt gracefully."""
        nonlocal process, stop_event
        
        # Restore the original signal handler first to prevent recursion
        signal.signal(signal.SIGINT, original_sigint)
        
        if process is not None and process.poll() is None:
            try:
                # Send SIGINT to the process group to ensure child processes are terminated
                if sys.platform == 'win32':
                    import ctypes
                    ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, 0)
                else:
                    import os
                    os.killpg(os.getpgid(process.pid), signal.SIGINT)
                
                # Wait a bit for the process to handle the signal
                time.sleep(0.5)
                
                # If it's still running, terminate it
                if process.poll() is None:
                    process.terminate()
                
                # Wait a bit more to ensure process termination
                time.sleep(0.2)
                
            except Exception as e:
                console.print(f"[yellow]Warning: Error during process termination: {e}[/]")
            
            # Set the stop event to clean up the loading animation
            stop_event.set()
        
        # Raise the keyboard interrupt to exit the program
        raise KeyboardInterrupt()
    
    # Check if this is a foreground command that should run without a spinner
    is_foreground_command = False
    if isinstance(cmd, (list, str)):
        cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
        cmd_str = cmd_str.lower()
        is_foreground_command = any(x in cmd_str for x in ['http.server', 'flask', 'django', 'uvicorn', 'gunicorn', 'dars'])
    
    try:
        # Set up environment to preserve colors and handle encoding
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["FORCE_COLOR"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        
        # Format the command for display
        cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
        
        # Enable ANSI colors on Windows
        if sys.platform == "win32":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not enable ANSI colors: {e}[/]")
        
        # Suppress the buffering warning
        import warnings
        warnings.filterwarnings("ignore", 
            message="line buffering .* isn't supported in binary mode")
        
        try:
            # Create the process with binary output and new process group
            # Inherit stdout/stderr so the child detects a TTY and keeps colors/boxes
            process = subprocess.Popen(
                cmd,
                stdout=None,
                stderr=None,
                bufsize=0,
                shell=shell,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0,
                start_new_session=True if sys.platform != 'win32' else False
            )
        except FileNotFoundError as e:
            cmd_name = cmd[0] if isinstance(cmd, list) else cmd.split()[0]
            console.print(f"[red]Error: Command not found: {cmd_name}[/]")
            return 127  # Standard "command not found" exit code
        
        # Set up the signal handler after process creation
        signal.signal(signal.SIGINT, handle_interrupt)
        
        # If we inherited stdout/stderr, no piping is needed; wait for completion
        if process.stdout is None:
            return_code = process.wait()
            return return_code

        # Queue for communication between threads (fallback if piping is re-enabled elsewhere)
        output_queue = Queue()
        
        def enqueue_output(out, queue):
            """Read lines from out and put them in the queue."""
            try:
                for line in iter(out.readline, b''):
                    queue.put(line)
            except ValueError:
                # Pipe was closed
                pass
            finally:
                out.close()
        
        # Start thread to read output
        thread = Thread(target=enqueue_output, args=(process.stdout, output_queue))
        thread.daemon = True
        thread.start()
        
        got_output = False
        
        try:
            # Process output
            while process.poll() is None or not output_queue.empty():
                try:
                    raw_output = output_queue.get(timeout=0.1)  # Small timeout to allow keyboard interrupt
                    got_output = True
                    if raw_output:
                        # Skip echoing the Python executable path lines
                        if sys.executable.encode() in raw_output:
                            continue
                        # Write raw bytes directly to stdout to preserve ANSI coloring
                        try:
                            sys.stdout.buffer.write(raw_output)
                            sys.stdout.buffer.flush()
                        except Exception:
                            # Fallback to text write if buffer isn't available
                            sys.stdout.write(raw_output.decode('utf-8', errors='replace'))
                            sys.stdout.flush()
                except Empty:
                    # No output yet, wait a bit
                    time.sleep(0.01)
        except KeyboardInterrupt:
            # Let the signal handler take care of cleanup
            raise
        
        # Get the return code
        return_code = process.wait()
        
        # Ensure output thread is done
        if output_thread is not None and output_thread.is_alive():
            output_thread.join(timeout=0.5)
            
        return return_code
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Command interrupted by user[/]")
        return_code = 130  # Standard exit code for SIGINT
    except TimeoutExpired:
        console.print("\n[red]Error: Command timed out[/]")
        console.print("[yellow]The command took too long to execute. Please check for any hanging processes.[/]")
        return_code = 124  # Standard exit code for timeout
    except FileNotFoundError as e:
        console.print(f"\n[red]Error: Command not found: {e.filename}[/]")
        console.print("[yellow]Please check if the command is installed and in your PATH.[/]")
        return_code = 127  # Command not found
    except PermissionError as e:
        console.print(f"\n[red]Error: Permission denied: {e.filename}[/]")
        console.print("[yellow]Please check if you have the necessary permissions to execute this command.[/]")
        return_code = 126  # Permission denied
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/]")
        console.print("[yellow]Please report this issue with the following details:[/]")
        console.print(f"- Command: {cmd_str if 'cmd_str' in locals() else cmd}")
        console.print(f"- Python: {sys.version}")
        console.print(f"- Platform: {sys.platform}")
        return_code = 1
    finally:
        # Always clean up resources
        try:
            stop_event.set()
            process_finished.set()
            
            # Ensure process is terminated
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except (TimeoutExpired, OSError):
                    try:
                        process.kill()
                    except:
                        pass
            
            # Restore the original signal handler
            if 'original_sigint' in locals():
                signal.signal(signal.SIGINT, original_sigint)
                
            # Ensure all threads are stopped
            if loading_thread and loading_thread.is_alive():
                loading_thread.join(timeout=0.5)
                
            if output_thread and output_thread.is_alive():
                output_thread.join(timeout=0.5)
                
            return return_code if 'return_code' in locals() else 1
        except Exception as e:
            console.print(f"[yellow]Warning: Error during cleanup: {e}[/]")
            return 1
            signal.signal(signal.SIGINT, original_sigint)

def execute_command(command: str, args: List[str], run_as_module: bool = False) -> int:
    """Execute a command with the best available method.
    
    Args:
        command: The command or module to execute
        args: Arguments to pass to the command
        run_as_module: If True, run as a Python module (python -m)
    """
    # List of commands that should be run directly without trying -m
    direct_commands = {'dars', 'black', 'pylint', 'mypy'}
    
    # If running as module
    if run_as_module:
        python_cmd = [sys.executable, "-m", command] + args
        return run_command(python_cmd)
    
    # Try direct execution first (for commands in PATH)
    if command in direct_commands or command.endswith(('.py', '.exe')):
        return run_command([command] + args)
    
    # Try direct execution first for all commands
    rc = run_command([command] + args)
    if rc == 0:
        return rc
    
    # For Python files
    if command.endswith('.py'):
        return run_command([sys.executable, command] + args)
    
    # Try with Python module as fallback if not already tried
    python_cmd = [sys.executable, "-m", command] + args
    rc = run_command(python_cmd)
    if rc == 0:
        return rc
    
    # Try with shell as last resort
    shell_cmd = " ".join([command] + args)
    return run_command(shell_cmd, shell=True)

def main():
    """Entry point for the pydx command with rich output."""
    # Parse command line arguments
    run_as_module = False
    args = sys.argv[1:]  # Skip script name
    
    # Check for -m/--module flag
    if args and args[0] in ('-m', '--module'):
        if len(args) < 2:
            console.print("[error]Error: No module specified after -m/--module[/]")
            sys.exit(1)
        run_as_module = True
        command = args[1]
        args = args[2:]
    elif args and args[0] in ('-h', '--help'):
        show_help()
        sys.exit(0)
    elif not args:
        show_help()
        sys.exit(1)
    else:
        command = args[0]
        args = args[1:]
    
    # Show help if no command provided
    if not command:
        show_help()
        sys.exit(1)
    
    # Execute the command directly without spinner
    rc = execute_command(command, args, run_as_module)
    
    sys.exit(rc if rc is not None else 0)

def show_help():
    """Show help message."""
    console.print("[info]PyDM eXecute (pydepx) - Run Python tools and scripts[/]")
    console.print("\n[info]Usage:[/] pydepx [options] <command> [args...]")
    console.print("\n[info]Options:[/]")
    console.print("  -m, --module    Run a module as a script (like python -m)")
    console.print("  -h, --help      Show this help message and exit")
    console.print("\n[info]Examples:[/]")
    console.print("  pydepx black .                     # Run black formatter")
    console.print("  pydepx -m http.server 8000        # Run HTTP server module")
    console.print("  pydepx -m pytest tests/           # Run tests with pytest")
    console.print("  pydepx -m pip install package     # Install a package")
    console.print("  pydepx -m http.server --bind 127.0.0.1 8000  # With args")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Execution interrupted by user")
        sys.exit(1)
