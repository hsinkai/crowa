import os
import time

from logutil import TimedRotatingLogger

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

err_logger = TimedRotatingLogger(filename=os.path.join(basedir, 'logs', 'srv_error_log'))
acc_logger = TimedRotatingLogger(filename=os.path.join(basedir, 'logs', 'srv_access_log'),
                                 format="[%(levelname)s][%(asctime)s][%(threadName)s] - %(message)s")


class LogFacade(object):
    def _logs(self, request, *args, **kwargs):
        user = request.user
        msg = u"Accepted Request: user=%s, remote_addr=%s, method=%s, path=%s, subject=%s, X-Forwarded-For=%s" % (
            user.get_username(),
            request.META.get('REMOTE_ADDR'),
            request.method,
            request.path,
            kwargs.get('_subject', '{}'),
            request.META.get('X-Forwarded-For')
        )
        acc_logger.info(msg)


class ListLog(object):
    def list(self, request, *args, **kwargs):
        self._tick = time.time()
        self._logs(request, *args, _subject=request.query_params.__repr__().decode('unicode-escape'), **kwargs)
        res = super(LogFacade, self).list(request, *args, **kwargs)
        acc_logger.info('Handled Request: code=success, cost=%s' % (time.time() - self._tick))
        return res


class RetrieveLog(object):
    def retrieve(self, request, *args, **kwargs):
        self._tick = time.time()
        self._logs(request, *args, _subject=request.query_params.__repr__().decode('unicode-escape'), **kwargs)
        res = super(LogFacade, self).retrieve(request, *args, **kwargs)
        acc_logger.info('Handled Request: code=success, cost=%s' % (time.time() - self._tick))
        return res


class WriteLog(object):
    def create(self, request, *args, **kwargs):
        self._tick = time.time()
        self._logs(request, *args, _subject=request.data.__repr__().decode('unicode-escape'), **kwargs)
        res = super(LogFacade, self).create(request, *args, **kwargs)
        acc_logger.info('Handled Request: code=success, cost=%s' % (time.time() - self._tick))
        return res

    def update(self, request, *args, **kwargs):
        self._tick = time.time()
        self._logs(request, *args, _subject=request.data.__repr__().decode('unicode-escape'), **kwargs)
        res = super(LogFacade, self).update(request, *args, **kwargs)
        acc_logger.info('Handled Request: code=success, cost=%s' % (time.time() - self._tick))
        return res

    def destroy(self, request, *args, **kwargs):
        self._tick = time.time()
        self._logs(request, *args, **kwargs)
        res = super(LogFacade, self).destroy(request, *args, **kwargs)
        acc_logger.info('Handled Request: code=success, cost=%s' % (time.time() - self._tick))
        return res