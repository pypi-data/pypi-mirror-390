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
from juice_simphony.CompositionEngine.Scenario.common.fileHandleTml import fileHandleTml
import shutil
from datetime import datetime, timedelta


class juice_evt(fileHandleTml):

    def __init__(self, path, exp_name, params=0):
        self.params = {}
        if params != 0:
            self.params.update(params)
        self.path = path
        self.rootPath = path
        self.exp_name = exp_name
        self.params["prefix"] = "EVT"
        self.params["type"] = "SOC"
        self.params["desc"] = ""
        self.params["version"] = "SXXPYY"
        self.params["ext"] = "xml"
        self.fileName = ""
        self.template = 0
        self.writeVersion = False
        self.writeTimeWindow = False

        segm_log = "segment_log.xml"
        segm_log_path = os.path.join(self.rootPath, "../TIMELINE", segm_log)

        evt_mef = "EVT_SOC_mission_file.xml"
        src_path = os.path.join(self.rootPath, "../ENVIRONMENT", evt_mef)
        dst_path = os.path.join(self.rootPath, evt_mef)

        shutil.move(src_path, dst_path)
        self.params["evt_mission_event_file"] = dst_path

        evt_segm = "EVT_SOC_segmentation.xml"
        self.params["evt_segmentation"] = os.path.join(self.rootPath, evt_segm)

        file1 = self.params["evt_mission_event_file"]
        file2 = self.params["evt_segmentation"]

        self.combined_uvt_lines = self.combine_evt_files(file1, file2)

        # Remove temporary files
        os.remove(self.params["evt_mission_event_file"])
        os.remove(self.params["evt_segmentation"])
        #os.remove(segm_log_path)

        fileHandleTml.__init__(self, path)

    def generate_start_end_uvt_lines(self):
        validity_start = self.params["startTime"]
        validity_end = self.params["endTime"]

        # Convert to datetime objects
        dt_start = datetime.strptime(validity_start, "%Y-%m-%dT%H:%M:%S")
        dt_end = datetime.strptime(validity_end, "%Y-%m-%dT%H:%M:%S")

        # Subtract one second from dt_start
        dt_start = dt_start + timedelta(seconds=1)

        # Format with milliseconds
        scen_start = dt_start.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        scen_end = dt_end.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


        # Generate start/end IDs
        name_start, name_end, id_start, id_end = self.generate_start_end_ids()

        # Generate UVT lines
        line_start = f'<uvt name="{name_start}" id="{id_start}" time="{scen_start}" count="1" duration="0"/>'
        line_end = f'<uvt name="{name_end}" id="{id_end}" time="{scen_end}" count="1" duration="0"/>'

        # Return lines if needed
        return line_start, line_end



    def combine_evt_files(self, file1, file2):
        uvt_lines = []

        generated_lines = self.generate_start_end_uvt_lines()

        pattern = re.compile(
            r'<uvt name\s*=\s*"([^"]+)" id\s*=\s*"([^"]+)" time\s*=\s*"([^"]+)" count\s*=\s*"\d+" duration\s*=\s*"\d+"\/>'
        )

        # Process generated lines first
        for line in generated_lines:
            line = line.strip()
            if line.startswith('<uvt') and line.endswith('/>'):
                match = pattern.match(line)
                if match:
                    name, event_id, time_str = match.groups()
                    #time_dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
                    time_dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    uvt_lines.append((time_dt, event_id, line))

        # Read both files and extract lines
        for file_path in [file1, file2]:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('<uvt') and line.endswith('/>'):
                        match = pattern.match(line)
                        if match:
                            name, event_id, time_str = match.groups()
                            #time_dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
                            time_dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                            uvt_lines.append((time_dt, event_id, line))

        # Sort by datetime
        uvt_lines.sort(key=lambda x: x[0])

        # Dictionary to keep counts per id
        count_per_id = {}

        combined_lines = []
        for _, event_id, original_line in uvt_lines:
            count_per_id[event_id] = count_per_id.get(event_id, 0) + 1
            new_count = count_per_id[event_id]
            new_line = re.sub(r'count\s*=\s*"\d+"', f'count="{new_count}"', original_line)
            combined_lines.append(new_line)

        return combined_lines

    def generate_start_end_ids(self):
        # Use the first letter of scenario_id
        # Two characters before the underscore
        # If underscore is at position 0 or 1, just take first two chars or pad if short
        # Add S or E for START/END, respectively
        #scenario_id = self.params["scenario_id"]
        #first_char = scenario_id[0]

        #underscore_pos = scenario_id.find('_')
        #if underscore_pos >= 2:
        #    middle_chars = scenario_id[underscore_pos - 2:underscore_pos]
        #else:
        #    middle_chars = scenario_id[:2].ljust(2, '0')

        # Build IDs
        #name_start = f"{scenario_id}_START"
        #name_end = f"{scenario_id}_END"
        #id_start = f"{first_char}{middle_chars}S"
        #id_end = f"{first_char}{middle_chars}E"

        scenario_id = "SCENARIO"
        name_start = f"{scenario_id}_START"
        name_end = f"{scenario_id}_END"
        id_start = "SCES"
        id_end = "SCEE"


        return name_start, name_end, id_start, id_end

    def writeContent(self):
        scenario_id = self.params["scenario_id"]
        gen_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        validity_start = self.params["startTime"]
        validity_end = self.params["endTime"]

        additional_uvt_lines = self.combined_uvt_lines

        # === Manual string-based XML assembly
        xml_header = f'''<?xml version="1.0" encoding="UTF-8"?>
    <eventfile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://esa.esoc.events juice_event_definitions.xsd"
        xmlns="http://esa.esoc.events"
        xmlns:ems="http://esa.esoc.ems">

        <header format_version="1"
            gen_time="{gen_time}"
            icd_version="PLID-1.0"
            spacecraft="JUIC"
            validity_start="{validity_start}"
            validity_end="{validity_end}"/>

        <events>
        '''

        # <uvt name="{name_start}" id="{id_start}" time="{validity_start}" count="1" duration="0"/>
        # <uvt name="{name_end}"  id="{id_end}" time="{validity_end}" count="1" duration="0"/>

        # === Combine everything
        event_lines = [xml_header]
        for uvt_line in additional_uvt_lines:
            event_lines.append(f"            {uvt_line}")  # add indentation
        event_lines.append("")
        event_lines.append("    </events>")
        event_lines.append("</eventfile>")

        # === Final XML
        final_xml = "\n".join(event_lines)

        # === Write to file
        self.fileHdl.write(final_xml)



