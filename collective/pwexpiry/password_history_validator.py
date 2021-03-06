from AccessControl import AuthEncoding
from collective.pwexpiry.interfaces import ICustomPasswordValidator
from plone import api
from zope.interface import implementer

from .config import _
from .interfaces import ICollectivePWExpiryLayer


@implementer(ICustomPasswordValidator)
class PasswordHistoryValidator(object):
    """ Checks if the password has already been used
    by iterating over the memberdata property password_history_size.
    """

    def __init__(self, context):
        self.context = context

    def validate(self, password, data):
        """
        Password validation method
        """

        # Don't check the password if collective.pwexpiry hasn't
        # been installed yet.
        if not ICollectivePWExpiryLayer \
                .providedBy(self.context.REQUEST):
            return None

        # Permit empty passwords here to allow registration links.
        # Plone will force the user to set one.
        if password is None:
            return None

        if api.user.is_anonymous():
            # No check for registrations.
            return None

        max_history_pws = api.portal.get_registry_record(
            'collective.pwexpiry.password_history_size'
        )
        if max_history_pws == 0:
            # max_history_pws has been disabled.
            return None

        user = api.user.get_current()
        pw_history = user.getProperty('password_history', tuple())

        for old_pw in pw_history[-max_history_pws:]:
            if AuthEncoding.pw_validate(old_pw, str(password)):
                return _(
                    u'info_reused_pw',
                    default=u'This password has been used already.'
                )

        # All fine
        return None
