from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

class ProgressTracker:
    def __init__(self):
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn()
        )

    def add_task(self, description, total=100):
        return self.progress.add_task(description, total=total)

    def update(self, task_id, completed):
        self.progress.update(task_id, completed=completed)

    def __enter__(self):
        self.progress.__enter__()
        return self

    def __exit__(self, *args):
        self.progress.__exit__(*args)