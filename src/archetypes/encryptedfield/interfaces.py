"""

"""

from zope.interface import Interface


class IKeyProvider(Interface):
    """
    Adapter for (context, HTTP request).

    Extract the encryption key from the environment.
    """

    def canDecrypt(field):
        """
        :return: True if the currently logged in user has decryption priviledges
        """

    def getKey(field):
        """
        :return: Symmetric encryption key as string or None if not available
        """

