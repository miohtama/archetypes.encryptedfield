# -*- coding: utf-8 -*-

import os
import unittest2 as unittest
import base64

from archetypes.encryptedfield.testing import\
    ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

from archetypes.encryptedfield import encryption
from archetypes.encryptedfield.field import EncryptedField, CannotSaveError
from archetypes.encryptedfield.envkey import EnvironKeyProvider


from Products.Archetypes.tests.utils import mkDummyInContext
from Products.Archetypes.atapi import Schema, BaseContentMixin

# Key must be 32 bytes long
KEY = "x" * 32

BAD_KEY = "y" * 32


class TestEncrypt(unittest.TestCase):
    """ Test encryption module """
    layer = ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        self.key = KEY

    def test_encrypt(self):
        encryption.encrypt_value(self.key, u"Foobar")

    def test_decrypt(self):
        value = u"Foobar"
        encrypted = encryption.encrypt_value(self.key, value)
        decrypted = encryption.decrypt_value(self.key, encrypted)
        self.assertEqual(value, decrypted)

    def test_decrypt_utf8(self):
        value = u"ÅÄÖ"
        encrypted = encryption.encrypt_value(self.key, value)
        decrypted = encryption.decrypt_value(self.key, encrypted)
        self.assertEqual(value, decrypted)

    def test_encrypt_not_unicode(self):
        try:
            encryption.encrypt_value(self.key, "x" * 16)
            raise AssertionError("Should not be reached")
        except RuntimeError:
            pass

    def test_decrypt_bad_key(self):
        value = u"Foobar"
        encrypted = encryption.encrypt_value(self.key, value)
        decrypted = encryption.decrypt_value(BAD_KEY, encrypted)
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

    def canDecrypt(self, field):
        """
        :return: True if the currently logged in user has decryption priviledges
        """
        return False


class TestField(unittest.TestCase):
    """ Test field and widget """
    layer = ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        self.key = KEY
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
        value = "foobar"
        field = self.schema["testField"]
        field.set(self.dummy, value)
        del os.environ["DATA_ENCRYPTION_SECRET"]
        decrypted = field.get(self.dummy)
        self.assertEqual(decrypted, field.msg_cannot_crypt)

    def test_decrypt_corrupted_data(self):
        self.dummy.testField = "z" * 16
        field = self.schema["testField"]
        decrypted = field.get(self.dummy)
        self.assertEqual(decrypted, field.msg_bad_key)

    def test_decrypt_corrupted_base64(self):
        self.dummy.testField = base64.b64encode("z" * 16)
        field = self.schema["testField"]
        decrypted = field.get(self.dummy)
        self.assertEqual(decrypted, field.msg_bad_key)

    def test_save_widget(self):
        """ Widge should spit out empty marker instead of actual value if no save priviledge """
        doc = self.dummy
        field = doc.Schema()['testField']
        widget = field.widget
        value = "zzzz"

        self.assertFalse(widget.isDisabled(doc, field))

        form = {'testField': value}
        marker = {}
        result = widget.process_form(doc, field, form, empty_marker=marker)
        expected = value, {}

        # We should get empty marker here
        self.assertEqual(expected, result)


class TestDecryptionNotAllowed(unittest.TestCase):
    """
    See the different cases when user has no decryption priviledge.
    """
    layer = ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        self.key = KEY
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

        self.assertTrue(widget.isDisabled(doc, field))

        form = {'testField': 'xxxxx'}
        marker = {}
        result = widget.process_form(doc, field, form, empty_marker=marker)

        # We should get empty marker here
        self.assertEqual(marker, result)

    def test_save_field(self):
        doc = self.dummy
        field = doc.Schema()['testField']
        try:
            field.set(doc, "foobar")
            raise AssertionError("Should not be reached")
        except CannotSaveError:
            pass
