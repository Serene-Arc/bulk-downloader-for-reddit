#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.handlers
import os
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class SqliteManager:
    def __init__(self, args):
        self.args = args
        self.db = self.connect_to_db()

    def connect_to_db(self):
        db_path = Path(self.args.directory, f"{self.args.downloads_db_name}.sqlite3")
        db_exists = os.path.exists(db_path)

        conn = sqlite3.connect(db_path)

        if not db_exists:
            self.create_table(conn)
            logger.info(f"Created new database at {db_path}")

        return conn

    def create_table(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS downloads (
            subreddit TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_hash TEXT PRIMARY KEY,
            file_size INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        logger.debug("Created new table 'downloads' with unique index 'idx_file_hash' on 'file_hash'")

    def insert(self, subreddit, file_name, file_hash, file_size):
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
            INSERT INTO downloads (subreddit, file_name, file_hash, file_size)
            VALUES (?, ?, ?, ?)
            """,
                (subreddit, file_name, file_hash, file_size),
            )
            self.db.commit()
            logger.debug(f"Inserted {file_name} into downloads table")
        except sqlite3.IntegrityError as e:
            logger.warning(f"Failed to insert {file_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error inserting {file_name}: {e}")

    def select(self, file_hash):
        cursor = self.db.cursor()
        cursor.execute(
            """
            SELECT * FROM downloads WHERE file_hash = ?
        """,
            (file_hash,),
        )
        return cursor.fetchone()

    def delete(self, file_hash):
        cursor = self.db.cursor()
        cursor.execute(
            """
            DELETE FROM downloads WHERE file_hash = ?
        """,
            (file_hash,),
        )
        self.db.commit()

    def delete_all(self):
        cursor = self.db.cursor()
        cursor.execute(
            """
            DELETE FROM downloads
        """
        )
        self.db.commit()

    def close(self):
        self.db.close()
