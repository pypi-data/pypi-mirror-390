======
crypto
======

.. autoclass:: python_plugins.crypto.cipher.AesCipher
    :members:
    :undoc-members:

.. code-block:: python

    from python_plugins.crypto import encrypt_txtfile,decrypt_txtfile

    # encrypt
    encrypt_txtfile(txtfile)
    encrypt_txtfile(txtfile,".")
    encrypt_txtfile(txtfile, encryptfile, password=password)
    
    # decrypt
    decrypt_txtfile(encryptedfile)
    decrypt_txtfile(encryptedfile,".")
    decrypt_txtfile(encryptedfile, decryptfile, password=password) 