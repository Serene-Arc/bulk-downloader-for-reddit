import sys


def full_exc_info(exc_info):

    def current_stack(skip=0):
        try:
            1 / 0
        except ZeroDivisionError:
            f = sys.exc_info()[2].tb_frame
        for i in range(skip + 2):
            f = f.f_back
        lst = []
        while f is not None:
            lst.append((f, f.f_lineno))
            f = f.f_back
        return lst

    def extend_traceback(tb, stack):

        class FauxTb():
            def __init__(self, tb_frame, tb_lineno, tb_next):
                self.tb_frame = tb_frame
                self.tb_lineno = tb_lineno
                self.tb_next = tb_next

        """Extend traceback with stack info."""
        head = tb
        for tb_frame, tb_lineno in stack:
            head = FauxTb(tb_frame, tb_lineno, head)
        return head

    """Like sys.exc_info, but includes the full traceback."""
    t, v, tb = exc_info
    full_tb = extend_traceback(tb, current_stack(1))
    return t, v, full_tb


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


class ProgramModeError(Exception):
    pass


class SearchModeError(Exception):
    pass


class RedditorNameError(Exception):
    pass


class NoMatchingSubmissionFound(Exception):
    pass


class NoPrawSupport(Exception):
    pass


class NoRedditSupport(Exception):
    pass


class MultiredditNotFound(Exception):
    pass


class InsufficientPermission(Exception):
    pass


class InvalidSortingType(Exception):
    pass


class FileNotFoundError(Exception):
    pass


class NoSuitablePost(Exception):
    pass


class ImgurLimitError(Exception):
    pass


class DirectLinkNotFound(Exception):
    pass


class InvalidJSONFile(Exception):
    pass


class FailedToDownload(Exception):
    pass


class TypeInSkip(Exception):
    pass


class DomainInSkip(Exception):
    pass


class ImageNotFound(Exception):
    pass


class ExtensionError(Exception):
    pass
