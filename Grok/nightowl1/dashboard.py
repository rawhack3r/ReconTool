
from flask import Flask, jsonify
import os
import glob
import psutil
from datetime import datetime

# Ensure nightowl package is importable
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from core.orchestrator import NightOwlOrchestrator
except ImportError as e:
    print(f"Import error: {e}. Ensure PYTHONPATH includes /home/nightowl/1807/19/Grok/nightowl")
    sys.exit(1)

app = Flask(__name__, static_folder='static', static_url_path='/')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/status/<target>')
async def status(target):
    orchestrator = NightOwlOrchestrator(target, 'deep')
    status = {
        'phases': orchestrator.workflow.get_phases(),
        'results': orchestrator.results,
        'logs': [],
        'resources': {
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'network': psutil.net_io_counters().bytes_sent / 1024
        },
        'target': target,
        'mode': orchestrator.mode,
        'type': 'single',
        'current_tool': None
    }
    try:
        with open('logs/error.log', 'r') as f:
            status['logs'] = f.readlines()[-10:]
        for phase, data in orchestrator.results.items():
            for tool, result in data.items():
                if isinstance(result, dict) and result.get('status') == 'In Progress':
                    status['current_tool'] = {'tool': tool, 'start_time': result.get('start_time')}
                    break
    except:
        status['logs'] = ['No logs available']
    return jsonify(status)

@app.route('/api/results/<target>')
def results(target):
    results = {}
    for phase in ["Subdomain Enumeration", "Secret Finding", "Endpoint Extraction", "Vulnerability Scanning", "Cloud and IP Discovery"]:
        results[phase] = {}
        for tool_output in glob.glob(f"output/*_{target}.txt"):
            tool_name = os.path.basename(tool_output).split('_')[0]
            try:
                with open(tool_output, 'r') as f:
                    results[phase][tool_name] = f.read().splitlines()
            except:
                results[phase][tool_name] = []
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)