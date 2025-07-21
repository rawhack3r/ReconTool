import os
import threading
from flask import Flask, render_template, jsonify, send_from_directory
from core.orchestrator import NightOwlOrchestrator

app = Flask(__name__, static_folder='static', template_folder='templates')
orchestrator = None
dashboard_data = {
    "status": "idle",
    "progress": 0,
    "current_phase": 0,
    "phases": [],
    "tools": {},
    "resources": {
        "cpu": 0,
        "memory": 0,
        "network": "0KB/s ▼ | 0KB/s ▲"
    }
}

def start_web_interface(orchestrator_instance):
    global orchestrator
    orchestrator = orchestrator_instance
    
    # Start the orchestrator in a separate thread
    threading.Thread(target=run_scan, daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)

def run_scan():
    global dashboard_data
    try:
        dashboard_data["status"] = "running"
        orchestrator.execute_workflow()
        dashboard_data["status"] = "completed"
    except Exception as e:
        dashboard_data["status"] = f"error: {str(e)}"

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/status')
def status():
    return jsonify(dashboard_data)

@app.route('/reports/<path:filename>')
def download_report(filename):
    return send_from_directory('outputs/reports', filename)

@app.route('/start')
def start_scan():
    if orchestrator and dashboard_data['status'] == 'idle':
        threading.Thread(target=run_scan).start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already running"})

@app.route('/pause')
def pause_scan():
    # Implement pause functionality
    return jsonify({"status": "paused"})

@app.route('/resume')
def resume_scan():
    # Implement resume functionality
    return jsonify({"status": "resumed"})

@app.route('/stop')
def stop_scan():
    # Implement stop functionality
    return jsonify({"status": "stopped"})