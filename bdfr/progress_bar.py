import logging
from typing import Optional

from tqdm import tqdm

logger = logging.getLogger()


class Progress:
    def __init__(self, progress_bar: bool, n_subreddits: int):
        self.progress_bar = progress_bar
        self.bar_outer: Optional[tqdm] = None
        self.bar_inner: Optional[tqdm] = None

        if self.progress_bar:
            logger.setLevel(logging.CRITICAL)
            self.bar_outer = tqdm(total=n_subreddits, initial=0, desc="Subreddits", unit="subreddit", colour="green")

    def subreddit_new(self, generator):
        if self.progress_bar:
            # generator is a ListingGenerator or a (usually empty) list
            try:
                desc = generator.url
            except:
                desc = "Posts"

            try:
                total = generator.limit
            except:
                total = 1

            self.bar_inner = tqdm(total=total, initial=0, desc=desc, unit="post", colour="green", leave=False)

    def subreddit_done(self):
        if self.progress_bar:
            self.bar_outer.update(1)
            self.bar_inner.close()

    def post_done(self, submission, success: bool):
        if self.progress_bar:
            self.bar_inner.update(1)
            title_short = submission.title[:60] + (submission.title[60:] and "...")
            log_str = f"{submission.score:5d}🔼 {title_short}"
            icon = "✅" if success else "❌"
            self.bar_outer.write(f"{icon} {log_str}")
