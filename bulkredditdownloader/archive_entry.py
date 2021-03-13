#!/usr/bin/env python3
# coding=utf-8

import logging

import praw.models

logger = logging.getLogger(__name__)


class ArchiveEntry:
    def __init__(self, submission: praw.models.Submission):
        self.submission = submission
        self.comments: list[dict] = []
        self.post_details: dict = {}

    def compile(self) -> dict:
        self._fill_entry()
        out = self.post_details
        out['comments'] = self.comments
        return out

    def _fill_entry(self):
        self._get_comments()
        self._get_post_details()

    def _get_post_details(self):
        self.post_details = {
            'title': self.submission.title,
            'name': self.submission.name,
            'url': self.submission.url,
            'selftext': self.submission.selftext,
            'score': self.submission.score,
            'upvote_ratio': self.submission.upvote_ratio,
            'permalink': self.submission.permalink,
            'id': self.submission.id,
            'author': self.submission.author.name if self.submission.author else 'DELETED',
            'link_flair_text': self.submission.link_flair_text,
            'num_comments': self.submission.num_comments,
            'over_18': self.submission.over_18,
        }

    def _get_comments(self):
        logger.debug(f'Retrieving full comment tree for submission {self.submission.id}')
        self.submission.comments.replace_more(0)
        for top_level_comment in self.submission.comments:
            self.comments.append(self._convert_comment_to_dict(top_level_comment))

    @staticmethod
    def _convert_comment_to_dict(in_comment: praw.models.Comment) -> dict:
        out_dict = {
            'author': in_comment.author.name if in_comment.author else 'DELETED',
            'id': in_comment.id,
            'score': in_comment.score,
            'subreddit': in_comment.subreddit.display_name,
            'submission': in_comment.submission.id,
            'stickied': in_comment.stickied,
            'body': in_comment.body,
            'is_submitter': in_comment.is_submitter,
            'created_utc': in_comment.created_utc,
            'parent_id': in_comment.parent_id,
            'replies': [],
        }
        in_comment.replies.replace_more(0)
        for reply in in_comment.replies:
            out_dict['replies'].append(ArchiveEntry._convert_comment_to_dict(reply))
        return out_dict
