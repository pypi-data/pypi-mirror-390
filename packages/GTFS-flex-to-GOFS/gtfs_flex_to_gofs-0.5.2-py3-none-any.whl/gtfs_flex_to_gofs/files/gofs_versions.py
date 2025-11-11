from dataclasses import dataclass

from ..gofs_file import GofsFile
from ..utils import concat_url

FILENAME = 'gofs_versions'


@dataclass
class Version:
    version: str
    url: str


def create(default_headers_template, base_url):
    if base_url is None:
        return GofsFile(FILENAME, created=False)

    versions = [Version(
        version=default_headers_template['version'], url=concat_url(base_url, 'gofs'))]

    return GofsFile(FILENAME, created=True, data=versions)
