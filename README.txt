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

Internals
===========

Provide EncryptionField Archetypes field.

Save encrypted values in the database using AES encryption.

By default, the encrypted key is read from an environment variable, but different ``IKeyProvider`` can be used.

There is special right check for saving the encrypted values. Decryption is always possible,
but if you do not have encryption rights the value will come out as "XXXX" from the field.

None and empty string values are specially handled and never encrypted.