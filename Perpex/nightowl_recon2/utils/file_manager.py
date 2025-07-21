from pathlib import Path
import json

class FileManager:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

    async def save_tool_results(self, tool_name, results):
        out_path = self.output_dir / f"{tool_name}.json"
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
