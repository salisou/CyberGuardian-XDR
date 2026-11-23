import psutil

def list_connections():
    try: connections = psutil.net_connections(kind='inet')
    except (psutil.AccessDenied, OSError): return []
    rows = []
    for item in connections:
        local = f'{item.laddr.ip}:{item.laddr.port}' if item.laddr else ''
        remote = f'{item.raddr.ip}:{item.raddr.port}' if item.raddr else ''
        rows.append({'protocol': 'TCP' if item.type == 1 else 'UDP', 'local': local,
            'remote': remote, 'status': item.status or '—', 'pid': item.pid})
    return rows
