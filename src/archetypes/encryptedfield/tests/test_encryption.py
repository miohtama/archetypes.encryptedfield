import os
import unittest2 as unittest


from archetypes.encryptedfield.testing import\
    ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

from archetypes.encryptedfield import encryption
from archetypes.encryptedfield.field import EncryptedField, CannotSaveError
from archetypes.encryptedfield.envkey import EnvironKeyProvider


from Products.Archetypes.tests.utils import mkDummyInContext
from Products.Archetypes.atapi import Schema, BaseContentMixin


class TestEncrypt(unittest.TestCase):

    layer = ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        self.key = "foobar"

    def test_encrypt(self):
        encryption.encrypt_value(u"Foobar", self.key)

    def test_decrypt(self):
        value = u"Foobar"
        encrypted = encryption.encrypt_value(value, self.key)
        decrypted = encryption.decrypt_value(encrypted, self.key)
        self.assertEqual(value, decrypted)

    def test_encrypt_not_unicode(self):
        try:
            encryption.encrypt_value("bytestring", self.key)
            raise AssertionError("Should not be reached")
        except RuntimeError:
            pass

    def test_decrypt_bad_key(self):
        value = u"Foobar"
        encrypted = encryption.encrypt_value(value, self.key)
        decrypted = encryption.decrypt_value(encrypted, "xxxx")
        self.assertEqual(decrypted, None)

TEST_SCHEMA = Schema((
        EncryptedField("testField"),
))


class Dummy(BaseContentMixin):
    def Title(self):
        # required for ImageField
        return 'Spam'


class NotAllowedProvider(EnvironKeyProvider):
    """
    Test that the user cannot decrypt fields and we should get XXX output.
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

        portal = self.layer["portal"]

        self.dummy = mkDummyInContext(Dummy, oid='dummy', context=portal, schema=self.schema)

    def test_encrypt(self):
        field = self.schema["testField"]
        field.set(self.dummy, "foobar")

    def test_encrypt_no_key(self):
        field = self.schema["testField"]
        del os.environ["DATA_ENCRYPTION_SECRET"]
        try:
            field.set(self.dummy, "foobar")
            raise AssertionError("Should not be reached")
        except CannotSaveError:
            pass

    def test_decrypt(self):
        value = u"Foobar"
        field = self.schema["testField"]
        field.set(self.dummy, value)
        decrypted = field.get(self.dummy)
        self.assertEqual(value, decrypted)

    def test_decrypt_none(self):
        value = None
        field = self.schema["testField"]
        field.set(self.dummy, value)
        decrypted = field.get(self.dummy)
        self.assertEqual(value, decrypted)

    def test_decrypt_empty(self):
        value = ""
        field = self.schema["testField"]
        field.set(self.dummy, value)
        decrypted = field.get(self.dummy)
        self.assertEqual(value, decrypted)

    def test_decrypt_no_key(self):
        value = ""
        field = self.schema["testField"]
        field.set(self.dummy, value)
        del os.environ["DATA_ENCRYPTION_SECRET"]
        decrypted = field.get(self.dummy)
        self.assertEqual(decrypted, field.msg_cannot_crypt)

    def test_decrypt_corrupted_data(self):
        self.dummy.testField = "35938503"
        field = self.schema["testField"]
        decrypted = field.get(self.dummy)
        self.assertEqual(decrypted, field.msg_bad_key)


class TestDecryptionNotAllowed(unittest.TestCase):
    """
    See the different cases when user has no decryption priviledge.
    """
    layer = ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        self.key = "foobar"
        os.environ["DATA_ENCRYPTION_SECRET"] = self.key

        self.schema = TEST_SCHEMA.copy()
        self.schema["testField"].key_provider = NotAllowedProvider

        portal = self.layer["portal"]

        self.dummy = mkDummyInContext(Dummy, oid='dummy', context=portal, schema=self.schema)

    def test_decrypt(self):
        """ No priviledges -> value should come out as XXX"""
        field = self.schema["testField"]

        # Set priviledge to save
        self.schema["testField"].key_provider = EnvironKeyProvider
        field.set(self.dummy, "foobar")
        self.schema["testField"].key_provider = NotAllowedProvider
        decrypted = field.get(self.dummy)

        # Assert is xxx
        self.assertEqual(decrypted, self.schema["testField"].msg_decrypt_filler)

    def test_save_widget(self):
        """ Widge should spit out empty marker instead of actual value if no save priviledge """
        doc = self.dummy
        field = doc.Schema()['testField']
        widget = field.widget

        self.assertTrue(widget.isDisabled(doc))

        form = {'testField': 'xxxxx'}
        marker = {}
        result = widget.process_form(doc, field, form, empty_marker=marker)

        # We should get empty marker here
        expected = marker, {}
        self.assertEqual(expected, result)

    def test_save_field(self):
        doc = self.dummy
        field = doc.Schema()['testField']
        try:
            field.set(doc, "foobar")
            raise AssertionError("Should not be reached")
        except CannotSaveError:
            pass
