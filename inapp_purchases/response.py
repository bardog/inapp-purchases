# coding: utf-8

class Response(object):
    status = None
    raw = None
    data = None
    success = None

    def __init__(self, status=None, raw=None, data=None):
        self.status = status
        self.raw = raw
        self.data = data
        self.success = self.is_success()

    def is_success(self, status=None):
        if status is not None:
            self.status = status
        self.success = self.status == 200
        return self.success

    def __dict__(self):
        return {
            'status': self.status,
            'raw': self.raw,
            'data': self.data,
            'success': self.success
        }
