import os
import pytest
from .utils import Notebook

def get_cells_contents(nb):
    JS = 'return Jupyter.notebook.get_cells().map(function(c) {return c.get_text();})'
    return nb.browser.execute_script(JS)

def set_cell_metadata(nb, index, key, value):
    JS = 'Jupyter.notebook.get_cell({}).metadata.{} = {}'.format(index, key, value)
    return nb.browser.execute_script(JS)

def cell_is_deletable(nb, index):
    JS = 'return Jupyter.notebook.get_cell({}).is_deletable();'.format(index)
    return nb.browser.execute_script(JS)

def delete_cell(notebook, index):
    notebook.focus_cell(index)
    notebook.to_command_mode
    notebook.current_cell.send_keys('dd')

def test_delete_cells(notebook):
    print('testing deleteable cells')
    a = 'print("a")'
    b = 'print("b")'
    c = 'print("c")'

    notebook.edit_cell(index=0, content=a)
    notebook.append(b, c)
    notebook.to_command_mode()
    
    # Validate initial state
    assert get_cells_contents(notebook) == [a, b, c]
    for cell in range(0, 3):
        assert cell_is_deletable(notebook, cell)

    set_cell_metadata(notebook, 0, 'deletable', 'false')
    set_cell_metadata(notebook, 1, 'deletable', 0
    )   
    assert not cell_is_deletable(notebook, 0)
    assert cell_is_deletable(notebook, 1)
    assert cell_is_deletable(notebook, 2)
    
    # Try to delete cell a (should not be deleted)
    delete_cell(notebook, 0)
    assert get_cells_contents(notebook) == [a, b, c]

    # Try to delete cell b (should succeed)
    delete_cell(notebook, 1)
    assert get_cells_contents(notebook) == [a, c]

    # Try to delete cell c
    delete_cell(notebook, 1)
    assert get_cells_contents(notebook) == [a]

    # Change the deletable state of cell a
    set_cell_metadata(notebook, 0, 'deletable', 'true')

    # Try to delete cell a (should succeed)
    delete_cell(notebook, 0)
    assert len(notebook.cells) == 1 # it contains an empty cell

    # Make sure copied cells are deletable
    notebook.edit_cell(index=0, content=a)
    set_cell_metadata(notebook, 0, 'deletable', 'false')
    assert not cell_is_deletable(notebook, 0)
    notebook.to_command_mode()
    notebook.current_cell.send_keys('cv')
    assert len(notebook.cells) == 2
    assert cell_is_deletable(notebook, 1)

# NOTE: APIs that will be useful for testing
# http://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.common.action_chains
