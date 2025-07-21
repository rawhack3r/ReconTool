import psutil
import threading
import time

class ResourceMonitor:
    def __init__(self):
        self.cpu_percent = 0
        self.mem_percent = 0
        self.network_bytes = (0, 0)
        self.monitoring = False

    def start(self):
        if not self.monitoring:
            self.monitoring = True
            threading.Thread(target=self._monitor, daemon=True).start()

    async def start_monitoring(self):
        self.start()

    def stop(self):
        self.monitoring = False

    async def stop_monitoring(self):
        self.stop()

    def _monitor(self):
        while self.monitoring:
            self.cpu_percent = psutil.cpu_percent(interval=0.5)
            self.mem_percent = psutil.virtual_memory().percent
            net = psutil.net_io_counters()
            self.network_bytes = (net.bytes_sent, net.bytes_recv)
            time.sleep(1)

    def get_usage(self):
        return {
            "cpu_percent": self.cpu_percent,
            "mem_percent": self.mem_percent,
            "network_bytes": self.network_bytes
        }

    def can_execute_tool(self):
        return self.cpu_percent < 80 and self.mem_percent < 80
