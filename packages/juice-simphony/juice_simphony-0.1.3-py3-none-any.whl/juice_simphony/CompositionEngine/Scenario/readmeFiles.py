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
from juice_simphony.CompositionEngine.Scenario.graphicalPath import graphicalPath
import textwrap

def generate_readme(path, dirname, overview_text, contents_summary_text, additional_info_text):
    if dirname == path:
        dir_path = path
        title = "JUICE SCENARIO DIRECTORY STRUCTURE"
        tree_depth = 1
    else:
        dir_path = os.path.join(path, dirname)
        title = f"JUICE SCENARIO {dirname} DIRECTORY"
        tree_depth = None

    struct_file_path = os.path.normpath(os.path.join(dir_path, "aareadme.rst"))

    os.makedirs(dir_path, exist_ok=True)  # Ensure folder exists

    with open(struct_file_path, "w", encoding="utf-8") as structFile:
        # Header
        structFile.write(title + "\n")
        structFile.write("=" * len(title) + "\n\n")

        # Overview
        structFile.write("Overview\n")
        structFile.write("--------\n\n")
        structFile.write(overview_text.strip() + "\n\n")

        # Contents Summary
        structFile.write("Contents Summary\n")
        structFile.write("----------------\n\n")
        structFile.write(contents_summary_text.strip() + "\n\n")

        # Directory Structure
        structFile.write("Directory Structure\n")
        structFile.write("-------------------\n\n")
        structFile.write(f"Below a directory structure example for the `{os.path.basename(dir_path)}` directory::\n\n")

        #paths = graphicalPath.make_tree(dir_path)
        paths = graphicalPath.make_tree(dir_path, max_depth=tree_depth)
        for path in paths:
            structFile.write(path.displayable() + "\n")

        # Additional Info
        structFile.write("\nAdditional Information\n")
        structFile.write("----------------------\n\n")
        structFile.write(additional_info_text.strip() + "\n\n")


