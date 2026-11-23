import psutil

def list_processes():
    result = []
    attrs = ['pid', 'name', 'exe', 'username', 'status', 'cpu_percent', 'memory_percent']
    for process in psutil.process_iter(attrs=attrs, ad_value=''):
        try:
            item = process.info
            result.append({'pid': item.get('pid'), 'name': item.get('name') or 'Unknown', 'path': item.get('exe') or '',
                'user': item.get('username') or '', 'status': item.get('status') or 'Unknown',
                'cpu': float(item.get('cpu_percent') or 0), 'memory': float(item.get('memory_percent') or 0)})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): continue
    return sorted(result, key=lambda row: row['pid'] or 0)
