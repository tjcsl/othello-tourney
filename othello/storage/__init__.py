import os
from django.conf import settings
from django.contrib.staticfiles.storage import StaticFilesStorage

from css_html_js_minify import process_single_css_file, process_single_js_file


class MinifiedStaticFilesStorage(StaticFilesStorage):
    def __init__(self):
        self.minify = not settings.DEBUG
        super(MinifiedStaticFilesStorage, self).__init__()

    def _open(self, name, mode='rb'):
        super(MinifiedStaticFilesStorage, self)._open(name, mode)

    def _save(self, name, content):
        filename = super(MinifiedStaticFilesStorage, self)._save(name, content)
        path, extension = os.path.splitext(filename)
        if self.minify:
            if "css" in extension:
                process_single_css_file(os.path.join(self.location, filename), overwrite=True)
            elif "js" in extension:
                process_single_js_file(os.path.join(self.location, filename), overwrite=True)
