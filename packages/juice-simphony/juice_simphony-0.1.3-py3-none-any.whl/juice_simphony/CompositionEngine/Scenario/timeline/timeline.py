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
from juice_simphony.CompositionEngine.Scenario.common import utils as utils
from juice_simphony.CompositionEngine.SegmentationImporter.SegmentationImporter import segmentationTimeline
from juice_simphony.CompositionEngine.Scenario.timeline import inst_timeline as inst_timeline
from juice_simphony.CompositionEngine.Scenario.timeline.inst_top_timeline import instToplevel
from juice_simphony.CompositionEngine.Scenario.timeline.plat_prof_timeline import plat_prof_timeline
from juice_simphony.CompositionEngine.Scenario.timeline.juice_comms_json import juice_comms_json
from juice_simphony.CompositionEngine.Scenario.timeline.juice_navcam import juice_navcam
from juice_simphony.CompositionEngine.Scenario.timeline.juice_evt import juice_evt


import os
from importlib import resources
import shutil
import json
import re
from datetime import datetime

base_package = (__package__ or "").split(".")[0]
config_file_path = resources.files(base_package) / "data"

class timeline:

    def __init__(self, segmentationTimelineInst, root_path, parameters=0):
        self.root_path = root_path
        self.params = parameters
        self.segTimeline = segmentationTimelineInst
        self.mainFolderPath = ""
        self.structure = {}
        self.elements  = {}
        self.expTimelines = []

    def build(self):
        self.createMainFolder('TIMELINE')
        self.structure["path"] = self.mainFolderPath;

        output = {}
        output["structure"] = self.structure
        output["elements"] = {}
        output["elements"]["overlays"] = self.elements
        exp_list = ["3GM","GAL","JAN","MAG","JMC","MAJ","NAV","PEH","PEL","RAD","RIM","RPW","SWI","UVS"]
        output["structure"].update(self.addTmlPlaceHolder(exp_list))

        # Copy instrument ITL json files existing in templates
        self.copyExpTimelineFiles(exp_list)

        self.params["includeFiles"] = self.expTimelines

        #output["structure"]["plat_timeline"] = self.createPlatProfTimeline(self.mainFolderPath,"JUICE")
        output["structure"]["comms_timeline"] = self.createCommsTimeline(self.mainFolderPath, "JUICE")

        initial_filename = "ITL_INIT_STATES_scenario_S00P00.itl"
        final_filename = initial_filename.replace("scenario", self.params["scenarioID"])
        orig_file = os.path.join(config_file_path, "templates/TIMELINE", initial_filename)
        dest_file = os.path.join(self.mainFolderPath, final_filename)
        shutil.copy2(orig_file, dest_file)

        new_filename = final_filename.replace("S00P00", "SXXPYY")
        dst_file_replacement = os.path.join(self.mainFolderPath, new_filename)
        shutil.copy2(dest_file, dst_file_replacement)

        output["structure"]["initial_states"] = dst_file_replacement

        initial_filename = "ITL_JUICE_SPC_scenario_S00P00.json"
        final_filename = initial_filename.replace("scenario", self.params["scenarioID"])
        orig_file = os.path.join(config_file_path, "templates/TIMELINE", initial_filename)
        dst_file = os.path.join(self.mainFolderPath, final_filename)
        shutil.copy2(orig_file, dst_file)
        #self.update_timeline_times(dst_file)

        new_filename = final_filename.replace("S00P00", "SXXPYY")
        dst_file_replacement = os.path.join(self.mainFolderPath, new_filename)
        shutil.copy2(dst_file, dst_file_replacement)

        with open(dst_file_replacement, "r", encoding="utf-8") as f:
            data_s00 = json.load(f)

        # Update filename in header (which is a dict)
        if "header" in data_s00 and isinstance(data_s00["header"], dict):
            filename_only = os.path.basename(dst_file_replacement)
            data_s00["header"]["filename"] = filename_only

        with open(dst_file_replacement, "w", encoding="utf-8") as f:
            json.dump(data_s00, f, indent=4)


        output["structure"]["spc"] = dst_file_replacement



        self.generate_event_lines_from_logs()

        output["structure"]["evt_timeline"] = self.createEvtTimeline(self.mainFolderPath, "JUICE")

        self.createNavcamTimeline(os.path.join(self.mainFolderPath, "NAV"), "JUICE")

        inst_top = instToplevel(self.root_path, self.mainFolderPath, self.params)
        output["structure"]["top_level_inst"] = inst_top.genFile()

        # Create NAVCAM
        #self.createNavcamTimeline(os.path.join(self.mainFolderPath, "NAV"), "JUICE")



        return output

    def createMainFolder(self, folderName):
        self.mainFolderPath = utils.createFolder(self.root_path, folderName)

    def addSegmentationTimeline(self):
        return self.segTimeline.generateSegmentTimeline(self.mainFolderPath, self.params["scenarioID"])

    # removed due to timeline/tms
    #def addOverlays(self):
    #    return self.segTimeline.generateProfileCsv(self.mainFolderPath, self.params["scenarioID"])

    def addTmlPlaceHolder(self, exp_list):
        structure = {}
        for exp in exp_list:
            structure[exp] = {}
            structure[exp]["path"] = utils.createFolder(self.mainFolderPath, exp)
            self.expTimelines.append(self.createPlaceHolderTimeline(structure[exp]["path"],exp))
            self.createPlaceHolderTimelinev0(structure[exp]["path"], exp)
        return structure

    def createPlaceHolderTimeline(self, pathFile, exp):
        tml = inst_timeline.timelineFile(path=pathFile, exp_name=exp, version="SXXPYY", params=self.params)
        return tml.genFile()

    def createPlaceHolderTimelinev0(self, pathFile, exp):
        tml_00 = inst_timeline.timelineFile(path=pathFile, exp_name=exp, version="S00P00", params=self.params)
        return tml_00.genFile()

    def copyExpTimelineFiles(self, exp_list):
        structure = {}
        for exp in exp_list:
            structure[exp] = {}
            structure[exp]["path"] = utils.createFolder(self.mainFolderPath, exp)
            defFilePath = structure[exp]["path"]

            template_timeline_exp_dir = os.path.normpath(os.path.join(config_file_path, "templates/TIMELINE", exp))

            # Only proceed if the directory exists
            if os.path.isdir(template_timeline_exp_dir):
                for filename_orig in os.listdir(template_timeline_exp_dir):
                    if filename_orig.lower().endswith(".json"):
                        src_file = os.path.join(template_timeline_exp_dir, filename_orig)

                        # 1) Copy original file with original filename (S00P00)
                        filename = filename_orig.replace("scenario", self.params["scenarioID"])
                        dst_file = os.path.join(defFilePath, filename)
                        shutil.copy2(src_file, dst_file)
                        #self.update_timeline_times(dst_file)

                        # 2) Copy file with S00P00 replaced by SXXPYY
                        new_filename = filename.replace("S00P00", "SXXPYY")
                        dst_file_replacement = os.path.join(defFilePath, new_filename)
                        shutil.copy2(dst_file, dst_file_replacement)


                        with open(dst_file, "r", encoding="utf-8") as f:
                            data_s00 = json.load(f)

                        # Update filename in header (which is a dict)
                        if "header" in data_s00 and isinstance(data_s00["header"], dict):
                            filename_only = os.path.basename(dst_file)
                            data_s00["header"]["filename"] = filename_only

                        with open(dst_file, "w", encoding="utf-8") as f:
                            json.dump(data_s00, f, indent=4)

                        with open(dst_file_replacement, "r", encoding="utf-8") as f:
                            data_sxx = json.load(f)

                        # Update filename in header (which is a dict)
                        if "header" in data_sxx and isinstance(data_sxx["header"], dict):
                            filename_only = os.path.basename(dst_file_replacement)
                            data_sxx["header"]["filename"] = filename_only

                        with open(dst_file_replacement, "w", encoding="utf-8") as f:
                            json.dump(data_sxx, f, indent=4)


    def generate_event_lines_from_logs(self):
        # this function creates an output file reading the segmentation and printing those events including
        # the following: OPNAV, TCM, WOL

        # filename for output containing the segment info as returned by the segmentation
        log_file_path = os.path.join(self.root_path, "TIMELINE", "segment_log.xml")
        # filename for output in EVT format
        log_file_path_uvt = os.path.join(self.root_path, "TIMELINE", "EVT_SOC_segmentation.xml")

        if not (hasattr(self.segTimeline, "log_messages") and self.segTimeline.log_messages):
            print("[INFO] No log messages available.")
            return

        filtered_logs = [log for log in self.segTimeline.log_messages
                         if ("OPNAV" in log["message"]) or ("TCM" in log["message"]) or ("WOL" in log["message"])]

        part1_list = []
        event_lines = []

        if not filtered_logs:
            print("[INFO] No filtered segment logs matching OPNAV, TCM, or WOL found.")
            return

        with open(log_file_path, "w", encoding="utf-8") as log_file:
            for log in filtered_logs:
                cleaned_msg = log["message"]
                # Parse message pattern
                match = re.match(
                    r"(\S+)\s+from\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+to\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)",
                    cleaned_msg
                )
                if not match:
                    continue
                part1, start_time, end_time = match.groups()
                cleaned_msg_csv = f"{part1},{start_time},{end_time}"
                log_file.write(cleaned_msg_csv.strip() + "\n")
                part1_list.append(part1)

                # Now generate START/END IDs and lines based on event type
                if part1.startswith("OPNAV_"):
                    # ID: ON + first letter after underscore + S/E
                    # OPNAV_CAL --> ONCS (OPNAV_CAL_START), ONCE (OPNAV_CAL_END)
                    event_code = part1.split("_")[1]
                    if event_code:
                        start_id = "ON" + event_code[0] + "S"
                        end_id = "ON" + event_code[0] + "E"
                        name_start = f"{part1}_START"
                        name_end = f"{part1}_END"
                        event_lines.append(f"{name_start} {start_id} {start_time}")
                        event_lines.append(f"{name_end} {end_id} {end_time}")

                elif part1.startswith("J_FD_"):
                    # J_FD_WOL --> FWOS (J_FD_WOL_START), FWOE (J_FD_WOL_END)
                    # J_FD_TCM --> FTCS (J_FD_TCM_START), FTCE (J_FD_TCM_END)
                    # J_FD_WOL_FB_START --> FWFS (J_FD_WOL_FB_START), FWFE (J_FD_WOL_FB_END)
                    parts = part1.split("_")

                    if len(parts) == 3:
                        event_code = parts[2]
                        two_letters = event_code[:2].upper()

                    elif len(parts) == 4:
                        first_letter = parts[2][0].upper() if parts[2] else '_'
                        second_letter = parts[3][0].upper() if parts[3] else '_'
                        two_letters = first_letter + second_letter

                    else:
                        # Fallback for unexpected format
                        two_letters = '__'

                    # Add S for START and E for END
                    start_id = "F" + two_letters + "S"
                    end_id = "F" + two_letters + "E"
                    name_start = f"{part1}_START"
                    name_end = f"{part1}_END"
                    event_lines.append(f"{name_start} {start_id} {start_time}")
                    event_lines.append(f"{name_end} {end_id} {end_time}")
                    #print(part1, name_start, name_end, start_id, end_id)


        # Remove duplicates first
        unique_lines = list(set(event_lines))

        # Sort by the timestamp (the second element after split)
        unique_lines.sort(key=lambda line: datetime.strptime(line.split()[2], "%Y-%m-%dT%H:%M:%SZ"))

        count = 1
        with open(log_file_path_uvt, "w", encoding="utf-8") as f:
            for line in unique_lines:
                event_name, event_id, timestamp = line.split()
                event_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                #formatted_time = event_time.strftime("%Y-%jT%H:%M:%S.%f")[:-3] + "Z"
                formatted_time = event_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                xml_line = f'\t\t<uvt name="{event_name}" id="{event_id}" time="{formatted_time}" count="{count}" duration="0"/>'
                f.write(xml_line + "\n")
                count += 1

        return event_lines

    def update_timeline_times(self, json_filepath):
        """
        Update start_time and end_time in the timeline entries of the JSON file
        with values from self.params['startTime'] and self.params['endTime'],
        removing any trailing 'Z'.
        """
        try:
            with open(json_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Update filename in header (which is a dict)
            if "header" in data and isinstance(data["header"], dict):
                filename_only = os.path.basename(json_filepath)
                data["header"]["filename"] = filename_only

            # Clean the times, remove trailing 'Z' if present
            start_time = self.params.get("startTime", "").rstrip('Z')
            end_time = self.params.get("endTime", "").rstrip('Z')

            modified = False
            for entry in data.get("timeline", []):
                if "start_time" in entry and start_time:
                    entry["start_time"] = start_time
                    modified = True
                if "end_time" in entry and end_time:
                    entry["end_time"] = end_time
                    modified = True

            if modified:
                with open(json_filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

        except Exception as e:
            print(f"Failed to update times in {json_filepath}: {e}")

    #def createPlatProfTimeline(self, pathFile, exp):
    #    self.params["power_profile"] = self.segTimeline.genPlatformPowerProfile(self.params["startTime"], self.params["endTime"])
    #    platform_timeline = plat_prof_timeline(path=pathFile, exp_name=exp, params=self.params)
    #    return platform_timeline.genFile()

    def createNavcamTimeline(self, pathFile, exp):
        version_xy = "SXXPYY"
        navcam = juice_navcam(path=pathFile, exp_name=exp, params=self.params, version=version_xy,
                              segTimeline=self.segTimeline)
        version_00 = "S00P00"
        navcam_00 = juice_navcam(path=pathFile, exp_name=exp, params=self.params, version=version_00,
                              segTimeline=self.segTimeline)
        return navcam.genFile(), navcam_00.genFile()

    def createCommsTimeline(self, pathFile, exp):
        #comms = juice_comms(path=pathFile, exp_name=exp, params=self.params)
        comms = juice_comms_json(path=pathFile, exp_name=exp, params=self.params)
        return comms.genFile()

    def createEvtTimeline(self, pathFile, exp):
        evt_timeline = juice_evt(path=pathFile, exp_name=exp, params=self.params)
        return evt_timeline.genFile()