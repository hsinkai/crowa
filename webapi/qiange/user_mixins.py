class _UserMixin(object):
    def get_username(self):
        raise NotImplementedError()

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_superuser(self):
        return False

    @property
    def is_staff(self):
        return False

    def __unicode__(self):
        return u"Hello %s: %s" % (self.__class__.__name__, self.get_username())


class TokenUser(_UserMixin, ):
    def __init__(self, id, username, **verbose):
        self.id = id
        self.username = username

    def get_username(self):
        return 'TokenUser'


class WebTokenUser(_UserMixin, ):
    def __init__(self, id, username, **verbose):
        self.id = id
        self.username = username

    def get_username(self):
        return self.username


class AdmTokenUser(_UserMixin, ):
    def __init__(self, id, username, **verbose):
        self.id = id
        self.username = username

    @property
    def is_staff(self):
        return True

    def get_username(self):
        return self.username
