from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.Archetypes.Field import StringField, ObjectField, encode, decode

from archetypes.encryptedfield.envkey import EnvironKeyProvider
from archetypes.encryptedfieldy import encryption


class CannotSaveError(RuntimeError):
    """
    """


class EncryptedField(StringField):
    """
    Save data with symmetric encryption in the database.

    Empty values are handled specially.
    """
    security = ClassSecurityInfo()

    _properties = StringField._properties.copy()

    _properties.update({
        'key_provider': EnvironKeyProvider,
        'msg_cannot_crypt': u"Decryption is not available",
        'msg_bad_key': u"Decryption key does not match data",
        "msg_decrypt_filler": u"XXXXX"
        })

    security.declarePrivate('get')

    def get(self, instance, **kwargs):
        value = ObjectField.get(self, instance, **kwargs)
        if getattr(self, 'raw', False):
            return value

        if value in [None, ""]:
            return value

        provider = self.key_provider((instance, self.REQUEST))

        if not provider.canDecrypt():
            return self.msg_decrypt_filler

        key = provider.getKey()

        if not key:
            return self.msg_cannot_crypt

        value = encryption.decrypt(key, value)

        return encode(value, instance, **kwargs)

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """
        """
        kwargs['field'] = self
        # Remove acquisition wrappers
        if not getattr(self, 'raw', False):
            value = decode(aq_base(value), instance, **kwargs)

        provider = self.key_provider((instance, self.REQUEST))

        key = provider.getKey()

        if not provider.canDecrypt():
            raise CannotSaveError("You cannot save this field because you have no encryption right")

        if not key:
            raise CannotSaveError(self.msg_cannot_crypt)

        # Handle None save specially
        if value in [None, ""]:
            self.getStorage(instance).set(self.getName(), instance, value, **kwargs)
            return

        value = encryption.encrypt(key, value)

        self.getStorage(instance).set(self.getName(), instance, value, **kwargs)
