import unittest2 as unittest


from archetypes.encryptedfield.testing import\
    ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING


class TestExample(unittest.TestCase):

    layer = ARCHETYPES_ENCRYPTEDFIELD_INTEGRATION_TESTING
    
    def setUp(self):
        # you'll want to use this to set up anything you need for your tests 
        # below
        pass

    def test_success(self):
        sum = 1 + 3
        self.assertEquals(sum, 4)

    def test_failure(self):
        sum = 2 + 3
        self.assertEquals(sum, 4)
