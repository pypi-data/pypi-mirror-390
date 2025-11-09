class PostingError(Exception):
    pass


class PeriodLockedError(PostingError):
    pass


class ValidationError(PostingError):
    pass