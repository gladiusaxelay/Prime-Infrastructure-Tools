#!/usr/bin/env python
#
#     Prime Configuration Extractor
#       v0.1
#
#     Christian Jaeckel (chjaecke@cisco.com)
#       May 2016
#
#     This tool extracts all available running and
#       startup configurations from the Prime
#       Infrastructure.
#
#     REQUIREMENTS:
#     It needs the PrimeAPI module to control access
#       to the Prime Infrastructure API.
#
#     WARNING:
#       Any use of these scripts and tools is at
#       your own risk. There is no guarantee that
#       they have been through thorough testing in a
#       comparable environment and we are not
#       responsible for any damage or data loss
#       incurred with their use.
#
import os
import logging
from PrimeAPI import PrimeAPI

def get_api_configurations(api):
    """
    Fetches configuration files from the Prime Infrastructure API and stores them in a dictionary list.
    The dictionary has the following keys:
        "deviceId" : Device ID
        "deviceIpAddress" : Device IP address
        "deviceName" : Device name
        "fileId" : File ID which assigns unique IDs to files stored on devices
        "fileState" : binary vs. text files
        "fileType" : Type of the file stored on the device (e.g. running config vs. startup config)
        "config" : Plain text configuration files

    :param api: PrimeAPI object to control access to the API.
    :return: Dictionary with device information and configurations.
    """

    logging.debug("Get configuration version IDs")

    cfg_version_ids = []

    # Variables to implement API result paging
    first = 0
    stepsize = 100
    count = 9999999

    # Fetch IDs from API and process results by paging
    while first < count:

        xml_root = api.send_prime_request("data/ConfigVersions.xml?.maxResults=%s&.firstResult=%s" % (first + stepsize, first), "XML")
        count = int(xml_root.attrib["count"])
        list = xml_root.findall(".//entityId")

        for elem in list:
            cfg_version_ids.append(elem.text)

        first += stepsize

    logging.debug("Retrieved the following configuration version IDs:")
    logging.debug(cfg_version_ids)

    # List that will store device information and configurations in dictionaries
    cfg_info = []

    logging.debug("Get device information and configuration files")

    ctr = 1

    for id in cfg_version_ids:

        logging.debug("Checking ID %s" % id)
        logging.debug("Processing device %s of %s" % (ctr, len(cfg_version_ids)))
        print("Processing device %s of %s" % (ctr, len(cfg_version_ids)))
        ctr += 1

        # Send API request and parse XML tree for device information
        xml_root = api.send_prime_request("data/ConfigVersions/%s.xml" % id, "XML")

        cfg_id = id
        cfg_device_ip = xml_root.find(".//deviceIpAddress").text
        cfg_device_name =xml_root.find(".//deviceName").text

        # Search for files that are assigned to current device
        for info in xml_root.findall(".//fileInfo"):
            cfg_file_id = info.find("./fileId").text
            cfg_file_state = info.find("./fileState").text
            cfg_file_type = info.find("./fileType").text

            # Only fetch configuration file if type is a running or startup config
            if cfg_file_state == "RUNNINGCONFIG" or cfg_file_state == "STARTUPCONFIG":

                # Extract configuration file through separate API call
                cfg_raw = get_api_config(api, cfg_file_id)

                cfg_dict = {
                    "deviceId" : cfg_id,
                    "deviceIpAddress" : cfg_device_ip,
                    "deviceName" : cfg_device_name,
                    "fileId" : cfg_file_id,
                    "fileState" : cfg_file_state,
                    "fileType" : cfg_file_type,
                    "config" : cfg_raw
                }

                logging.debug("Retrieved the following device:")
                logging.debug("Device ID: %s" % cfg_id)
                logging.debug("Device Name: %s" % cfg_device_name)
                logging.debug("File ID: %s" % cfg_file_id)

                # Only add information if it was possible to fetch the configuration file from the API
                if cfg_raw is not None:
                    cfg_info.append(cfg_dict)

    return cfg_info


