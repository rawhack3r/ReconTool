from pathlib import Path
import subprocess
import time
import logging
from typing import Tuple, Optional


class Tool:
    def __init__(self, name: str, command: str, phase: str, output: str, parallel: bool = False):
        self.name = name
        self.command = command
        self.phase = phase
        self.output_template = output
        self.parallel = parallel

    def get_output_path(self, target: str, output_dir: Path) -> Path:
        return Path(self.output_template.format(target=target, output_dir=output_dir))

    def format_command(self, target: str, output_dir: Path) -> str:
        return self.command.format(target=target, output_dir=output_dir)

    def run(self, target: str, output_dir: Path, timeout: int = 300) -> Tuple[bool, Optional[Path], float, Optional[str]]:
        cmd = self.format_command(target, output_dir)
        out_path = self.get_output_path(target, output_dir)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        logging.info(f"Running: {self.name} | Phase: {self.phase}")
        logging.debug(f"Command: {cmd}")
        start = time.time()
        try:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            duration = round(time.time() - start, 2)

            if result.returncode == 0:
                with open(out_path, "wb") as f:
                    f.write(result.stdout)
                logging.info(f"✅ [{self.name}] Success in {duration}s → {out_path.name}")
                return True, out_path, duration, None
            else:
                error = result.stderr.decode()
                logging.error(f"❌ [{self.name}] Failed in {duration}s: {error}")
                return False, None, duration, error

        except subprocess.TimeoutExpired:
            logging.warning(f"❌ [{self.name}] Timed out after {timeout}s")
            return False, None, timeout, "Timeout"
        except Exception as e:
            logging.exception(f"[{self.name}] Crashed during execution")
            return False, None, 0, str(e)
