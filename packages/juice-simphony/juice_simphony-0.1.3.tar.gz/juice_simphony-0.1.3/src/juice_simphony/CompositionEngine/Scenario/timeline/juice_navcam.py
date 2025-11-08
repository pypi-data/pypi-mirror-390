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
import re
import json
from datetime import datetime
from juice_simphony.CompositionEngine.Scenario.common.fileHandleTml import fileHandleTml
from juice_simphony.CompositionEngine.SegmentationImporter.SegmentationImporter import segmentationTimeline

class juice_navcam(fileHandleTml):

    def __init__(self, path, exp_name, version, params=0, segTimeline=None):
        self.params = {}
        if params != 0:
            self.params.update(params)
        self.path = path
        self.rootPath = path
        self.exp_name = exp_name
        self.params["prefix"] = "ITL"
        self.params["type"] = "NAV"
        self.params["desc"] = ""
        self.params["version"] = version # "SXXPYY"
        self.params["ext"] = "json"
        self.fileName = ""
        self.template = 0
        self.writeVersion = False
        self.writeTimeWindow = False
        self.segTimeline = segTimeline
        fileHandleTml.__init__(self, path)

    def generate_navcam(self, input_file):
        timeline = []

        # Regex to parse your log lines
        # Example log: OPNAV_CAL from 2032-12-18T22:05:31Z to 2032-12-18T23:35:31Z
        log_pattern = re.compile(
            r'OPNAV_[A-Z]+ from (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) to (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)'
        )

        counter = 1  # Start counter at 1

        if hasattr(self.segTimeline, "log_messages") and self.segTimeline.log_messages:
            for log in self.segTimeline.log_messages:
                msg = log.get("message", "")
                match = log_pattern.search(msg)
                #print(match)
                if match:
                    #raw_start_time = match.group(1)
                    #raw_end_time = match.group(2)

                    entry = {
                        "name": "NAV_OPNAV_BLOCK",
                        "unique_id": "NAV_OPNAV_BLOCK",
                        "instrument": "NAVCAM",
                        "type": "OBSERVATION",
                        "start_time": {
                            "name": "ONCS",
                            "counter": counter,
                            "delta_time": "000.00:00:00.000"
                        },
                        "end_time": {
                            "name": "ONCE",
                            "counter": counter,
                            "delta_time": "000.00:00:00.000"
                        }
                    }
                    timeline.append(entry)
                    counter += 1  # Increment after each match

        # Optionally, handle the rest of input_file parsing if needed, or ignore
        # ...

        return timeline


    def writeTimelineHeader(self, writeVersion, writeTimeWindow):
        self.writeHeader(self.params["scenarioID"], "JUICE COMMS TIMELINE")
        self.insertEmptyLine()

        if writeVersion == True:
            self.insertVersion()
            self.insertEmptyLine()

        if writeTimeWindow == True:
            self.insertTimeWindow(self.params["timeline"]["startTime"], self.params["timeline"]["endTime"])

    def generate_json_with_header(self, timeline_data, scenario_id, version=None):
        if version is None:
            version = self.params.get("version", "SXXPYY")
        filename = f"ITL_NAV_{scenario_id}_01_{version}.json"
        creation_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        json_structure = {
            "header": {
                "filename": filename,
                "creation_date": creation_date,
                "author": "JUICE SOC"
            },
            "timeline": timeline_data
        }

        return json_structure


    def writeContent(self):
        scenario_id = self.params["scenario_id"]
        # Skipping input_file since logs provide timeline data
        timeline_data = self.generate_navcam(None)  # passing None or just ignore input_file

        full_json = self.generate_json_with_header(timeline_data, scenario_id)

        for line in json.dumps(full_json, indent=4).splitlines():
            self.insertLine(line)







