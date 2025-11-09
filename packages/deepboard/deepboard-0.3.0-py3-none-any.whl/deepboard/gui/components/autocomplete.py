from typing import *
from fasthtml.common import *

def AutoCompleteInput(id: str, suggestions: List[str] = None, placeholder: str = "placeholder", value: str = "",
                      return_suggestions: bool = False, oob: bool = False):
    if suggestions is None:
        suggestions = []
    suggestion_component = Div(*[
            Div(suggestion,
                hx_get=f"/autocomplete/tags?id={id}&placeholder={placeholder}&eventType=clicked&search={suggestion}",
                hx_trigger="mousedown",
                hx_target="#experiment-table",
                cls='autocomplete-suggestion-item')
        for suggestion in suggestions
        ],
            cls="autocomplete-suggestions" + (' hidden' if len(suggestions) == 0 else ''),
            id=f'{id}-suggestions',
            hx_swap_oob="true" if oob and return_suggestions else None,
            ),
    if return_suggestions:
        return suggestion_component
    else:
        return Div(
            Input(type='text',
                  id=f'{id}-search',
                  placeholder=placeholder,
                  name='search',
                  value=value,
                  autocomplete="off",
                  hx_get=f"/autocomplete/tags?id={id}&placeholder={placeholder}",
                  hx_trigger="focus, keyup[key=='Enter'], keyup changed delay:300ms, blur delay:200ms", #
                  hx_vals=f'''js:{{
                    search: document.getElementById("{id}-search").value,
                    eventType: event.type,
                    eventKey: event.key
                  }}''',
                  onkeydown=f"if(event.key === 'Enter') setTimeout(() => {{document.getElementById('{f'{id}-search'}').blur();}}, 100);",
                  cls="autocomplete-input"),
            suggestion_component,
            cls=f"autocomplete {value}",
            id=f"{id}",
            hx_swap_oob="true" if oob else None
        )
