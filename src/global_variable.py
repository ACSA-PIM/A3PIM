# https://github.com/doudoudzj/python-global-variable

def _init():
    """在主模块初始化"""
    global GLOBALS_DICT
    GLOBALS_DICT = {}

def _set(name, value):
    """设置"""
    try:
        GLOBALS_DICT[name] = value
        return True
    except KeyError:
        return False

def _get(name):
    """取值"""
    try:
        return GLOBALS_DICT[name]
    except KeyError:
        return "Not Found"