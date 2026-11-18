"""Step 5: short-term memory for scan results.

Results live only in this dictionary while the app is open.
Nothing is ever written to a file, and clear() wipes it.
"""

_results = {}

def save(results):
    """ Replace the stored results with new ones. """
    _results.clear()
    _results.update(results)
    
def get():
    """ Return a copy of the stored results (empty if nothing saved). """
    return dict(_results)
    
def clear():
    """ Forget everything. """
    _results.clear()