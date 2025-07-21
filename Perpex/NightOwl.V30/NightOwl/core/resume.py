import json
from pathlib import Path

def save_resume_state(state_data, output_dir):
    try:
        resume_path = Path(output_dir) / "resume.json"
        with open(resume_path, "w") as f:
            json.dump(state_data, f, indent=2)
        print(f"[💾] Resume state saved to: {resume_path}")
    except Exception as e:
        print(f"[❌] Failed to save resume state: {e}")


def load_resume_state(output_dir):
    try:
        resume_path = Path(output_dir) / "resume.json"
        if resume_path.exists():
            with open(resume_path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"[❌] Could not load resume.json: {e}")
    return None
