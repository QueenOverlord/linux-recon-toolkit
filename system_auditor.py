import subprocess
import datetime

def run_command(command: list) -> str | None:
    """
    Executes a shell command and returns its stdout.
    Handles errors gracefully.
    """
    try:
        # Execute the command
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True,
            timeout=10  # Added a timeout for safety
        )
        # Return the standard output if successful
        return result.stdout.strip()
    except FileNotFoundError:
        print(f"❌ Error: Command not found: '{command[0]}'")
        return None
    except subprocess.CalledProcessError as e:
        # This catches errors if the command returns a non-zero exit code
        print(f"❌ Error executing command: '{' '.join(command)}'")
        print(f"   Stderr: {e.stderr.strip()}")
        return None
    except subprocess.TimeoutExpired:
        print(f"❌ Error: Command timed out: '{' '.join(command)}'")
        return None

def get_active_users() -> str | None:
    """
    Checks for actively logged-in users.
    """
    print("ℹ️  Checking for active users...")
    
    # Define the command to be executed
    command = ['who']
    
    # Use our robust wrapper to run the command
    output = run_command(command)
    
    # If the command failed, output will be None. We return None to the caller.
    if output is None:
        return None
        
    # If the command succeeded, format the output for the report
    header = "--- Active Users ---"
    
    # If there are no users, 'who' returns an empty string. Handle that case.
    if not output:
        report_section = f"{header}\nNo active users found.\n"
    else:
        report_section = f"{header}\n{output}\n"
        
    return report_section

def get_last_logins() -> str | None:
    """
    Retrieves the last 10 login records.
    """
    print("ℹ️  Retrieving last 10 logins...")
    
    # The 'last' command shows login history. '-n 10' limits it to 10 lines.
    command = ['last', '-n', '10']
    
    output = run_command(command)
    
    # The same safety check as before.
    if output is None:
        return None
        
    header = "--- Last 10 Logins ---"
    
    # The 'last' command is unlikely to be empty, but this is good practice.
    if not output:
        report_section = f"{header}\nNo login history found.\n"
    else:
        report_section = f"{header}\n{output}\n"
        
    return report_section

# This line should be at the very end of your auditor.py file.
# Make sure it is not indented.

if __name__ == "__main__":
    print("--- Running Sanity Checks ---")
    print("="*30) # A separator for visual clarity

    # --- Test 1: Get Active Users ---
    active_users_report = get_active_users()
    
    # Check if the function returned a report string or None (an error)
    if active_users_report:
        print(active_users_report)
    else:
        print("❌ get_active_users() failed to produce a report.\n")

    # --- Test 2: Get Last Logins ---
    last_logins_report = get_last_logins()
    
    if last_logins_report:
        print(last_logins_report)
    else:
        print("❌ get_last_logins() failed to produce a report.\n")

    print("="*30)
    print("--- Sanity Checks Complete ---")

