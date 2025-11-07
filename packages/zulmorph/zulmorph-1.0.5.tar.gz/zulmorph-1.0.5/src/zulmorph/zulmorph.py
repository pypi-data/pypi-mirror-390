from foma import FST
import re
from importlib import resources

PKG_NAME = "zulmorph"
RES_LOC = "res"
FST_NAME = 'zul.fom'
MAX_ANALYSES = 30

def _fix_notation(analysis):
    stem_class_pattern = re.compile(r"\.([0-9a]+(-[0-9a]+)?)")
    stem_class_matches = re.finditer(stem_class_pattern,analysis)
    for m in stem_class_matches:
        m_group_0 = m.group(0)
        m_group_1 = m.group(1)
        analysis = analysis.replace(m_group_0,f"[{m_group_1}]")
    
    return analysis

def _sort_analyses(token_analyses : list):
    """Sort analyses by number of tags."""

    tag_pattern = re.compile(r'((\[[a-zA-Z0-9-]+\])+)')
    token_analyses_counted = []
    for ta in token_analyses:
        ta = _fix_notation(ta)
        tags = re.findall(tag_pattern,ta)
        token_analyses_counted.append((ta,len(tags)))
    
    ta_sorted = sorted(token_analyses_counted,key=lambda x: x[1])
    return [ta for (ta,tags) in ta_sorted]

def analyse_token(token : str,fst : FST = None):
    """Produce list of analyses of 'token'"""

    if not fst:
        with resources.files(f'{PKG_NAME}.{RES_LOC}').joinpath(FST_NAME) as fp:
            fst = load_fst(fp)

    a_iter = fst.apply_up(token)
    a_list = []

    while len(a_list) < MAX_ANALYSES:
        try:
            a = next(a_iter)
            a_list.append(a)
        except StopIteration:
            break
    
    return _sort_analyses(a_list)

def analyse_tokens(tokens : list, fst : FST = None):
    """Analyse a list of tokens using specified (or default) FOMA fst and gather results into a dict."""
    analyses = {}
    for t in tokens:
        if not t in analyses.keys():
            t_analyses = analyse_token(t,fst)
            analyses[t] = t_analyses
    return analyses

def load_fst(fst_path : str):
    """Load a FOMA fst."""
    return FST.load(fst_path)
    
