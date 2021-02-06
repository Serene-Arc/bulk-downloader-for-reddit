import os
import pathlib
import urllib.error
import urllib.request
from html.parser import HTMLParser

from src.downloaders.downloaderUtils import getExtension, getFile
from src.errors import AlbumNotDownloadedCompletely, FileAlreadyExistsError, NotADownloadableLinkError
from src.utils import GLOBAL
from src.utils import printToFile as print


class Erome:
    def __init__(self, directory: pathlib.Path, post: dict):
        try:
            images = self.getLinks(post['CONTENTURL'])
        except urllib.error.HTTPError:
            raise NotADownloadableLinkError("Not a downloadable link")

        images_length = len(images)
        how_many_downloaded = images_length
        duplicates = 0

        if images_length == 1:
            extension = getExtension(images[0])

            """Filenames are declared here"""
            filename = GLOBAL.config['filename'].format(**post) + post["EXTENSION"]
            short_filename = post['POSTID'] + extension

            image_url = images[0]
            if 'https://' not in image_url or 'http://' not in image_url:
                image_url = "https://" + image_url

            getFile(filename, short_filename, directory, image_url)

        else:
            filename = GLOBAL.config['filename'].format(**post)
            print(filename)

            folder_dir = directory / filename

            try:
                if not os.path.exists(folder_dir):
                    os.makedirs(folder_dir)
            except FileNotFoundError:
                folder_dir = directory / post['POSTID']
                os.makedirs(folder_dir)

            for i in range(images_length):
                extension = getExtension(images[i])

                filename = str(i + 1) + extension
                image_url = images[i]
                if 'https://' not in image_url and 'http://' not in image_url:
                    image_url = "https://" + image_url

                print("  ({}/{})".format(i + 1, images_length))
                print("  {}".format(filename))

                try:
                    getFile(filename, filename, folder_dir, image_url, indent=2)
                    print()
                except FileAlreadyExistsError:
                    print("  The file already exists" + " " * 10, end="\n\n")
                    duplicates += 1
                    how_many_downloaded -= 1

                except Exception as exception:
                    # raise exception
                    print("\n  Could not get the file")
                    print(
                        "  "
                        + "{class_name}: {info}".format(class_name=exception.__class__.__name__, info=str(exception))
                        + "\n"
                    )
                    how_many_downloaded -= 1

            if duplicates == images_length:
                raise FileAlreadyExistsError
            elif how_many_downloaded + duplicates < images_length:
                raise AlbumNotDownloadedCompletely("Album Not Downloaded Completely")

    def getLinks(self, url: str) -> list[str]:
        content = []
        line_number = None

        class EromeParser(HTMLParser):
            tag = None

            def handle_starttag(self, tag, attrs):
                self.tag = {tag: {attr[0]: attr[1] for attr in attrs}}

        page_source = (urllib.request.urlopen(url).read().decode().split('\n'))

        """ FIND WHERE ALBUM STARTS IN ORDER NOT TO GET WRONG LINKS"""
        for i in range(len(page_source)):
            obj = EromeParser()
            obj.feed(page_source[i])
            tag = obj.tag

            if tag is not None:
                if "div" in tag:
                    if "id" in tag["div"]:
                        if tag["div"]["id"] == "album":
                            line_number = i
                            break

        for line in page_source[line_number:]:
            obj = EromeParser()
            obj.feed(line)
            tag = obj.tag
            if tag is not None:
                if "img" in tag:
                    if "class" in tag["img"]:
                        if tag["img"]["class"] == "img-front":
                            content.append(tag["img"]["src"])
                elif "source" in tag:
                    content.append(tag["source"]["src"])

        return [link for link in content if link.endswith("_480p.mp4") or not link.endswith(".mp4")]
