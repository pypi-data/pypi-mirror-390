# SPDX-FileCopyrightText: 2025-present Anton Popov <a.popov.fizteh@gmail.com>
#
# SPDX-License-Identifier: MIT

def is_jupyter():
    "Check environment"
    try:
        # Check if we're in IPython/Jupyter
        from IPython import get_ipython
        if get_ipython() is None:
            return False
        # Check if it's a Jupyter notebook/lab
        if 'IPKernelApp' in get_ipython().config:
            return True
        # Alternative check
        if hasattr(get_ipython(), 'kernel'):
            return True
        return False
    except ImportError:
        return False
    
def dispmay_item(item_to_display: object) -> None:
    if is_jupyter():
        display(item_to_display)
    else:
        print(item_to_display)