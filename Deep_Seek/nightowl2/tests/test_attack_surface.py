import pytest
from core.attack_surface import AttackSurfaceMapper

def test_attack_surface_mapping():
    mapper = AttackSurfaceMapper()
    mapper.add_node("web1", "Web Server", {"risk": 70})
    mapper.add_node("db1", "Database", {"risk": 90})
    mapper.add_edge("web1", "db1", "Database Connection", 5)
    
    surface_map = mapper.generate_interactive_map("test.com")
    assert "test.com_attack_surface.html" in surface_map
    
    risk_report = mapper.generate_risk_report("test.com")
    assert "critical_paths" in risk_report