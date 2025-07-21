class ErrorHandler:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def log_error(self, tool_name, message, target):
        with open(f"{self.output_dir}/{tool_name}_error.txt", "a") as f:
            f.write(f"[{target}] {message}\n")
