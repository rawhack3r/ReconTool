import pytest
from core.error_handler import ErrorHandler, ErrorLevel, ErrorType

def test_error_handling():
    handler = ErrorHandler()
    error = handler.handle("TestTool", "Test error", "TestPhase", 
                          ErrorLevel.ERROR, ErrorType.API, True)
    assert "id" in error
    assert handler.errors
    
    report = handler.generate_error_report("test.com")
    assert "total_errors" in report
    assert report["total_errors"] == 1