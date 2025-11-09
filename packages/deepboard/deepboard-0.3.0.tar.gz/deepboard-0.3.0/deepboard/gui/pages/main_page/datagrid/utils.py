from deepboard.gui.utils import smart_round, sci_round
from datetime import datetime

def format_value(value, decimals: int = 4, is_hparam: bool = False) -> str:
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    if is_hparam and (isinstance(value, float) or isinstance(value, int)):
        return sci_round(value, decimals)
    if isinstance(value, float):
        return smart_round(value, decimals)
    return value