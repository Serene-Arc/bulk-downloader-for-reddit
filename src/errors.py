class RedditLoginFailed(Exception):
    pass

class ImgurLoginError(Exception):
    pass

class FileAlreadyExistsError(Exception):
    pass

class NotADownloadableLinkError(Exception):
    pass

class AlbumNotDownloadedCompletely(Exception):
    pass

class FileNameTooLong(Exception):
    pass

class InvalidRedditLink(Exception):
    pass

class NoMatchingSubmissionFound(Exception):
    pass

class NoPrawSupport(Exception):
    pass

class NoRedditSupoort(Exception):
    pass

class MultiredditNotFound(Exception):
    pass

class InsufficientPermission(Exception):
    pass

class InvalidSortingType(Exception):
    pass

class FileNotFoundError(Exception):
    pass