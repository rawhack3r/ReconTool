# core/resource_monitor.py

import threading
import time
import psutil


class ResourceMonitor:
    def __init__(self):
        self._lock = threading.Lock()
        self.running = False
        self.cpu_percent = 0
        self.memory_percent = 0
        self.network_mb = 0
        self._last_net = psutil.net_io_counters()

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._collect, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        self._thread.join(timeout=1)

    def _collect(self):
        while self.running:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            net = psutil.net_io_counters()
            sent = net.bytes_sent - self._last_net.bytes_sent
            recv = net.bytes_recv - self._last_net.bytes_recv
            self._last_net = net
            with self._lock:
                self.cpu_percent = cpu
                self.memory_percent = mem
                self.network_mb = (sent + recv) / 1024 / 1024
            time.sleep(1)

    def get_usage(self):
        with self._lock:
            return {
                "cpu_percent": self.cpu_percent,
                "memory_percent": self.memory_percent,
                "network_mb": self.network_mb,
            }
