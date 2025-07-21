from typing import Dict
from datetime import datetime

class ProgressTracker:
    """
    Tracks progress of individual tools and overall scan phases.
    """

    def __init__(self):
        # tool_name -> progress percent (0-100)
        self.tool_progress: Dict[str, float] = {}
        # phase_name -> completed status
        self.phase_status: Dict[str, str] = {}

    def update_tool_progress(self, tool_name: str, percent: float):
        """Update progress for a tool"""
        self.tool_progress[tool_name] = min(max(percent, 0), 100)

    def get_tool_progress(self, tool_name: str) -> float:
        """Get current progress of a tool"""
        return self.tool_progress.get(tool_name, 0.0)

    def remove_tool(self, tool_name: str):
        """Remove a tool from tracking"""
        if tool_name in self.tool_progress:
            del self.tool_progress[tool_name]

    def mark_phase_complete(self, phase_name: str):
        """Mark a workflow phase complete"""
        self.phase_status[phase_name] = "completed"

    def mark_phase_in_progress(self, phase_name: str):
        """Mark a workflow phase in progress"""
        self.phase_status[phase_name] = "in_progress"

    def get_phase_status(self, phase_name: str) -> str:
        """Get current status of a phase"""
        return self.phase_status.get(phase_name, "pending")

    def overall_progress(self) -> float:
        """Calculate aggregate progress across all tools"""
        if not self.tool_progress:
            return 0.0
        return sum(self.tool_progress.values()) / len(self.tool_progress)
