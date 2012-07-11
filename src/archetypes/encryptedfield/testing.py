from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class ArchetypesEncryptedfield(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import archetypes.encryptedfield
        xmlconfig.file('configure.zcml',
                       archetypes.encryptedfield,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        pass

ARCHETYPES_ENCRYPTEDFIELD_FIXTURE = ArchetypesEncryptedfield()
ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(ARCHETYPES_ENCRYPTEDFIELD_FIXTURE, ),
                       name="ArchetypesEncryptedfield:Integration")