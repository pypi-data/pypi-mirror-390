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
from jinja2 import Template
import os
from datetime import datetime
import json
from juice_simphony.CompositionEngine.Scenario.common.fileHandleEps1 import fileHandleEps1
from juice_simphony.CompositionEngine.Scenario.common.fileName import fileName
from juice_simphony.CompositionEngine.Scenario.common.fileHandleTml import fileHandleTml




class timelineFile(fileHandleTml):
     
    def __init__(self, path, exp_name, version, params = 0):
        self.params = {}
        if params!=0: 
            self.params.update(params)
        self.path = path
        self.rootPath = path
        self.exp_name = exp_name
        self.params["prefix"]  = "ITL"
        self.params["type"]    = self.exp_name
        self.params["desc"]    = ""
        self.params["version"] = version #"SXXPYY"
        self.params["ext"]     = "json"
        self.fileName = ""
        self.template = 0
        self.writeVersion    = False
        self.writeTimeWindow = False
        fileName.__init__(self, self.params)


    def writeTimelineHeader(self, writeVersion, writeTimeWindow):
        self.writeHeader(self.params["scenarioID"], "JUICE " + self.exp_name + " SCENARIO TIMELINE")
        self.insertEmptyLine()

        if writeVersion == True:
            self.insertVersion()
            self.insertEmptyLine()

        if writeTimeWindow == True:
            self.insertTimeWindow(self.params["timeline"]["startTime"], self.params["timeline"]["endTime"])

    def generate_json_with_header(self, scenario_id, version):
        sxxpyy = version # "SXXPYY"
        filename = f"ITL_{self.exp_name}_{scenario_id}_{sxxpyy}.json"
        creation_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        json_structure = {
            "header": {
                "filename": filename,
                "creation_date": creation_date,
                "author": "JUICE SOC"
            }
        }

        return json_structure

    #def insertLine(self, line):
    #    with open(self.outputFilePath, "a", encoding="utf-8") as f:
    #        f.write(line + "\n")



    def writeContent(self):
        scenario_id = self.params["scenario_id"]

        # Generate JSON header
        full_json = self.generate_json_with_header(scenario_id, self.params["version"])

        # Output line-by-line (like your legacy method)
        for line in json.dumps(full_json, indent=4).splitlines():
            self.insertLine(line)


    #def writeContent(self):
    #    self.writeTimelineHeader(self.writeVersion, self.writeTimeWindow)



