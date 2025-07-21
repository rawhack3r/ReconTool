def calculate_completion_ratio(completed, total):
    return round((completed / total) * 100, 2) if total else 0

def completion_msg(completed, total):
    percent = calculate_completion_ratio(completed, total)
    icon = "🚀" if percent == 100 else "⏳"
    return f"{icon} {percent}% Completed ({completed}/{total})"
