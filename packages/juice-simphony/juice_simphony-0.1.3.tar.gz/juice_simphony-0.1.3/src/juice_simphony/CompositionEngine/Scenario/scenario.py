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
import re
import shutil
from pathlib import Path
from datetime import datetime
import pprint
from importlib import resources
from juice_simphony.CompositionEngine.SegmentationImporter.shtRestClient import shtRestClient

from juice_simphony.CompositionEngine.Scenario.common import utils
from juice_simphony.CompositionEngine.Scenario.environment.environment import environment
from juice_simphony.CompositionEngine.Scenario.config.configuration import configuration
from juice_simphony.CompositionEngine.Scenario.config.notebooks import notebooks
from juice_simphony.CompositionEngine.Scenario.modelling.modelling import modelling
from juice_simphony.CompositionEngine.Scenario.definitions.definitions import definitions
from juice_simphony.CompositionEngine.Scenario.timeline.timeline import timeline
from juice_simphony.CompositionEngine.Scenario.timeline.segmentation import segmentation
from juice_simphony.CompositionEngine.Scenario.root.toplevelItl import toplevelItl
from juice_simphony.CompositionEngine.Scenario.root.toplevelEvt import toplevelEvt
from juice_simphony.CompositionEngine.Scenario.graphicalPath import graphicalPath
from juice_simphony.CompositionEngine.Scenario.attitude.attitude import attitude
from juice_simphony.CompositionEngine.Scenario.root.seg_conf import seg_conf
from juice_simphony.CompositionEngine.SegmentationImporter.SegmentationImporter import segmentationTimeline
from juice_simphony.CompositionEngine.Scenario.readmeFiles import generate_all_readmes


base_package = (__package__ or "").split(".")[0]
config_file_path = resources.files(base_package) / "data"
default_config_path = config_file_path / "config_scenario.json"


