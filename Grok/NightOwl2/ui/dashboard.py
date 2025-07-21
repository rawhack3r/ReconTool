
from flask import Flask
from core.ui import UI

app = Flask(__name__, template_folder="templates", static_folder="../static")

def start_dashboard(ui):
    ui.setup_routes()
    ui.start_web_server()