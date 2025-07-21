import subprocess
import os
import sys
from pathlib import Path

# Attempt to import ErrorHandler from core; fallback to basic logging if not found
try:
    from core.error_handler import ErrorHandler
    error_handler = ErrorHandler()
except ModuleNotFoundError:
    import logging
    logging.basicConfig(level=logging.ERROR)
    error_handler = logging
    error_handler.error = error_handler.error  # Ensure compatibility with expected method

def run_findomain(target, output_dir="output"):
    """
    Run findomain for subdomain enumeration and save results to a custom output file.
    
    Args:
        target (str): The target domain (e.g., swiggy.com).
        output_dir (str): Directory to store the output file (default: 'output').
    
    Returns:
        str: Path to the output file, or None if execution fails.
    """
    try:
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Construct findomain command
        command = ["findomain", "--target", target, "-o"]
        
        # Run findomain
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Default output file created by findomain is <target>.txt
        default_output = f"{target}.txt"
        desired_output = os.path.join(output_dir, f"findomain_{target}.txt")
        
        # Check if default output file exists and rename it
        if os.path.exists(default_output):
            os.rename(default_output, desired_output)
            error_handler.info(f"Findomain output saved to {desired_output}")
            return desired_output
        else:
            error_handler.error(f"Findomain did not create output file: {default_output}")
            return None
            
    except subprocess.CalledProcessError as e:
        error_handler.error(f"Findomain execution failed: {e.stderr}")
        return None
    except FileNotFoundError:
        error_handler.error("Findomain binary not found. Please ensure it is installed and in PATH.")
        return None
    except Exception as e:
        error_handler.error(f"Unexpected error in findomain_wrapper: {str(e)}")
        return None

def main():
    # Example entry point for testing the script standalone
    if len(sys.argv) < 2:
        print("Usage: python3 findomain_wrapper.py <target>")
        sys.exit(1)
    
    target = sys.argv[1]
    result = run_findomain(target)
    if result:
        print(f"Subdomain enumeration completed. Output saved to: {result}")
    else:
        print("Subdomain enumeration failed. Check logs for details.")

if __name__ == "__main__":
    main()
