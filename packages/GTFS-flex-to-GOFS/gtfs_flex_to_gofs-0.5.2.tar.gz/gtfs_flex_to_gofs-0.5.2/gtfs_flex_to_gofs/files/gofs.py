from dataclasses import dataclass

from ..gofs_file import GofsFile
from ..utils import concat_url

FILENAME = 'gofs'


@dataclass
class URL:
    name: str
    url: str


def create(gtfs, base_url, created_files):
    if base_url is None:
        return GofsFile(FILENAME, False)

    agency = list(gtfs.agency.values())[0]  # Only support one agency so far
    lang = agency.agency_lang
    urls = []

    for created_file in created_files.values():
        urls.append(URL(name=created_file.filename, url=concat_url(
            base_url, lang, created_file.filename)))

    data = {lang: {'feeds': urls}}
    return GofsFile(FILENAME, created=True, data=data, nest_data_under_filename=False)
