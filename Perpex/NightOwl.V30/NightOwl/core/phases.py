import yaml

def load_profile(mode, profile_path="configs/scan_profiles.yaml"):
    try:
        with open(profile_path, "r") as f:
            data = yaml.safe_load(f)

        profile = data.get("profiles", {}).get(mode)
        if not profile:
            raise ValueError(f"Profile '{mode}' not found.")

        return profile

    except FileNotFoundError:
        print(f"[❌] Profile file '{profile_path}' not found.")
        return {"phases": []}
    except yaml.YAMLError as e:
        print(f"[❌] YAML error: {e}")
        return {"phases": []}
    except Exception as e:
        print(f"[❌] Unexpected profile error: {e}")
        return {"phases": []}
