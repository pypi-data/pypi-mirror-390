from fasthtml.common import *

def _not_found(req, exc): return Title('Not found [404]'), Div(H1('We could not find that page :('), cls="center-center")