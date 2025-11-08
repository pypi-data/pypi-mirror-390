============
walkremove
============

.. automodule:: python_plugins.ospath

.. code-block:: python

    from  python_plugins.ospath.walk import remove
    from  python_plugins.ospath.walk import remove_pycache
    from  python_plugins.ospath.walk import remove_ipynb_checkpoints

    remove(dir_path,rm_dir_name)
    
    remove_pycache()   # default is "."
    
    remove_pycache("./tests")

    