def generate_all_readmes(main_scenario_path):
    generate_readme(
        path=main_scenario_path,
        dirname=main_scenario_path,  # same as path
        overview_text=textwrap.dedent("""
    This `aareadme.rst` file describes the contents of the top-level directory of an operational scenario
    in the JUICE operational repository.
    """),
        contents_summary_text=textwrap.dedent("""
    The scenario directory has a given structure that is the result of gathering both the experience with
    missions in operations and the specific requirements of JUICE. The directory contains different types of
    files that serve different purposes.

    This directory also contains the top-level ITL and event files loaded by OSVE.
    """),
        additional_info_text=textwrap.dedent("""
    For more details of each directory within this directory refer to the `aareadme.rst` files within each
    subdirectory.
    """)
    )

    generate_readme(
        path=main_scenario_path,
        dirname="CONFIG",
        overview_text=textwrap.dedent("""
        This `aareadme.rst` file describes the contents of the configuration directory of an operational scenario 
        in the JUICE operational repository.
        """),
        contents_summary_text=textwrap.dedent("""
        This directory includes EPS, AGM, and other configuration models required for the execution
        of simulation tools. It includes both system-level and mission-specific data prepared for simulation.
        """),
        additional_info_text=textwrap.dedent("""
        This directory may include generated files or user-provided configuration templates.
        """)
    )

    generate_readme(
        path=main_scenario_path,
        dirname="ENVIRONMENT",
        overview_text=textwrap.dedent("""
        This `aareadme.rst` file describes the contents of the environment directory of an operational scenario
        in the JUICE operational repository.
        """),
        contents_summary_text=textwrap.dedent("""
        The Environment files are input files to OSVE that define or configure the "environment" of the
        scenario.

        There is a directory to include geometrical events as generated with the ``geopipeline`` package,
        which is populated at the start of the operational scenario activity.

        The ``OPS`` directory includes operational files that includes input related to the power and data models.
        In particular we have a file that provides the solar cell counts, one for the efficiency of the solar cells
        and another one for the bit rates of the S/C.

        In addition, there is a directory that provides the Data Volume Envelopes for each instrument type
        coming from the segmentation, these act as resources envelopes during the Instrument Timeline Harmonisation
        process.
        """),
        additional_info_text=textwrap.dedent("""
        These files can be also considered as configuration files.

        The trajectory files required by MAPPS were also included in this directory.

        Internally to the SOC the origin of these files is the
        Configuration repository `conf <https://gitlab.esa.int/juice-soc/juice-uplink/conf>`_.
        """)
    )

    generate_readme(
        path=main_scenario_path,
        dirname="MODELLING",
        overview_text=textwrap.dedent("""
    This `aareadme.rst` file describes the contents of the modelling directory of an operational scenario 
    in the JUICE operational repository.
    """),
        contents_summary_text=textwrap.dedent("""
    The configuration files required by AGM, EPS, and OSVE (and MAPPS) are
    present in the corresponding sub-directories within the ``CONFIG`` directory.

    From this directory, only the OSVE Configuration file is accessed directly by the
    user when running the OSVE simulation. In general, it is recommended to create
    a local version of the OSVE configuration file (session file), in order to avoid issues with the
    loading of SPICE kernels. The Python notebook associated with running OSVE already
    includes the feature of creating the local OSVE session file.
    """),
        additional_info_text=textwrap.dedent("""
    This directory may include generated files or user-provided configuration templates.
    """)
    )

    generate_readme(
        path=main_scenario_path,
        dirname="NOTEBOOKS",
        overview_text=textwrap.dedent("""
        This `aareadme.rst` file describes the contents of the Python notebooks directory of an operational scenario 
        in the JUICE operational repository.
        """),
        contents_summary_text=textwrap.dedent("""
        This directory contains a number of Python Notebooks to support the planning process of the given operational
        period or detailed scenario exercise. 

        This directory might also include Python modules used in certain notebooks.
        """),
        additional_info_text=textwrap.dedent("""
        To setup the required environmental variables. Copy the environmental variables' setup file `env.txt`
        to your home directory and edit the paths with your favorite editor. For example::

            cp <path_to_repo>/env.txt ~/.env
            vi ~/.env

        For more information please refer to the
        JUICE Public Notebooks repository: https://gitlab.esa.int/juice-soc/notebooks/juice-public-notebooks.
        """)
    )

    generate_readme(
        path=main_scenario_path,
        dirname="OBSERVATIONS",
        overview_text=textwrap.dedent("""
        This `aareadme.rst` file describes the contents of the observation definitions directory of an operational scenario
        in the JUICE operational repository.
        """),
        contents_summary_text=textwrap.dedent("""
        The Observation definition files used by OSVE to run the simulation have a specific directory in the structure.

        Each instrument has its own directory with two subdirectories: ``GLOBAL`` and ``SCENARIO``. The global
        sub-directory has all the observation definitions available to the instrument, whereas the scenario one has
        the ones that are linked to the segments present in the scenario.

        These files are considered planning files and can be delivered by the SOC or PIs throughout the entire
        Operational Scenario Process.
        """),
        additional_info_text=textwrap.dedent("""
        These observation definitions are initially generated from
        the `SOC Observation Database <https://juicesoc.esac.esa.int/readonly_admin/core/observationdefinition/>`_.
        """)
    )

    generate_readme(
        path=main_scenario_path,
        dirname="OUTPUT",
        overview_text=textwrap.dedent("""
        This `aareadme.rst` file describes the contents of the OSVE output directory of an operational scenario
        in the JUICE operational repository.
        """),
        contents_summary_text=textwrap.dedent("""
        This directory hosts all the output files generated by OSVE.

        By default this directory should be empty, except for this file.
        """),
        additional_info_text=textwrap.dedent("""
        N/A.
        """)
    )

    generate_readme(
        path=main_scenario_path,
        dirname="POINTING",
        overview_text=textwrap.dedent("""
        This `aareadme.rst` file describes the contents of the pointing directory of an operational scenario
        in the JUICE operational repository.
        """),
        contents_summary_text=textwrap.dedent("""
        This directory hosts all the Pointing Request Files (PTR) and the resulting SPICE C-Kernels (CK), it also
        hosts the Pointing Tool (OSVE) logs for the PTRs.

        This is the directory where the instrument teams deliver their pointing requests as well.
        These files are considered planning files and can be delivered by the SOC or PIs during the
        Pointing Timeline Harmonisation process.
        """),
        additional_info_text=textwrap.dedent("""
        N/A.
        """)
    )

    generate_readme(
        path=main_scenario_path,
        dirname="TIMELINE",
        overview_text=textwrap.dedent("""
        This `aareadme.rst` file describes the contents of the timeline directory of an operational scenario
        in the JUICE operational repository.
        """),
        contents_summary_text=textwrap.dedent("""
        This directory hosts all the planning files related to instrument operations to
        provide instrument modes, module states, data generation, and power consumption information.

        Different types of files are hosted in this directory such as the event fies, Activity Plan files (APL),
        Observation Plan files (OPL), Observation Timeline files (OTL), Instrument Timeline files (ITL), and
        Payload Operations Requests Files (POR).

        Each instrument has a sub-directory which is also the location where the files are delivered by the PI teams.
        """),
        additional_info_text=textwrap.dedent("""
        The TIMELINE directory has some particularities that need to be taken into account, it contains:

        - **Top-level ITL for the instruments**: this ITL points to the latest version of the individual instrument ITLs. These
        latest version are always the static ones with ``SXXPXX``.
        - **ITL for JUICE S/C Communications**: Contains the ground station links of the detailed scenario.
        - **ITL for JUICE S/C Platform Power**: Contains the power profile of the JUICE S/C platform for the detailed scenario.
        - **SOC Observation Plans**: These OPLs are a merge of all the OPLs of the Prime individual instruments as obtained from the
        SHT Timeline Tool.
        - **SOC event file**: The file that contains the events defined by the SOC for the detailed scenario.
        """)
    )



