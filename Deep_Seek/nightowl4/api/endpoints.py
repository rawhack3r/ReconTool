from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import asyncio
from core.orchestrator import NightOwlOrchestrator
from core.dashboard import NightOwlDashboard

app = FastAPI(
    title="NightOwl Recon API",
    description="REST API for NightOwl Reconnaissance Tool",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scan_status = {}

class ScanRequest(BaseModel):
    target: str
    mode: str = "light"
    target_type: str = "single"
    custom_tools: list = []

@app.post("/scan", status_code=202)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    scan_id = f"scan_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
    scan_status[scan_id] = {
        "id": scan_id,
        "target": request.target,
        "status": "queued",
        "start_time": datetime.now().isoformat()
    }
    
    background_tasks.add_task(run_scan, scan_id, request)
    return {"scan_id": scan_id, "status": "queued"}

@app.get("/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    if scan_id not in scan_status:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan_status[scan_id]

@app.get("/scan/{scan_id}/report")
async def get_scan_report(scan_id: str, report_type: str = "html"):
    if scan_id not in scan_status:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if scan_status[scan_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Scan not completed")
    
    output_dir = scan_status[scan_id]["output_dir"]
    
    if report_type == "html":
        report_path = f"{output_dir}/reports/report.html"
        return FileResponse(report_path, media_type="text/html")
    elif report_type == "pdf":
        report_path = f"{output_dir}/reports/report.pdf"
        return FileResponse(report_path, media_type="application/pdf")
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

def run_scan(scan_id: str, request: ScanRequest):
    try:
        scan_status[scan_id]["status"] = "running"
        
        output_dir = f"outputs/{request.target}_{scan_id}"
        os.makedirs(output_dir, exist_ok=True)
        scan_status[scan_id]["output_dir"] = output_dir
        
        dashboard = NightOwlDashboard(verbose=True)
        dashboard.start()
        dashboard.set_target_info(request.target, request.mode, request.target_type)
        
        orchestrator = NightOwlOrchestrator(
            target=request.target,
            mode=request.mode,
            target_type=request.target_type,
            custom_tools=request.custom_tools,
            output_dir=output_dir,
            dashboard=dashboard,
            verbose=True
        )
        
        asyncio.run(orchestrator.execute_workflow())
        
        scan_status[scan_id]["status"] = "completed"
        scan_status[scan_id]["end_time"] = datetime.now().isoformat()
        scan_status[scan_id]["report_url"] = f"/scan/{scan_id}/report"
        
    except Exception as e:
        scan_status[scan_id]["status"] = "failed"
        scan_status[scan_id]["error"] = str(e)