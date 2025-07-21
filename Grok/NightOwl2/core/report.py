import os
from jinja2 import Environment, FileSystemLoader

def generate_report(target, subdomains, alive, dead, important, secrets, endpoints, vulnerabilities, config):
    output_dir = config.get("general", {}).get("output_dir", "output") if config else "output"
    env = Environment(loader=FileSystemLoader("ui/templates"))
    template = env.get_template("report.html")
    os.makedirs(f"{output_dir}/reports", exist_ok=True)
    report_path = f"{output_dir}/reports/{target}_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(template.render(
            target=target,
            subdomains=subdomains,
            alive=alive,
            dead=dead,
            important=important,
            secrets=secrets,
            endpoints=endpoints,
            vulnerabilities=vulnerabilities
        ))
    return report_path