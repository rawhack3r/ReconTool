import json
import zlib
from pathlib import Path
from filelock import FileLock

class StateManager:
    def __init__(self, output_dir):
        self.state_file = Path(output_dir) / ".nightowl.state"
        self.lock_file = self.state_file.with_suffix(".lock")

    def save_state(self, state: dict):
        data = zlib.compress(json.dumps(state, default=str).encode())
        with FileLock(str(self.lock_file)):
            with open(self.state_file, "wb") as f:
                f.write(data)

    def load_state(self) -> dict:
        try:
            with FileLock(str(self.lock_file)):
                if not self.state_file.exists():
                    return None
                with open(self.state_file, "rb") as f:
                    data = zlib.decompress(f.read())
                    return json.loads(data)
        except Exception:
            return None
