# Copyright (c) 2021,2022,2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Parse source text file into a book model."""

import argparse
import logging
from collections import Counter
from dataclasses import dataclass
from types import ModuleType
from typing import List, Tuple, Union

import regex as re

from txt2ebook.models import Book, Chapter, Volume
from txt2ebook.tokenizer import Token, Tokenizer
from txt2ebook.languages.zh_base import (
    zh_halfwidth_to_fullwidth,
    zh_words_to_numbers,
)

logger = logging.getLogger(__name__)


@dataclass
class Parser:
    """Parser class to massage and parse a text content."""

    raw_content: str
    config: argparse.Namespace
    langconf: ModuleType

    def __init__(
        self,
        raw_content: str,
        config: argparse.Namespace,
        langconf: ModuleType,
    ) -> None:
        """Set the constructor for the Parser."""
        self.raw_content = raw_content
        self.config = config
        self.langconf = langconf

    def parse(self) -> Book:
        """Parse the content into volumes (optional) and chapters.

        Returns:
          txt2ebook.models.Book: The Book model.
        """
        tokenizer = Tokenizer(self.raw_content, self.config, self.langconf)

        (book_title, authors, translators, tags, index, toc) = (
            self.parse_tokens(tokenizer)
        )

        book = Book(
            title=book_title,
            language=self.config.language,
            authors=authors,
            translators=translators,
            tags=tags,
            index=index,
            cover=getattr(self.config, "cover", ""),
            raw_content=self.raw_content,
            toc=toc,
        )

        stats = book.stats()
        logger.info("Found volumes: %s", stats["Volume"])
        logger.info("Found chapters: %s", stats["Chapter"])

        return book

    def _pad_header_number(self, words: str, length: int) -> str:
        """Left pad the section number if found as halfwidth or fullwidth
        integer.
        """
        # left pad the section number if found as halfwidth integer
        match = re.match(rf"第([{self.langconf.HALFWIDTH_NUMS}]*)", words)
        if match and match.group(1) != "":
            header_nums = match.group(1)
            return words.replace(
                header_nums, str(header_nums).rjust(length, "0")
            )

        # left pad the section number if found as fullwidth integer
        match = re.match(rf"第([{self.langconf.FULLWIDTH_NUMS}]*)", words)
        if match and match.group(1) != "":
            header_nums = match.group(1)
            return words.replace(
                header_nums, str(header_nums).rjust(length, "０")
            )

        return words

    def words_to_nums(self, words: str, length: int) -> str:
        """Convert header from words to numbers.

        For example, `第一百零八章` becomes `第108章`.

        Args:
            words(str): The line that contains section header in words.
            length(int): The number of left zero-padding to prepend.

        Returns:
            str: The formatted section header.
        """
        if not getattr(
            self.config, "header_number", False
        ) or self.config.language not in (
            "zh-cn",
            "zh-tw",
        ):
            return words

        # Check if the header is already a number and pad it
        padded_words = self._pad_header_number(words, length)
        if padded_words != words:
            return padded_words

        # Convert words to numbers and then apply fullwidth conversion if
        # configured
        replaced_words = zh_words_to_numbers(words, length=length)

        if hasattr(self.config, "fullwidth") and self.config.fullwidth:
            replaced_words = zh_halfwidth_to_fullwidth(replaced_words)

        logger.debug(
            "Convert header to numbers: %s -> %s",
            words[:10],
            replaced_words[:10],
        )
        return replaced_words

    def _process_metadata_token(self, token: Token, book_data: dict) -> None:
        """Process metadata tokens (TITLE, AUTHOR, TAG, INDEX, TRANSLATOR)."""
        if token.type == "TITLE":
            book_data["book_title"] = token.value
        elif token.type == "AUTHOR":
            book_data["authors"].append(token.value)
        elif token.type == "TAG":
            book_data["tags"].append(token.value)
        elif token.type == "INDEX":
            book_data["index"] = token.value.split(" ")
        elif token.type == "TRANSLATOR":
            book_data["translators"].append(token.value)

    def _process_volume_chapter_token(
        self,
        token: Token,
        toc: List[Volume | Chapter],
        stats: Counter,
        current_volume: Volume,
        current_chapter: Chapter,
    ) -> Tuple[Volume, Chapter]:
        """Process VOLUME_CHAPTER token and update current volume/chapter."""
        [volume, chapter] = token.value

        volume_title = self.words_to_nums(volume.value, 2)
        if current_volume.title != volume_title:
            current_volume = Volume(title=volume_title)
            toc.append(current_volume)

        chapter_title = self.words_to_nums(
            chapter.value, len(str(stats.get("VOLUME_CHAPTER")))
        )
        if current_chapter.title != chapter_title:
            current_chapter = Chapter(title=chapter_title)
            if isinstance(toc[-1], Volume):
                toc[-1].add_chapter(current_chapter)

        return current_volume, current_chapter

    def _process_volume_token(
        self,
        token: Token,
        toc: List[Volume | Chapter],
        stats: Counter,
        current_volume: Volume,
    ) -> Volume:
        """Process VOLUME token and update current volume."""
        volume_title = self.words_to_nums(
            token.value, len(str(stats.get("VOLUME")))
        )
        if current_volume.title != volume_title:
            current_volume = Volume(title=volume_title)
            toc.append(current_volume)
        return current_volume

    def _process_chapter_token(
        self,
        token: Token,
        toc: List[Volume | Chapter],
        stats: Counter,
        current_chapter: Chapter,
    ) -> Chapter:
        """Process CHAPTER token and update current chapter."""
        chapter_title = self.words_to_nums(
            token.value, len(str(stats.get("CHAPTER")))
        )
        if current_chapter.title != chapter_title:
            current_chapter = Chapter(title=chapter_title)

            if toc and isinstance(toc[-1], Volume):
                toc[-1].add_chapter(current_chapter)
            else:
                toc.append(current_chapter)
        return current_chapter

    def _process_paragraph_token(
        self, token: Token, toc: List[Volume | Chapter]
    ) -> None:
        """Process PARAGRAPH token and add it to the current chapter."""
        if toc:
            if isinstance(toc[-1], Volume):
                toc[-1].chapters[-1].add_paragraph(token.value)

            if isinstance(toc[-1], Chapter):
                toc[-1].add_paragraph(token.value)

    def parse_tokens(self, tokenizer: Tokenizer) -> Tuple:
        """Parse the tokens and organize into book structure."""
        toc: List[Volume | Chapter] = []
        book_data = {
            "book_title": "",
            "authors": [],
            "tags": [],
            "index": [],
            "translators": [],
        }
        current_volume = Volume("")
        current_chapter = Chapter("")

        tokens = tokenizer.tokens
        stats = tokenizer.stats()

        # Show chapter tokens by default if no volume tokens
        chapter_verbosity = 0
        paragraph_verbosity = 1
        if bool(stats.get("VOLUME_CHAPTER")) or bool(stats.get("VOLUME")):
            chapter_verbosity = 2
            paragraph_verbosity = 3

        for token in tokens:
            if (
                token.type not in ["CHAPTER", "PARAGRAPH"]
                or (
                    token.type == "CHAPTER"
                    and self.config.verbose >= chapter_verbosity
                )
                or (
                    token.type == "PARAGRAPH"
                    and self.config.verbose >= paragraph_verbosity
                )
            ):
                logger.debug(repr(token))

            if token.type in [
                "TITLE",
                "AUTHOR",
                "TAG",
                "INDEX",
                "TRANSLATOR",
            ]:
                self._process_metadata_token(token, book_data)
            elif token.type == "VOLUME_CHAPTER":
                (current_volume, current_chapter) = (
                    self._process_volume_chapter_token(
                        token, toc, stats, current_volume, current_chapter
                    )
                )
            elif token.type == "VOLUME":
                current_volume = self._process_volume_token(
                    token, toc, stats, current_volume
                )
            elif token.type == "CHAPTER":
                current_chapter = self._process_chapter_token(
                    token, toc, stats, current_chapter
                )
            elif token.type == "PARAGRAPH":
                self._process_paragraph_token(token, toc)

        # Use authors if set explicitly from command line.
        if getattr(self.config, "author", None):
            book_data["authors"] = self.config.author

        if getattr(self.config, "title", None):
            book_data["book_title"] = self.config.title

        if getattr(self.config, "translator", None):
            book_data["translators"] = self.config.translator

        logger.info("Found or set book title: %s", book_data["book_title"])
        logger.info("Found or set authors: %s", repr(book_data["authors"]))
        logger.info(
            "Found or set translators: %s", repr(book_data["translators"])
        )
        logger.info("Found or set tags: %s", repr(book_data["tags"]))
        logger.info("Found or set index: %s", repr(book_data["index"]))

        if getattr(self.config, "sort_volume_and_chapter", False):
            self.sort_volume_and_chapter(toc)

        return (
            book_data["book_title"],
            book_data["authors"],
            book_data["translators"],
            book_data["tags"],
            book_data["index"],
            toc,
        )

    def sort_volume_and_chapter(self, toc: List[Union[Volume, Chapter]]) -> None:
        """Sort by title of volumes and its chapters.

        Args:
            toc(List[Union[Volume, Chapter]]): The parsed table of content

        Returns:
            str: The formatted book content
        """
        for section in toc:
            if isinstance(section, Volume):
                section.chapters.sort(key=lambda x: x.title)

        toc.sort(key=lambda x: x.title if isinstance(x, Volume) else "")
