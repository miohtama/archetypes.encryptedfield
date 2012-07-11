.. contents::

Introduction
============

Provide symmetrical value encryption for Archetypes field.

Field value is stored encrypted in Data.fs.

- Encryption key is stored separately from the database

- Partially make your data harder to access e.g. social security number

- Database is safe to hand to third party

- When data is handed to the third party and the encryption key is not available then display a placeholder
  message instead of the encryption value

Support Archetypes. Dexterity support availabl

Installation
==============

- Add ``archetypes.encryptedfield`` to your eggs in buildout.cfg

- Install in Add/remove add-ons

In your Archetypes schema code you can then use::

    your_schema = Schema((
            EncryptedField("testField"),
    ))


Internals
===========

Provide EncryptionField Archetypes field and matching EncryptoinWidget.

Save encrypted values in the database using AES encryption. String values are padded to 16-bytes AES
boundary using a padding character ``{``. The padding character cannot be contained in the value.

By default, the encrypted key is read from an environment variable, but different ``IKeyProvider`` can be used.

There is special right check for saving the encrypted values. Decryption is always possible,
but if you do not have encryption rights the value will come out as "XXXX" from the field.

None and empty string values are specially handled and never encrypted. Saving None does not require the encryption key.

Widget behavior
================

All users will see the encrypted data widgets regardless whether they have permission to decrypt it or not.
EncryptionWidget will show "XXX" and disable text input if the user does not have permission to access the value.

The "XXX" and other custom error messages what will be shown can be customed on the field properites::

        'msg_cannot_crypt': u"Decryption is not available",
        'msg_bad_key': u"Decryption key does not match data",
        "msg_decrypt_filler": u"XXXXX",

Encryption
============

Encryption is done using AES of `PyCrypto <http://pypi.python.org/pypi/pycrypto/>`_ library.

Author
========

`Mikko Ohtamaa <http://opensourcehacker.com>`_

