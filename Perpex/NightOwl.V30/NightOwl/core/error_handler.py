import logging
from pathlib import Path

def handle_errors(error_list, target, output_dir):
    err_file = Path(output_dir) / "error.log"
    with open(err_file, "w") as f:
        for err in error_list:
            f.write(f"{err['tool']}: {err['error']}\n")
    print(f"[!] Total Failures: {len(error_list)} logged in {err_file}")
