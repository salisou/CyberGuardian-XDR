from core.threat_score import ThreatInputs, calculate_threat_score

def test_clean_system():
    result = calculate_threat_score(ThreatInputs())
    assert result.score == 0 and result.level == 'LOW'

def test_score_is_capped():
    result = calculate_threat_score(ThreatInputs(cpu_percent=99, memory_percent=99, open_connections=900, suspicious_processes=10, system_errors=20))
    assert result.score == 100 and result.level == 'HIGH'

def test_connection_indicator():
    result = calculate_threat_score(ThreatInputs(open_connections=200))
    assert result.score == 10
