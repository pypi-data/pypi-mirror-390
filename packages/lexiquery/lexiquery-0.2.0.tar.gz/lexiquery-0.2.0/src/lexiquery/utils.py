import re
def replace_symbols_with_space(s: str) -> str:
    pattern = re.compile(r'[^\w\s]')
    return pattern.sub(' ', s).replace('_', ' ')

def default_pre_clean(s: str) -> str:
    return replace_symbols_with_space(s).lower()

def build_index(text: str):
    idx = {}
    for pos, token in enumerate(text.split()):
        idx.setdefault(token, []).append(pos)
    return idx