def get_api_config(api, file_id):
    """
    Extract raw (sanitized) configuration file via the Prime Infrastructure API.

    :param api: PrimeAPI object to control access to the API.
    :param file_id: File Id of the configuration file. Can be found via the API call GET Configuration versions and files list.
    :return: Plain text configuration
    """

    logging.debug("Process configuration ID %s" % file_id)
    try:
        # API call to extract the configuration and process XML
        xml = api.send_prime_request("op/configArchiveService/extractSanitizedFile.xml?fileId=%s" % file_id, "XML")
        cfg_raw = xml.find(".//fileData").text

        return cfg_raw

    except Exception:
        logging.warning("Failed to fetch configuration ID %s" % file_id)
        return None


def main():
    """
    Main method to start this configuration extraction tool.

    :return: Nothing
    """

    # Initiate logger
    logging.basicConfig(
        filename='pi_cfg.log',
        level=logging.DEBUG,
        filemode='w',
        format='%(asctime)s|%(levelname)s:%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S'
    )

    logging.debug("Start tool execution")

    print("######################################################")
    print("####                                              ####")
    print("####  PRIME INFRASTRUCTURE CONFIG EXTRACTOR TOOL  ####")
    print("####                                              ####")
    print("####  Version: 1.0                                ####")
    print("####  Date: 2015-05-10                            ####")
    print("####  Developer: Christian Jaeckel                ####")
    print("####  Email: chjaecke@cisco.com                   ####")
    print("####                                              ####")
    print("######################################################")
    print()
    print("This tool extract configuration files from Prime")
    print("Infrastructure devices and store them as plain text")
    print("files in a folder on your computer.")
    print("")
    print("Please enter Prime Infrastructure URL")
    print("For example: https://myprime.com")
    prime_url = input("Input: ")
    print()
    print("Please enter Prime Infrastructure username")
    prime_user = input("Input: ")
    print()
    print("Please enter Prime Infrastructure password")
    prime_pw = input("Input: ")
    print()

    logging.debug("Retrieved PI information via CLI")
    logging.debug("Entered URL: %s" % prime_url)
    logging.debug("Entered username: %s" % prime_user)

    print()
    logging.debug("Trying to access Prime Infrastructure API")

    try:
        api = PrimeAPI(prime_url, prime_user, prime_pw)
    except Exception as e:
        logging.critical("Prime Infrastructure API access failed!")
        logging.critical(str(e))
        print("An unexpected error occurred while executing this script. Please take a look at the log file for more information.")
        os.system('pause')
        return

    logging.debug("Prime Infrastructure API access successful")
    print()

    print("Please enter the path where the configuration files should be stored (default: C:\\)")
    print("Configuration files will be stored in the folder pi_cfg_files in this path.")
    dir_name = input("Input: ")
    print()

    if dir_name == "":
        dir_name = "C:"

    try:
        # Retrieve configuration files and device information through the API
        cfg_info = get_api_configurations(api)

    except Exception as e:
        logging.critical("An error occurred while fetching configuration and device information through the API")
        logging.exception(str(e))
        print("An unexpected error occurred while executing this script. Please take a look at the log file for more information.")
        os.system('pause')
        return

    dir_name = "%s\\pi_cfg_files" % dir_name
    logging.debug("Directory to store configuration files:")
    logging.debug(dir_name)
    logging.debug("Check and create configuration folder")

    print()
    print("Saving files to:")
    print(dir_name)
    print()

    try:
        # Check if file folder exists and delete all files if yes
        if os.path.exists(dir_name):

            filelist = [f for f in os.listdir(dir_name)]

            for f in filelist:
                os.remove("%s/%s" % (dir_name, f))

        # Create file folder
        os.makedirs(dir_name, exist_ok=True)

    except Exception as e:
        logging.critical("An error occurred while creating configuration folder")
        logging.critical(str(e))
        print("An unexpected error occurred while executing this script. Please take a look at the log file for more information.")
        os.system('pause')
        return

    logging.debug("Check and create configuration folder successful")

    logging.debug("Start writing configuration files")
    # Write all configuration files on hard drive
    for line in cfg_info:

        with open("%s/%s-%s-%s.txt" % (dir_name, line["deviceName"], line["deviceIpAddress"], line["fileState"]), "w") as file:
            file.write(line["config"])
            file.close()
            logging.debug("Successful write: %s" % file.name)

    logging.debug("Writing configuration files successful")

    print("Finished")
    os.system('pause')


if __name__ == "__main__":
    main()