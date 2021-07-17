#!/usr/bin/env python3
# coding=utf-8

from abc import ABC, abstractmethod

from praw.models import Comment, Submission


class BaseArchiveEntry(ABC):
    def __init__(self, source: (Comment, Submission)):
        self.source = source
        self.post_details: dict = {}

    @abstractmethod
    def compile(self) -> dict:
        raise NotImplementedError

    @staticmethod
    def _convert_comment_to_dict(in_comment: Comment) -> dict:
        out_dict = {
            'author': in_comment.author.name if in_comment.author else 'DELETED',
            'id': in_comment.id,
            'score': in_comment.score,
            'subreddit': in_comment.subreddit.display_name,
            'author_flair': in_comment.author_flair_text,
            'submission': in_comment.submission.id,
            'stickied': in_comment.stickied,
            'body': in_comment.body,
            'is_submitter': in_comment.is_submitter,
            'distinguished': in_comment.distinguished,
            'created_utc': in_comment.created_utc,
            'parent_id': in_comment.parent_id,
            'replies': [],
        }
        in_comment.replies.replace_more(0)
        for reply in in_comment.replies:
            out_dict['replies'].append(BaseArchiveEntry._convert_comment_to_dict(reply))
        return out_dict
