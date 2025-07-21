def validate_target(target):
    return "." in target and not target.startswith(".")
