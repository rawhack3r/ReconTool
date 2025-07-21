import yaml
import os

def load_tools_yaml(path="configs/tools.yaml"):
    if not os.path.exists(path):
        print(f"[⚠️] tools.yaml not found at: {path}")
        return []

    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return data.get("tools", [])
    except yaml.YAMLError as e:
        print(f"[❌] YAML error in tools.yaml: {e}")
    except Exception as e:
        print(f"[❌] Unexpected error loading tools.yaml: {e}")
    return []