class scenario:

    def __init__(self, root_path, parameters, force=False, mapps=False, zip=False):
        self.root_path = root_path + "/SCENARIOS"
        self.params = parameters
        self.mapps = mapps
        self.zip = zip
        self.genRootFolder = False
        self.force = force
        self.mainFolderPath = ""
        self.structure = {}
        self.elements  = {}
        self.segTimeline = segmentationTimeline()
        self.ingestScenario()
        self.params['cremaVersion']   = self.segTimeline.getTrajectory()
        self.params['cremaVersionId'] = self.params['cremaVersion'].upper().strip().replace('CREMA_', '').replace('_', '')
        self.params['scenarioID'] = self.params['scenario_id']
        self.params['genScenarioID']  = self.getGenericScenarioID()
        startTime = self.params['startTime']
        self.shtClient = shtRestClient(server="https://juicesoc.esac.esa.int")
        self.defs_config = self.shtClient.getDefinitionsConfig()



    def ingestScenario(self):
        self.segTimeline.ingestPlan(self.params["segmentID"], self.params["startTime"], self.params["endTime"])

        #print("Log messages set?", hasattr(self.segTimeline, "log_messages"))
        #print("Log messages count:", len(getattr(self.segTimeline, "log_messages", [])))

        self.params["source"] = {}
        self.params["source"]["segmentation_info"] = self.segTimeline.get_segmentation_info()
        self.params["source"]["trajectory_info"]   = self.segTimeline.get_trajectory_info()
        self.params["source"]["spice_info"]        = self.segTimeline.get_spice_info()
        self.params["spice_if"] = self.segTimeline.spice

        self.segTimeline.get_spice_info()

    def getGenericScenarioID(self):
        scenario = self.params['scenario_id'].split('_')[0]

        # Validate format: one letter followed by 3 digits
        if re.fullmatch(r'[A-Z]\d{3}', scenario, re.IGNORECASE):
            # Normalize to uppercase and return
            return scenario.upper()
        else:
            raise ValueError(
                f"Invalid scenario format: '{scenario}'. Expected format: 1 letter + 3 digits (e.g., 'E001').")

    def copy_and_process_templates(self, src_dir, dest_dir, replacement):
        src_dir = os.path.normpath(src_dir)
        dest_dir = os.path.normpath(dest_dir)

        os.makedirs(dest_dir, exist_ok=True)

        for filename in os.listdir(src_dir):
            src_file = os.path.join(src_dir, filename)

            if os.path.isfile(src_file):
                # Replace 'template' in filename
                new_filename = filename.replace("template", replacement)
                dest_file = os.path.join(dest_dir, new_filename)
                shutil.copy2(src_file, dest_file)

                # If it's a scenario file, replace 'template' in its content
                if "ODF_SCENARIO" in new_filename:
                    with open(dest_file, 'r', encoding='utf-8') as file:
                        content = file.read()

                    content = content.replace("template", replacement)
                    with open(dest_file, "w", encoding="utf-8") as f:
                        f.write(content)



    def save_filtered_segmentation_logs(self):
        log_file_path = os.path.join(self.mainFolderPath, "segment_log.txt")

        if hasattr(self.segTimeline, "log_messages") and self.segTimeline.log_messages:
            filtered_logs = [log for log in self.segTimeline.log_messages
                             if ("OPNAV" in log["message"]) or ("TCM" in log["message"]) or ("WOL" in log["message"])]

            part1_list = []  # To collect all part1 fields

            if filtered_logs:
                with open(log_file_path, "w", encoding="utf-8") as log_file:
                    for log in filtered_logs:
                        cleaned_msg = log["message"]
                        # Match pattern and transform message
                        match = re.match(
                            r"(\S+)\s+from\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+to\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)",
                            cleaned_msg
                        )
                        if match:
                            part1, part2, part3 = match.groups()
                            cleaned_msg = f"{part1},{part2},{part3}"
                            part1_list.append(part1)

                        log_file.write(cleaned_msg.strip() + "\n")

                unique_sorted_part1 = sorted(set(part1_list))

                print(f"[INFO] Filtered segment log saved to: {log_file_path}")
                print("[INFO] Unique sorted part1 values:")
                for item in unique_sorted_part1:
                    print(f"{item}")

            else:
                print("[INFO] No filtered segment logs matching OPNAV, TCM, or WOL found.")
        else:
            print("[INFO] No log messages available.")

        print("mission evf")

    def buildScenario(self):

        if self.genRootFolder:
            self.mainFolderRootPath = self.createRootFolder(self.root_path,self.params["genScenarioID"])
            self.mainFolderPath = self.createMainFolder(self.mainFolderRootPath,self.params["scenarioID"])

        else:
            self.mainFolderPath = self.createMainFolder(self.root_path,self.params["scenarioID"])
            self.mainFolderRootPath = self.mainFolderPath

        self.structure["root_path"]        = self.root_path
        self.structure["main_folder_name"] = self.params["scenarioID"]
        self.structure["path"]             = self.mainFolderPath;
        self.structure["environment"]      = self.addEnvironmentSection()
        self.structure["modelling"]        = self.addModellingSection()
        self.structure["definitions"]      = self.addDefinitionsSection()
        self.structure["notebooks"]        = self.addNotebooksSection()
        self.structure["attitude"]         = self.addAttitudeSection()
        self.structure["segmentation"]     = self.addSegmentationSection()
        timelineOutput                     = self.addTimelineSection()

        #self.save_filtered_segmentation_logs()

        self.structure["timeline"]         = timelineOutput["structure"]
        self.elements                      = timelineOutput["elements"]

        # Store the dict returned by addRootContent() in a variable before updating self.structure
        root_content = self.addRootContent()
        self.structure.update(root_content)

        structure = self.structure




        # Now call your ACC extractor with the updated structure
        self.extract_acc_final_values(structure)

        #print("Keys at top level:", structure.keys())
        #print("Keys under 'segmentation':", structure.get('segmentation', {}).keys())

        self.structure["configuration"] = self.addConfigurationSection()
        self.structure.update(self.generateSegImporterCfgFile())

        folderName = self.params['scenario_id'] + '_' + \
                     self.params["shortDesc"].upper().replace(' ', '_') + '_' + \
                     self.params["startDate"] + '_' + \
                     self.params["endDate"]


        obs_jui_scenario = os.path.normpath(os.path.join(self.structure["definitions"]["path"], "JUI/SCENARIO"))
        tmp_obs_jui_scenario = os.path.normpath(os.path.join(config_file_path, "templates/OBSERVATIONS/JUI/SCENARIO"))
        #self.copy_and_process_templates(tmp_obs_jui_scenario, obs_jui_scenario, replacement=self.params['scenario_id'])

        if os.path.isdir(tmp_obs_jui_scenario):
            self.copy_and_process_templates(
                tmp_obs_jui_scenario,
                obs_jui_scenario,
                replacement=self.params['scenario_id'])

        # Create output zip file
        self.zipFileName = folderName

        #generateScenarioStructure()
        #generateScenarioStructureConf(self.mainFolderPath)
        #generateScenarioStructureNotebook(self.mainFolderPath)
        #generateScenarioStructureModelling((self.mainFolderPath))

        #self.generate_event_lines_from_logs()
        generate_all_readmes(self.mainFolderPath)

        parentRootPath = Path(self.root_path)
        output_filename = os.path.normpath(os.path.join(parentRootPath.parent.absolute(), "SCENARIOS", self.zipFileName))

        if self.zip == True:
            zip_folder = os.path.join(self.root_path, folderName)
            shutil.make_archive(output_filename, 'zip', zip_folder)
            output_filename = output_filename + ".zip"
            shutil.rmtree(zip_folder)

        return output_filename

    import re


    def createTopFolder(self):
        TopFolderName = self.scenarioID
        return utils.createFolder(self.root_path, TopFolderName)

    def createMainFolder(self, refPath, scenarioID):
        # Build folder name (S0003_01_21C13_CALLISTO_FB_320110_320112)
        self.params["startDate"] = datetime.fromisoformat(self.params["startTime"]).strftime("%y%m%d")
        self.params["endDate"]   = datetime.fromisoformat(self.params["endTime"]).strftime("%y%m%d")
        folderName = scenarioID + '_' + \
                     self.params["shortDesc"].upper().replace(' ', '_') + '_' + \
                     self.params["startDate"] + '_' + \
                     self.params["endDate"]
        if self.force:
            utils.removeFolderTree(os.path.join(self.root_path, folderName))

        main_folder_path = utils.createFolder(refPath, folderName)
        utils.createFolder(main_folder_path, "OUTPUT")

        return main_folder_path

    def createRootFolder(self, refPath, scenarioID):
        # Build folder name (S0003_01_21C13_CALLISTO_FB)
        self.params["startDate"] = datetime.fromisoformat(self.params["startTime"]).strftime("%y%m%d")
        self.params["endDate"]   = datetime.fromisoformat(self.params["endTime"]).strftime("%y%m%d")
        folderName = scenarioID + '_' + \
                     self.params["shortDesc"].upper().replace(' ', '_')
        if self.force:
            utils.removeFolderTree(os.path.join(self.root_path, folderName))
        return utils.createFolder(refPath, folderName)

    def addConfigurationSection(self, mapps=False):
        confParams = self.params
        confParams["scenarioStructure"] = self.structure;
        confParams["elements"]          = self.elements;
        conf = configuration(self.mainFolderPath, confParams, mapps=self.mapps)
        return conf.build()

    def addEnvironmentSection(self, mapps=False):
        envParams = self.params
        env = environment(self.mainFolderPath,envParams, mapps=self.mapps)
        return env.build()

    def addNotebooksSection(self):
        notebooksParams = self.params
        notebook = notebooks(self.mainFolderPath, notebooksParams)
        return notebook.build()

    def addDefinitionsSection(self):
        defsParams = self.params
        defs = definitions(self.segTimeline, self.mainFolderPath, defsParams)
        return defs.build()

    def addModellingSection(self):
        modelParams = self.params
        mod = modelling(self.mainFolderPath, modelParams)
        return mod.build()

    def addAttitudeSection(self):
        attParams = self.params
        att = attitude(self.segTimeline, self.mainFolderPath, attParams)
        return att.build()

    def addTimelineSection(self):
        tmlParams = self.params
        tml = timeline(self.segTimeline, self.mainFolderPath, tmlParams)
        return tml.build()

    def addSegmentationSection(self):
        segParams = self.params
        seg = segmentation(self.segTimeline, self.mainFolderPath, segParams)
        return seg.build()

    def print_dv_per_category(self, file_list, category_key, heading, acc_prefixes):
        print(heading)

        mnemonics = {entry["mnemonic"].upper() for entry in self.defs_config[category_key]}
        totals = {mnemonic: 0.0 for mnemonic in mnemonics}
        unit = ""  # input unit, e.g. 'kbits'

        # Define conversion factors dict here or assume it exists in your class/module
        unit_conv_factor = {
            "kbits": {
                "gbits": 1 / 1_000_000
            },
        }
        target_unit = "Gbits"

        for file_entry in file_list:
            filename = file_entry.get("fileName", "").upper()

            if any(prefix in filename for prefix in acc_prefixes):
                matched_mnemonics = [m for m in mnemonics if m in filename]

                if matched_mnemonics:
                    try:
                        with open(filename, 'r') as f:
                            lines = f.readlines()
                            for line in reversed(lines):
                                line = line.strip()
                                if line:
                                    parts = line.split()
                                    if len(parts) >= 2:
                                        timestamp = parts[0]
                                        value = float(parts[1])
                                        unit = file_entry.get('dataUnit', '')  # e.g. 'kbits'
                                        for mnemonic in matched_mnemonics:
                                            totals[mnemonic] += value
                                    break
                    except FileNotFoundError:
                        print(f"⚠ File not found: {filename}")
                    except Exception as e:
                        print(f"⚠ Error reading file {filename}: {e}")

        combined_total = sum(value for value in totals.values() if value != 0)

        if combined_total != 0:
            print()
            # Get conversion factor if available, else default to 1 (no conversion)
            conv_factor = 1.0
            if unit in unit_conv_factor and target_unit.lower() in unit_conv_factor[unit]:
                conv_factor = unit_conv_factor[unit][target_unit.lower()]

            combined_total_converted = combined_total * conv_factor

            for mnemonic in sorted(totals):
                value_raw = totals[mnemonic]
                if value_raw != 0:
                    value_converted = value_raw * conv_factor
                    percentage = (value_raw / combined_total) * 100
                    print(f"   → DV {mnemonic}: {value_converted:.3f} {target_unit} ({percentage:.2f}%)")

            print()
            print(f"   → Total DV: {combined_total_converted:.3f} {target_unit}")
            print()

    def extract_acc_final_values(self, structure):
        try:
            file_list = structure["segmentation"]["elements"]["overlays"]["externals"]["fileList"]
        except KeyError:
            print("ACC file extraction: Invalid structure, no fileList found.")
            return

        print()
        # Each call resets its own totals inside print_dv_per_category
        self.print_dv_per_category(file_list, "targets", "DV PER TARGET", acc_prefixes=["ACC_TARG_"])
        self.print_dv_per_category(file_list, "instrument_types", "DV PER INSTRUMENT TYPE", acc_prefixes=["ACC_TYPE_"])
        self.print_dv_per_category(file_list, "instruments", "DV PER INSTRUMENT", acc_prefixes=["ACC_INST_"])

    def addRootContent(self):
        structure = dict()

        # Timeline top level
        # ------------------
        tlTmlParams = self.params
        tlTmlParams["timeline"] = {}
        tlTmlParams["timeline"]["version"]   = "V1"
        tlTmlParams["timeline"]["startTime"] = self.params["startTime"] + "Z"
        tlTmlParams["timeline"]["endTime"]   = self.params["endTime"] + "Z"
        includeList = []


        include_file = {}
        include_file["fileDescription"] = "Include Initial States"
        include_file["filePath"] = self.structure["timeline"]["initial_states"]
        includeList.append(include_file)

        include_file = {}
        include_file["fileDescription"] = "Include Instrument APL ITLs"
        include_file["filePath"] = self.structure["timeline"]["top_level_inst"]
        includeList.append(include_file)

        include_file = {}
        include_file["fileDescription"] = "Include JUICE SPC"
        include_file["filePath"] = self.structure["timeline"]["spc"]
        includeList.append(include_file)

        #if "plat_timeline" in self.structure["timeline"]:
        #    include_file = {}
        #    include_file["fileDescription"] = "Include JUICE SPC"
        #    include_file["filePath"] = self.structure["timeline"]["plat_timeline"]
        #    includeList.append(include_file)



        include_file = {}
        include_file["fileDescription"] = "Include JUICE COMS"
        include_file["filePath"] = self.structure["timeline"]["comms_timeline"]
        includeList.append(include_file)

        tlTml = toplevelItl(self.mainFolderPath, includeList, tlTmlParams)
        structure["toplevelItl"] = tlTml.genFile()

        tlTmlParams["prefix"] = "EVT"
        includeList = []

        include_file_1 = {"filePath": self.structure["environment"]["events"]["geopipelineEvents"]}
        includeList.append(include_file_1)
        include_file_2 = {"filePath": self.structure["environment"]["events"]["downlinkEvents"]}
        includeList.append(include_file_2)
        include_file_3 = {"filePath": self.structure["timeline"]["evt_timeline"]}
        includeList.append(include_file_3)

        tlEvf = toplevelEvt(self.mainFolderPath, includeList, tlTmlParams)
        structure["toplevelEvf"] = tlEvf.genFile()


        #with open("output.txt", "w") as f:
        #    pp = pprint.PrettyPrinter(stream=f, indent=2, width=80)
        #    pp.pprint(self.structure)

        return structure



    def generateSegImporterCfgFile(self):
        structure = {}
        seg_conf_file = seg_conf(self.mainFolderPath, self.params)
        structure["segCfgFile"] = seg_conf_file.gen(self.structure)
        return structure



