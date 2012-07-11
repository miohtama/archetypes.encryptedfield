"""

"""

from zope.interface import Interface


class IKeyProvider(Interface):
    """
    Adapter for (context, HTTP request).

    Extract the encryption key from the environment.

    1) If the user has not *permission* to access the value canDecrypt() must return False

    2) If the key is not available in the system getKey() must return None

    """

    def canDecrypt(field):
        """
        :return: True if the currently logged in user has decryption priviledges
        """

    def getKey(field):
        """
        :return: Symmetric encryption key as string or None if not available
        """
