
import re
import yaml
import os

def find_secrets(target, input_file, output_file):
    with open("config/patterns.yaml", "r") as f:
        patterns = yaml.safe_load(f)
    secrets = []
    try:
        with open(input_file, "r") as f:
            content = f.read()
        for key, pattern in patterns["patterns"].items():
            matches = re.findall(pattern, content)
            secrets.extend([f"{key}: {match}" for match in matches])
        with open(output_file, "w") as f:
            f.write("\n".join(secrets))
        return secrets, ""
    except Exception as e:
        return [], str(e)