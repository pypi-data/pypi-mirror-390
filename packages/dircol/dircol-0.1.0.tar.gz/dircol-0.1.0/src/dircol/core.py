import traceback
from inspect import ismodule, isclass, isfunction, ismethod, isbuiltin

from rich import print as rprint
from rich.columns import Columns
from rich.text import Text
from rich.style import Style

def dirc(obj):
    """Prints the result of calling dir with obj in neat 'columns' (with a title)"""
    # create the columns 
    columns = Columns(
        dir(obj),
        equal=True,
        expand=True,
        title=Text(f"\ndir({get_name(obj)})\n", style="bold")
    )  
    # print the columns
    rprint(columns)


def dirfc(obj):
    """Prints the result of calling dir with obj in neat 'fancy columns' (with a title and legends)"""
    # create styles
    style_dict = {
        'module': Style(color='blue', bold=True),
        'class': Style(color='green', bold=True),
        'method': Style(color='yellow', bold=False),
        'function': Style(color='magenta', bold=True),
        'builtin_function_or_method': Style(color='bright_black', bold=True),
        'default': Style(color='white', bold=False),
    }

    # form title and legend
    title = Text(f"\ndir({get_name(obj)})\n", style="bold")
    legend = Text('<module>', style=style_dict['module']) \
        + ' ' \
        + Text('<class>', style=style_dict['class']) \
        + ' ' \
        + Text('<method>', style=style_dict['method']) \
        + ' ' \
        + Text('<function>', style=style_dict['function']) \
        + ' ' \
        + Text('<builtin_function_or_method>', style=style_dict['builtin_function_or_method']) \
        + ' ' \
        + Text('othertype\n', style=style_dict['default'])

    title = title + legend 

    # create columns 
    columns = Columns(
        equal=True,
        expand=True,
        title=title
    )

    # stylize and add items to columns
    for item in dir(obj):
        if ismodule(getattr(obj, item)):        
            columns.add_renderable(
                Text(item, style=style_dict['module'])
            )
        elif isclass(getattr(obj, item)):        
            columns.add_renderable(
                Text(item, style=style_dict['class'])
            )
        elif ismethod(getattr(obj, item)):        
            columns.add_renderable(
                Text(item, style=style_dict['method'])
            )
        elif isfunction(getattr(obj, item)):        
            columns.add_renderable(
                Text(item, style=style_dict['function'])
            )
        elif isbuiltin(getattr(obj, item)):        
            columns.add_renderable(
                Text(item, style=style_dict['builtin_function_or_method'])
            )
        else:        
            columns.add_renderable(
                Text(item, style=style_dict['default'])
            )

    # print columns
    rprint(columns)


def get_name(var):
    _, _, _, text = traceback.extract_stack()[-3]
    return text[text.find('(')+1:-1]