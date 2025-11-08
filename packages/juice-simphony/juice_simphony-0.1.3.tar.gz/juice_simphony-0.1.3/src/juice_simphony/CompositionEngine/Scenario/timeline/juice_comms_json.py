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


class juice_comms_json(fileHandleTml):

    def __init__(self, path, exp_name, params=0):
        self.params = {}
        if params != 0:
            self.params.update(params)
        self.path = path
        self.rootPath = path
        self.exp_name = exp_name
        self.params["prefix"] = "ITL"
        self.params["type"] = self.exp_name
        self.params["desc"] = "COMS"
        self.params["version"] = "SXXPYY"
        self.params["ext"] = "json"
        self.fileName = ""
        self.template = 0
        self.writeVersion = False
        self.writeTimeWindow = False
        fileHandleTml.__init__(self, path)


    def generate_comms_json(self, input_file):
        pattern = re.compile(r'\(COUNT=(\d+)\)')
        counts = []

        # Step 1: Extract unique COUNT values
        with open(input_file, 'r') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    count = int(match.group(1))
                    if count not in counts:
                        counts.append(count)

        # Step 2: Define the timeline template (pairs of start/end)
        timeline_template = [
            ("MAL_DL_START", "MAL_DL_20_START", "X_HGA_DOWNLINK"),
            ("MAL_DL_20_START", "MAL_DL_20_END", "X_KA_HGA_DOWNLINK"),
            ("MAL_DL_20_END", "MAL_DL_END", "X_HGA_DOWNLINK")
        ]

        # Step 3: Build JSON structure with timeline entries per count
        timeline = []
        for count in sorted(counts):
            for start, end, instr_name in timeline_template:
                entry = {
                    "name": instr_name,
                    "unique_id": instr_name,
                    "instrument": "COMS",
                    "type": "OBSERVATION",
                    "start_time": {
                        "name": start,
                        "counter": count,
                        "delta_time": "00:00:00"
                    },
                    "end_time": {
                        "name": end,
                        "counter": count,
                        "delta_time": "00:00:00"
                    }
                }
                timeline.append(entry)

        return timeline


    def writeTimelineHeader(self, writeVersion, writeTimeWindow):
        self.writeHeader(self.params["scenarioID"], "JUICE COMS TIMELINE")
        self.insertEmptyLine()

        if writeVersion == True:
            self.insertVersion()
            self.insertEmptyLine()

        if writeTimeWindow == True:
            self.insertTimeWindow(self.params["timeline"]["startTime"], self.params["timeline"]["endTime"])


    def generate_json_with_header(self, timeline_data, scenario_id):
        sxxpyy = "SXXPYY"
        filename = f"ITL_JUICE_COMS_{scenario_id}_{sxxpyy}.json"
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
        downlink_file = f"EVT_{scenario_id}_DOWNLINK.evf"
        input_file = os.path.join(self.rootPath, "../ENVIRONMENT/EVENTS/GEOMETRY", downlink_file)

        # === Step 1: Generate timeline from file
        timeline_data = self.generate_comms_json(input_file)  # should return list of dicts

        # === Step 2: Wrap with header
        full_json = self.generate_json_with_header(timeline_data, scenario_id)

        # === Step 3: Write JSON line-by-line
        for line in json.dumps(full_json, indent=2).splitlines():
            self.insertLine(line)

