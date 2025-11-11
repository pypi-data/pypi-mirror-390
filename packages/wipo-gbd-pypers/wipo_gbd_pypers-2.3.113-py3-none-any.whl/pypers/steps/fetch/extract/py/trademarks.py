from pypers.steps.base.extract import ExtractBase
import os

class Trademarks(ExtractBase):
    """
    Extract PYTM archive
    """

    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def add_xml_file(self, appnum, fullpath):
        # a bit of cleaning of the appnum to remove the _biblio which 
        # might come from the file name, e.g. PYM20252505839_biblio.xml
        appnum = appnum.replace("_biblio", "")

        self.manifest['data_files'].setdefault(appnum, {})
        self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
            fullpath, self.extraction_dir
        )

    def add_img_file(self, appnum, fullpath):
        if appnum == "logo" and "ATTACHMENT" in fullpath:
            # path to the file is via something like PYM20252519667/ATTACHMENT/logo.jpeg
            # which is one common default from ipas
            pieces = fullpath.split("/")
            if len(pieces)>3:
                appnum = pieces[-3]
        
        path = os.path.relpath(fullpath, self.extraction_dir)

        self.manifest['img_files'].setdefault(appnum, [])
        self.manifest['img_files'][appnum].append(
            {'ori': path}
        )

    def process(self):
        pass