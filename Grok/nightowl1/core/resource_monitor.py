import psutil

class ResourceMonitor:
    @staticmethod
    def get_resources():
        return {
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'network': psutil.net_io_counters().bytes_sent / 1024
        }