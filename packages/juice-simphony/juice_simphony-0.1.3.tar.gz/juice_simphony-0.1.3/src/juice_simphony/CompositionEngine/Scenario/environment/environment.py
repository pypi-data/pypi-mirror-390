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
import json
from pathlib import Path
import shutil
from datetime import datetime
import re
from importlib import resources

from juice_simphony.CompositionEngine.Scenario.common import utils
from juice_simphony.CompositionEngine.Scenario.environment.trajectory import trajectory

base_package = (__package__ or "").split(".")[0]
config_file_path = resources.files(base_package) / "data"

def find_file_with(directory, filestring):
    for filename in os.listdir(directory):
        if filestring in filename:  # case-insensitive
            return os.path.join(directory, filename)

    return None

def replace_in_file(file_path, target_word, replacement):
    # Read the file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Replace the target word
    updated_content = content.replace(target_word, replacement)

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(updated_content)


def parse_custom_config(file_path):
    config = {
        "Mission": None,
        "Planning_periods": [],
        "Resolve_to_event": None,
        "Power_algorithm": None,
        "Power_model": {},
        "Resources": [],
        "Output_format": []
    }

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("Mission:"):
                config["Mission"] = line.split(":", 1)[1].strip()

            elif line.startswith("Planning_periods:"):
                parts = line.split(":", 1)[1].strip().split()
                config["Planning_periods"] = parts

            elif line.startswith("Resolve_to_event:"):
                config["Resolve_to_event"] = line.split(":", 1)[1].strip()

            elif line.startswith("Power_algorithm:"):
                config["Power_algorithm"] = line.split(":", 1)[1].strip()

            elif line.startswith("Power_model:"):
                parts = line.split(":", 1)[1].strip().split(maxsplit=1)
                key = parts[0]
                value = parts[1] if len(parts) > 1 else None
                config["Power_model"][key] = value

            elif line.startswith("Resource:"):
                parts = line.split(":", 1)[1].strip().split()
                # Example structure:
                # ['PM_SA_CELL_COUNT', '23560', '"cfg_eps_res_sa_cells_count.asc"']
                resource = {
                    "name": parts[0],
                    "value": parts[1] if len(parts) > 1 else None,
                    "file": parts[2].strip('"') if len(parts) > 2 and parts[2].startswith('"') else None,
                    "type": parts[3] if len(parts) > 3 else None,
                    "rate": float(parts[4]) if len(parts) > 4 and parts[4].replace('.', '', 1).isdigit() else None,            
                    "units": parts[5] if len(parts) > 5 else None,
                    "brfile": parts[6].strip('"') if len(parts) > 6 and parts[6].startswith('"') and parts[6].endswith('.brf"') else None,
                    "id": int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else None,
                    "raw": parts                    # store full token list for debugging/reference
                }
                config["Resources"].append(resource)

            elif line.startswith("Output_format:"):
                parts = line.split(":", 1)[1].strip().split()
                config["Output_format"].append(parts)

    return config


