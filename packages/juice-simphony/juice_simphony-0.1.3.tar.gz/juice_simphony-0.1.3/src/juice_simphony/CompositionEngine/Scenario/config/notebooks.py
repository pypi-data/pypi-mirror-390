# *************************************************************************** #
# This file is subject to the terms and conditions defined in the             #
# file 'LICENSE.txt', which is part of this source code package.              #
#                                                                             #
# No part of the package, including this file, may be copied, modified,       #
# propagated, or distributed except according to the terms contained in       #
# the file 'LICENSE.txt'.                                                     #
#                                                                             #
# (C) Copyright European Space Agency, 2025                                   #
# *************************************************************************** #
import os
from pathlib import Path
import textwrap
from importlib import resources
import shutil

base_package = (__package__ or "").split(".")[0]
config_file_path = resources.files(base_package) / "data"


from juice_simphony.CompositionEngine.Scenario.common import utils


class notebooks:

    def __init__(self, root_path, parameters=0, mapps=False):
        self.root_path = root_path
        self.parameters = parameters
        self.mapps = mapps
        self.mainFolderPath = ""
        self.iniAbsPath = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(self.root_path))), self.parameters["iniAbsolutePath"]))
        self.structure = {}

    def build(self):
        self.structure["path"] = self.createMainFolder('NOTEBOOKS')
        return self.structure

    def createMainFolder(self, folderName):
        self.mainFolderPath = utils.createFolder(self.root_path, folderName)

        # copy .env file to NOTEBOOKS folder
        env_file = "env.txt"
        dest_file = os.path.normpath(os.path.join(self.mainFolderPath))
        template_file = os.path.normpath(os.path.join(config_file_path, "templates/README/NOTEBOOKS", env_file))
        shutil.copy2(template_file, dest_file)

        return self.mainFolderPath

