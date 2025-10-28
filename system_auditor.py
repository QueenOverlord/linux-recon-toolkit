import subprocess
import datetime

def run_command(command: list, show_error: bool = True) -> str | None:
    """
    Executes a shell command and returns its stdout.
    Handles errors gracefully. Can suppress error messages.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return result.stdout.strip()
    except FileNotFoundError:
        if show_error:
            print(f"❌ Error: Command not found: '{command[0]}'")
        return None
    except subprocess.CalledProcessError as e:
        if show_error:
            print(f"❌ Error executing command: '{' '.join(command)}'")
            # Only show stderr if it contains something
            if e.stderr:
                print(f"   Stderr: {e.stderr.strip()}")
        return None
    except subprocess.TimeoutExpired:
        if show_error:
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

def get_listening_ports() -> str | None:
    """
    Finds all TCP/UDP ports in a listening state and the processes using them.
    """
    print("ℹ️  Scanning for listening ports (ss -tulpn)...")
    
    # ss = socket statistics. 
    # -t = tcp, -u = udp, -l = listening, -p = processes, -n = numeric
    command = ['ss', '-tulpn']
    
    output = run_command(command)
    
    if output is None:
        return None # The command failed entirely.
        
    header = "--- Listening Ports ---"
    
    # The output of 'ss' has a header line. We need to skip it.
    lines = output.strip().split('\n')
    
    # If there's only the header or less, no ports are listening.
    if len(lines) <= 1:
        return f"{header}\nNo listening ports found.\n"
        
    parsed_ports = []
    # We start the loop from the second line to skip the header
    for line in lines[1:]:
        # ss output can have variable whitespace. Split handles this.
        parts = line.split()
        
        # We expect at least 5 columns for a valid listening port line
        if len(parts) >= 5:
            local_address_port = parts[4]
            process_info = parts[6] if len(parts) > 6 else 'N/A'
            
            # Clean up the process info string like 'users:(("nginx",pid=123,...))'
            process_name = process_info.split('"')[1] if '"' in process_info else 'N/A'
            
            parsed_ports.append(f"  - Port: {local_address_port} | Process: {process_name}")

    if not parsed_ports:
        return f"{header}\nNo listening ports found.\n"

    # Join the list of parsed ports into a single string with newlines
    report_body = "\n".join(parsed_ports)
    return f"{header}\n{report_body}\n"

def check_cloud_metadata() -> str:
    """
    Checks if the machine has access to a standard cloud metadata service.
    """
    print("ℹ️  Checking for cloud metadata service...")
    
    # 169.254.169.254 is a non-routable IP used by cloud providers (AWS, GCP, Azure)
    # for instance metadata.
    # -s = silent, --connect-timeout 1 = fail after 1 second.
    command = [
        'curl', 
        '-s', 
        '--connect-timeout', 
        '1', 
        'http://169.254.169.254/latest/meta-data/'
    ]
    
    output = run_command(command, show_error=False)

    
    header = "--- Cloud Instance Check ---"
    
    # the run_command returns None on failure (timeout, error, etc.)
    if output is not None and output != "":
        # Success means the service is accessible.
        report_body = "✅ Cloud metadata service is accessible. This machine is likely a cloud instance."
    else:
        # Failure (timeout or other error) means the service is not there.
        report_body = "ℹ️ Cloud metadata service not found. This is likely not a standard cloud instance."
        
    return f"{header}\n{report_body}\n"

def main():
    """
    Main function to orchestrate the audit and generate the report.
    """
    print("🚀 Starting System Audit...")
    
    # 1. GATHER DATA
    # Create a list of all the report sections from our audit functions.
    report_parts = [
        get_active_users(),
        get_last_logins(),
        get_listening_ports(),
        check_cloud_metadata()
    ]
    
    # Filter out any 'None' results from failed functions
    valid_report_parts = [part for part in report_parts if part is not None]
    
    # 2. ASSEMBLE THE REPORT
    # Generate a timestamp for the report header and filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_header = f"System Security Audit Report\nGenerated on: {timestamp}\n"
    report_body = "\n".join(valid_report_parts)
    
    full_report = f"{report_header}\n{'-'*40}\n\n{report_body}"
    
    # 3. DELIVER THE REPORT
    # Create a unique filename with a timestamp
    filename_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"security_report_{filename_timestamp}.txt"
    
    try:
        with open(filename, 'w') as f:
            f.write(full_report)
        print(f"✅ Report generated successfully: {filename}")
    except IOError as e:
        print(f"❌ Critical Error: Could not write report to file: {e}")

# --- FINAL EXECUTION BLOCK ---
if __name__ == "__main__":
    main()

