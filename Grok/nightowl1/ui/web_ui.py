from flask import Flask, render_template
from core.resource_monitor import ResourceMonitor
from core.orchestrator import NightOwlOrchestrator
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    resources = ResourceMonitor.get_resources()
    with open("nightowl_state.json", "r") as f:
        state = json.load(f)
    return render_template('dashboard.html', resources=resources, state=state)

if __name__ == '__main__':
    app.run(debug=True)