import logging
import os
import traceback
import sys
from datetime import datetime
from enum import Enum

class ErrorLevel(Enum):
    WARNING = 1
    ERROR = 2
    CRITICAL = 3

class ErrorType(Enum):
    DEPENDENCY = "Dependency Missing"
    TIMEOUT = "Execution Timeout"
    RESOURCE = "Resource Exhaustion"
    API = "API Failure"
    NETWORK = "Network Issue"
    UNKNOWN = "Unknown Error"

class ErrorHandler:
    def __init__(self):
        self.errors = []
        self.failed_tools = []
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(self.log_dir, "nightowl_errors.log"),
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filemode='a'
        )
        self.logger = logging.getLogger("NightOwl")
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
    
    def handle(self, tool_name, error, phase, level=ErrorLevel.ERROR, 
               error_type=ErrorType.UNKNOWN, recoverable=True, retry_count=0):
        error_id = f"{tool_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        tb = traceback.format_exc()
        
        error_data = {
            "id": error_id,
            "tool": tool_name,
            "phase": phase,
            "error": str(error),
            "type": error_type.value,
            "level": level.name,
            "recoverable": recoverable,
            "retry_count": retry_count,
            "timestamp": datetime.now().isoformat(),
            "traceback": tb
        }
        
        self.errors.append(error_data)
        
        if not recoverable:
            self.failed_tools.append(tool_name)
        
        log_message = f"[{error_type.value}] {tool_name}@{phase}: {str(error)}"
        
        if level == ErrorLevel.WARNING:
            self.logger.warning(log_message)
        elif level == ErrorLevel.ERROR:
            self.logger.error(log_message)
        else:
            self.logger.critical(log_message)
        
        if tb:
            self.logger.debug(f"Traceback:\n{tb}")
        
        return error_data
    
    def check_dependencies(self, tool_name, dependencies):
        missing = []
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        if missing:
            return self.handle(
                tool_name,
                f"Missing dependencies: {', '.join(missing)}",
                "Initialization",
                ErrorLevel.CRITICAL,
                ErrorType.DEPENDENCY,
                recoverable=False
            )
        return None
    
    def get_recoverable_errors(self):
        return [e for e in self.errors if e['recoverable']]
    
    def generate_error_report(self, target):
        report = {
            "target": target,
            "total_errors": len(self.errors),
            "critical_errors": len([e for e in self.errors if e['level'] == "CRITICAL"]),
            "recoverable_errors": len(self.get_recoverable_errors()),
            "dependency_errors": len([e for e in self.errors if e['type'] == ErrorType.DEPENDENCY.value]),
            "errors_by_phase": self._errors_by_phase(),
            "failed_tools": list(set(self.failed_tools)),
            "detailed_errors": self.errors
        }
        
        report_dir = "outputs/errors"
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"{target}_errors.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return report_path
    
    def _errors_by_phase(self):
        phases = {}
        for error in self.errors:
            phase = error['phase']
            phases.setdefault(phase, 0)
            phases[phase] += 1
        return phases
    
    def get_retry_suggestions(self):
        return [e for e in self.get_recoverable_errors() if e['retry_count'] < 3]