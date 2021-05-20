#!/usr/bin/env python3
# coding=utf-8

import logging

import praw.models

from bdfr.archive_entry.base_archive_entry import BaseArchiveEntry

logger = logging.getLogger(__name__)


class SubmissionArchiveEntry(BaseArchiveEntry):
    def __init__(self, submission: praw.models.Submission):
        super(SubmissionArchiveEntry, self).__init__(submission)

    def compile(self) -> dict:
        comments = self._get_comments()
        self._get_post_details()
        out = self.post_details
        out['comments'] = comments
        return out

    def _get_post_details(self):
        self.post_details = {
            'title': self.source.title,
            'name': self.source.name,
            'url': self.source.url,
            'selftext': self.source.selftext,
            'score': self.source.score,
            'upvote_ratio': self.source.upvote_ratio,
            'permalink': self.source.permalink,
            'id': self.source.id,
            'author': self.source.author.name if self.source.author else 'DELETED',
            'link_flair_text': self.source.link_flair_text,
            'num_comments': self.source.num_comments,
            'over_18': self.source.over_18,
            'spoiler': self.source.spoiler,
            'pinned': self.source.pinned,
            'locked': self.source.locked,
            'distinguished': self.source.distinguished,
            'created_utc': self.source.created_utc,
        }

    def _get_comments(self) -> list[dict]:
        logger.debug(f'Retrieving full comment tree for submission {self.source.id}')
        comments = []
        self.source.comments.replace_more(0)
        for top_level_comment in self.source.comments:
            comments.append(self._convert_comment_to_dict(top_level_comment))
        return comments
