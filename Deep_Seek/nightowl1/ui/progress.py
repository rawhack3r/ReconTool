from rich.progress import (
    Progress, 
    BarColumn, 
    TextColumn, 
    TimeRemainingColumn,
    TimeElapsedColumn
)

class NightOwlProgress(Progress):
    def __init__(self):
        super().__init__(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
            expand=True
        )
    
    def add_tool_task(self, tool_name, description):
        """Add a new task for tool execution"""
        return self.add_task(
            f"[tool]{tool_name}[/]: {description}",
            total=100
        )
    
    def update_tool_progress(self, task_id, progress, message=""):
        """Update progress for a tool task"""
        self.update(
            task_id,
            completed=progress,
            description=f"[tool]{self.tasks[task_id].fields['description'].split(':')[0]}[/]: {message}"
        )