from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import StringWidget


class EncryptedWidget(StringWidget):
    """
    Disable input field unless encryption priviledge is available.
    """
    security = ClassSecurityInfo()

    _properties = StringWidget._properties.copy()

    _properties.update({
            "macro": "encryptedwidget"
    })

    def isDisabled(self, context, field):
        """
        Can user access the encrypted value.

        :return: Boolean
        """
        provider = field.key_provider(context, context.REQUEST)

        if not provider.canDecrypt(field):
            return True

        if not provider.getKey(field):
            return True

        return False

    def disabled(self, context, field):
        """ Called from template.
        :return: HTML for disabling the field.
        """
        if self.isDisabled(context, field):
            return "DISABLED"
        return None

    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""

        # Field value cannot be set
        # if we don't have key provider encryption priviledge
        if self.isDisabled(instance, field):
            return empty_marker

        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker

        if emptyReturnsMarker and value == '':
            return empty_marker
        return value, {}