class environment:

    def __init__(self, root_path, parameters=0, mapps=False):
        self.root_path = root_path
        self.parameters = parameters
        self.mainFolderPath = ""
        self.structure = dict()
        self.mapps = mapps

    def build(self):
        self.mainFolderPath = self.createMainFolder('ENVIRONMENT')
        self.structure["path"]       = self.mainFolderPath
        self.structure["ops"]        = self.addOpsSection('OPS')
        self.structure["events"]     = self.addEventsSection('EVENTS')
        #self.structure["segmentation"] = self.addSegmentationSection('SEGMENTATION')
        if self.mapps == True:
            self.structure["trajectory"] = self.addTrajectorySection('TRAJECTORY')
        return self.structure

    def createMainFolder(self, folderName):
        return utils.createFolder(self.root_path, folderName)


    def trim_downlink_events_file(self, file_path, start_time_str, end_time_str, output_path):
        time_format_iso = "%Y-%m-%dT%H:%M:%S"
        start_time = datetime.strptime(start_time_str, time_format_iso)
        end_time = datetime.strptime(end_time_str, time_format_iso)

        output_lines = []
        keep_block = False
        current_block = []

        with open(file_path, 'r') as file:
            for line in file:
                line = line.rstrip()

                # Start of a new block
                if line.startswith("# DL_ segment start"):
                    current_block = [line]
                    keep_block = False  # Reset flag for new block

                elif "MAL_DL_START" in line:
                    match = re.match(r"(\d{2}-[A-Za-z]{3}-\d{4}_\d{2}:\d{2}:\d{2})\s+MAL_DL_START", line)
                    if match:
                        dt_str = match.group(1)
                        dt_obj = datetime.strptime(dt_str, "%d-%b-%Y_%H:%M:%S")
                        if start_time <= dt_obj <= end_time:
                            keep_block = True
                    current_block.append(line)

                elif line.startswith("# DL_ segment end"):
                    current_block.append(line)
                    if keep_block:
                        output_lines.extend(current_block)
                        output_lines.append("")  # Add empty line after each block
                    current_block = []  # Reset for next block

                else:
                    current_block.append(line)

        # Write filtered result to output file
        with open(output_path, 'w') as out_file:
            for line in output_lines:
                out_file.write(line + '\n')



    def trim_geopipeline_event_file(self, input_path, start_time_str, end_time_str, output_path):
        time_format_input = "%d-%b-%Y_%H:%M:%S"
        time_format_iso = "%Y-%m-%dT%H:%M:%S"

        # Convert ISO strings to datetime objects
        start_time = datetime.strptime(start_time_str, time_format_iso)
        end_time = datetime.strptime(end_time_str, time_format_iso)

        output_lines = []

        with open(input_path, "r") as infile:
            for line in infile:
                line = line.rstrip()

                if line.startswith("#"):
                    # Always keep comments
                    output_lines.append(line)
                    continue

                # Try to extract the timestamp (must be the first "word" on the line)
                match = re.match(r"(\d{2}-[A-Za-z]{3}-\d{4}_\d{2}:\d{2}:\d{2})", line)
                if match:
                    dt_str = match.group(1)
                    try:
                        dt_obj = datetime.strptime(dt_str, time_format_input)
                        if start_time <= dt_obj <= end_time:
                            output_lines.append(line)
                    except ValueError:
                        # Skip malformed datetime entries
                        continue

        # Write output
        with open(output_path, "w") as outfile:
            for line in output_lines:
                outfile.write(line + "\n")

    def generate_id(self, keyword):
        if "FLYBY" in keyword:
            parts = keyword.split('_')
            if len(parts) > 1:
                return 'F' + parts[1][:3]
            else:
                return "F___"

        if "APOJOVE" in keyword or "PERIJOVE" in keyword:
            parts = keyword.split('_')
            if len(parts) > 1:
                return parts[1][:4]
            else:
                return "____"

        if keyword.startswith("FLIP_"):

            first_letter = keyword[0].upper()

            parts = keyword.split('_')
            # Part before first underscore
            before_underscore = parts[0]
            second_letter = before_underscore[-1].upper() if before_underscore else '_'
            # Part after first underscore
            after_underscore = parts[1] if len(parts) > 1 else ''
            third_letter = after_underscore[0].upper() if after_underscore else '_'

            # Determine final letter
            if 'START' in keyword.upper():
                fourth_letter = 'S'
            elif 'END' in keyword.upper():
                fourth_letter = 'E'
            else:
                fourth_letter = '_'

            if len(parts) >= 3:
                return first_letter + second_letter + third_letter + fourth_letter
            else:
                return "F___"

        return keyword[:4]

    def trim_mission_file_by_time_range(self, file_path, start_time_str, end_time_str, output_path):
        time_format_iso_z = "%Y-%m-%dT%H:%M:%SZ"  # timestamps format in your file
        keywords = ["FLYBY", "PERIJOVE", "APOJOVE", "FLIP"]

        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S")

        output_lines = []
        count = 1  # initialize counter

        fileNameEvt = f"EVT_SOC_mission_file.xml"
        evt_mission_events = os.path.join(self.mainFolderPath, fileNameEvt)
        with open(evt_mission_events, 'w') as evt_file:  # Open file to write XML lines
            with open(file_path, 'r') as file:
                for line in file:
                    if not line or line.startswith("#"):
                        continue

                    parts = line.strip().split(",")
                    if len(parts) < 2:
                        continue

                    event_name = parts[0].strip()
                    timestamp_str = parts[1].strip()

                    try:
                        event_time = datetime.strptime(timestamp_str, time_format_iso_z)
                        if start_time <= event_time <= end_time:
                            if any(keyword in event_name for keyword in keywords):
                                event_id = self.generate_id(event_name)
                                #print(event_name, event_id)
                                output_lines.append(f"{event_id},{event_name},{timestamp_str}")

                                # Format time as "YYYY-DDDThh:mm:ss.sssZ"
                                #formatted_time = event_time.strftime("%Y-%jT%H:%M:%S.%f")[:-3] + "Z"
                                formatted_time = event_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

                                xml_line = f'\t\t<uvt name="{event_name}" id="{event_id}" time="{formatted_time}" count="{count}" duration="0"/>'

                                # Save to file
                                evt_file.write(xml_line + '\n')

                                count += 1

                    except ValueError:
                        print(f"[WARN] Skipping line with invalid date: {line}")
                        continue

        with open(output_path, 'w') as out_file:
            for line in output_lines:
                out_file.write(line + '\n')

    def addEventsSection(self, folderName):
        print("")
        print("Add ENVIRONMENT section")
        structure = dict()
        structure["path"] = utils.createFolder(self.mainFolderPath, folderName)

        geometryPath = utils.createFolder(structure["path"], "GEOMETRY")
        structure["geometryPath"] = geometryPath
        scenario_id = self.parameters['scenarioID']
        crema_version = self.parameters['cremaVersion'].upper()
        crema_id = crema_version.strip().replace('CREMA_', '')
        desc = self.parameters['shortDesc']
        start = self.parameters["startTime"]
        end = self.parameters['endTime']
        juice_conf = self.parameters['conf_repo']['juice_conf']

        # GEOPIPELINE file
        geo_evt_params = {}
        geo_evt_params["version"] = ""
        geo_evt_params["scenarioID"] = scenario_id
        fileName = f"EVT_EPS_FORMAT_GEOPIPELINE_{crema_id}.EVF"
        filePath = os.path.normpath(os.path.join(juice_conf, "internal/geopipeline/output", crema_version, fileName))
        fileNameOutput = os.path.join(geometryPath, f"EVT_{scenario_id}_GEOPIPELINE.evf")
        self.trim_geopipeline_event_file(filePath, start, end, fileNameOutput)
        structure["geopipelineEvents"] = fileNameOutput

        # DOWNLINK file
        fileName = "downlink.evf"
        fileNameOutput = f"EVT_{scenario_id}_DOWNLINK.evf"
        refFile = os.path.normpath(os.path.join(juice_conf, "internal/timeline/output", crema_version, "eps_package/instrument_type", fileName))
        destFile = os.path.join(geometryPath, fileNameOutput)
        self.trim_downlink_events_file(refFile, start, end, destFile)
        structure["downlinkEvents"] = destFile

        # MISSION TIMELINE event file
        crema_id_lowercase = crema_id.lower()
        fileName = f"mission_timeline_event_file_{crema_id_lowercase}.csv"
        fileNameOutput = f"MISSION_TIMELINE_EVENT_FILE_{scenario_id}_{desc}.csv"
        fileNameOutputTrim = f"MISSION_TIMELINE_EVENT_FILE_{scenario_id}_{desc}_filtered.csv"
        refFile = os.path.normpath(os.path.join(juice_conf, "internal/geopipeline/output", crema_version, fileName))
        destFile = os.path.join(geometryPath, fileNameOutput)
        utils.copyFile(refFile, destFile)
        structure["missionEvf"] = destFile

        destFileTrim = os.path.join(geometryPath, fileNameOutputTrim)

        self.trim_mission_file_by_time_range(destFile, start, end, destFileTrim)
        structure["missionEvfFilter"] = destFileTrim

        return structure


    def addOpsSection(self, folderName):
        structure = dict()
        structure["path"] = utils.createFolder(self.mainFolderPath, folderName)
        dest_folder = structure["path"]
        root_path = self.root_path
        crema_version = self.parameters['cremaVersion'].upper()
        scenario_id = self.parameters['scenarioID']
        juice_conf = self.parameters['conf_repo']['juice_conf']

        # SA cell count
        mypath = os.path.normpath(os.path.join(juice_conf, "internal/geopipeline/output", crema_version))
        filestr = "count"
        pm_sa_cell_count_file = find_file_with(mypath, filestr)

        structure["saCellsCount"] = "#"
        if pm_sa_cell_count_file:
            src_file = os.path.join(mypath, pm_sa_cell_count_file)
            os.makedirs(dest_folder, exist_ok=True)
            dest_file = os.path.join(dest_folder, os.path.basename(src_file))

            if os.path.abspath(src_file) != os.path.abspath(dest_file):
                shutil.copyfile(src_file, dest_file)
                structure["saCellsCount"] = dest_file

        # Cell efficiency
        filestr = "EFFICIENCY"
        mypath = os.path.normpath(os.path.join(juice_conf, "internal/geopipeline/output", crema_version))
        pm_sa_cell_eff_file = find_file_with(mypath, filestr)
        src_file = os.path.join(mypath, pm_sa_cell_eff_file)
        dest_file = os.path.join(dest_folder, os.path.basename(src_file))

        structure["saCellsEff"] = "#"
        if os.path.abspath(src_file) != os.path.abspath(dest_file):
            shutil.copyfile(src_file, dest_file)
            structure["saCellsEff"] = dest_file

        # Bitrate file
        filestr = "BRF_MAL"
        #mypath = os.path.join(config_file_path, "templates", crema_version)
        mypath = os.path.normpath(os.path.join(juice_conf, "internal/geopipeline/output"))
        downlink_brf_file = find_file_with(mypath, filestr)
        src_file = os.path.join(config_file_path,"templates", crema_version, downlink_brf_file)
        dest_file = os.path.join(dest_folder, os.path.basename(src_file))

        structure["brf"] = "#"
        if os.path.abspath(src_file) != os.path.abspath(dest_file):
            shutil.copyfile(src_file, dest_file)
            structure["brf"] = dest_file

        return structure

    def addTrajectorySection(self,folderName):
        structure = dict()
        structure["path"] = utils.createFolder(self.mainFolderPath, folderName)
        confParams = self.parameters
        confParams["scenarioStructure"] = self.structure
        traj = trajectory(structure["path"], confParams)
        return traj.build()
