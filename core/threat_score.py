from dataclasses import dataclass

@dataclass(frozen=True)
class ThreatInputs:
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    open_connections: int = 0
    suspicious_processes: int = 0
    system_errors: int = 0

@dataclass(frozen=True)
class ThreatAssessment:
    score: int
    level: str
    reasons: tuple[str, ...]

def calculate_threat_score(data: ThreatInputs) -> ThreatAssessment:
    score, reasons = 0, []
    if data.cpu_percent >= 95: score += 15; reasons.append('CPU utilization is critically high')
    elif data.cpu_percent >= 85: score += 8; reasons.append('CPU utilization is unusually high')
    if data.memory_percent >= 95: score += 15; reasons.append('Memory utilization is critically high')
    elif data.memory_percent >= 85: score += 8; reasons.append('Memory utilization is unusually high')
    if data.open_connections >= 500: score += 20; reasons.append('Very high connection count')
    elif data.open_connections >= 200: score += 10; reasons.append('Elevated connection count')
    if data.suspicious_processes > 0:
        score += min(30, data.suspicious_processes * 10); reasons.append(f'{data.suspicious_processes} process indicator(s) require review')
    if data.system_errors > 0:
        score += min(20, data.system_errors * 2); reasons.append(f'{data.system_errors} recent system error(s)')
    score = max(0, min(100, score))
    level = 'LOW' if score <= 30 else 'MEDIUM' if score <= 70 else 'HIGH'
    return ThreatAssessment(score, level, tuple(reasons))
