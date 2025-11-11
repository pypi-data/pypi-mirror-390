import json
import dataclasses
from dataclasses import dataclass

from .default_headers import get_default_headers


@dataclass
class GofsFile:
    EXTENSION = '.json'

    filename: str
    created: bool 
    data: any = None
    nest_data_under_filename: bool = True

    def get_filename_with_ext(self):
        return self.filename + GofsFile.EXTENSION

    def save(self, filepath, ttl, version, creation_timestamp):
        file = get_default_headers(ttl, version, creation_timestamp)
        if self.nest_data_under_filename:
            file['data'][self.filename] = self.data
        else:
            file['data'] = self.data

        full_filepath = filepath / self.get_filename_with_ext() 

        print('Saving {}'.format(full_filepath))
        with open(full_filepath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(file, indent=4, default=vars))

    copy_with = dataclasses.replace