import yaml

def load_tools():
    with open("configs/tools.yaml", "r") as f:
        return yaml.safe_load(f)["tools"]
