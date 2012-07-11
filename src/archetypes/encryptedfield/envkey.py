"""

    Implementation which reads the encryption key from OS environ

"""

import os

from zope.interface import implements

from archetypes.encryptedfield.interfaces import IKeyProvider

ENV_VAR_NAME = "DATA_ENCRYPTION_SECRET"


class EnvironKeyProvider(object):

    implements(IKeyProvider)

    def __init__(self, context, request):
        """
        """
        self.context = context
        self.request = request

    def canDecrypt(self, field):
        """
        :return: True if the currently logged in user has decryption priviledges
        """
        return True

    def getKey(self, field):
        """
        :return: Symmetric encryption key as string or None if not available
        """
        return os.environ.get(ENV_VAR_NAME)
