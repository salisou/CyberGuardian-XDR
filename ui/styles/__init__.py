from pathlib import Path
def load_stylesheet(): return (Path(__file__).with_name('dark_theme.qss')).read_text(encoding='utf-8')
