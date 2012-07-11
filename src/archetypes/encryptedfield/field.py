from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.Archetypes.Field import StringField, ObjectField, encode, decode

from archetypes.encryptedfield.envkey import EnvironKeyProvider
from archetypes.encryptedfield import encryption
from archetypes.encryptedfield.widget import EncryptedWidget


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
        "msg_decrypt_filler": u"XXXXX",
        "widget": EncryptedWidget
        })

    security.declarePrivate('get')

    def get(self, instance, **kwargs):
        value = ObjectField.get(self, instance, **kwargs)
        if getattr(self, 'raw', False):
            return value

        if value in [None, ""]:
            return value

        request = getattr(instance, "REQUEST", None)
        provider = self.key_provider(instance, request)

        if not provider.canDecrypt(self):
            return self.msg_decrypt_filler

        key = provider.getKey(self)

        if not key:
            return self.msg_cannot_crypt

        value = encryption.decrypt_value(key, value)

        # Decryption with the current key failed
        if value is None:
            return self.msg_bad_key

        return encode(value, instance, **kwargs)

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """
        Save encrypted value.

        Value can be only saved if IKeyProvider.canDecrypt() value returns True.
        You should not reach this point otherwise as it's checked by widget.

        Empty values are saved as is.

        Other values are symmetrically encrypted using key provided by IKeyProvider.
        """
        kwargs['field'] = self
        # Remove acquisition wrappers
        if not getattr(self, 'raw', False):
            value = decode(aq_base(value), instance, **kwargs)

        request = getattr(instance, "REQUEST", None)
        provider = self.key_provider(instance, request)

        if not provider.canDecrypt(self):
            raise CannotSaveError("You cannot save this field because you have no encryption right")

        # Handle None save specially
        if value in [None, ""]:
            self.getStorage(instance).set(self.getName(), instance, value, **kwargs)
            return

        key = provider.getKey(self)

        if not key:
            raise CannotSaveError(self.msg_cannot_crypt)

        value = encryption.encrypt_value(key, value)

        self.getStorage(instance).set(self.getName(), instance, value, **kwargs)
