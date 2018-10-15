class IDReprMixin(object):
    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class NameReprMixin(object):
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class DescriptionReprMixin(object):
    def __str__(self):
        return self.description

    def __unicode__(self):
        return self.description