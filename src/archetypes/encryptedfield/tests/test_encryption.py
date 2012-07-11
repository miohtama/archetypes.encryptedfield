import os
import unittest2 as unittest


from archetypes.encryptedfield.testing import\
    ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

from archetypes.encryptedfield import encryption
from archetypes.encryptedfield.field import EncryptedField, CannotSaveError
from acrhetypes.encryptedfield.envkey import EnvironKeyProvider


from Products.Archetypes.tests.utils import mkDummyInContext
from Products.Archetypes.atapi import Schema, BaseContentMixin


class TestEncrypt(unittest.TestCase):

    layer = ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        self.key = "foobar"

    def test_encrypt(self):
        encryption.encrypt(u"Foobar", self.key)

    def test_decrypt(self):
        value = u"Foobar"
        encrypted = encryption.encrypt(value, self.key)
        decrypted = encryption.decrypt(encrypted, self.key)
        self.assertEqual(value, decrypted)


TEST_SCHEMA = Schema({
        "testField": EncryptedField()
})


class Dummy(BaseContentMixin):
    def Title(self):
        # required for ImageField
        return 'Spam'


class NotAllowedProvider(EnvironKeyProvider):
    """
    Test that the user cannot decrypt fields.
    """

    def canDecrypt(field):
        """
        :return: True if the currently logged in user has decryption priviledges
        """
        return False


class TestField(unittest.TestCase):

    layer = ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        self.key = "foobar"
        os.environ["DATA_ENCRYPTION_SECRET"] = self.key

        self.schema = TEST_SCHEMA

        self.dummy = mkDummyInContext(Dummy, oid='dummy', context=self.portal, schema=self.schema)

    def test_encrypt(self):
        field = self.schema[0]
        field.set(self.dummy, "foobar")

    def test_decrypt(self):
        value = u"Foobar"
        field = self.schema[0]
        field.set(self.dummy, value)
        decrypted = field.get(self.dummy)
        self.assertEqual(value, decrypted)

    def test_decrypt_none(self):
        value = None
        field = self.schema[0]
        field.set(self.dummy, value)
        decrypted = field.get(self.dummy)
        self.assertEqual(value, decrypted)

    def test_decrypt_empty(self):
        value = ""
        field = self.schema[0]
        field.set(self.dummy, value)
        decrypted = field.get(self.dummy)
        self.assertEqual(value, decrypted)


class TestDecryptionNotAllowed(unittest.TestCase):

    layer = ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        self.key = "foobar"
        os.environ["DATA_ENCRYPTION_SECRET"] = self.key

        self.schema = TEST_SCHEMA.copy()
        self.schema[0].key_provider = NotAllowedProvider

        self.dummy = mkDummyInContext(Dummy, oid='dummy', context=self.portal, schema=self.schema)

    def test_decrypt(self):
        value = u"Foobar"
        field = self.schema[0]
        field.set(self.dummy, "foobar")
        decrypted = field.get(self.dummy)
        self.assertEqual(value, self.schema[0].msg_decrypt_filler)
