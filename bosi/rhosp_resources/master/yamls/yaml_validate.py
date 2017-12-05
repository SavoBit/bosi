#!/usr/bin/env python

import argparse
import os
import sys
import yaml

EXIT_ERROR = -1
YAML_FILE_EXT = ".yaml"
SUPPORTED_BOND = ['linux_bond']


def help():
    """ Print how to use the script """
    print "Usage: %s <directory>" % sys.argv[0]



def validate_yaml_bridge(yaml_file_path):
    """
    Validate the bridge info in the controller or compute's yaml file given
    as param.

    :param yaml_file_path:
    :return:
    """
    valid_bridge = False
    yaml_file = open(yaml_file_path, 'r')
    config_yaml = yaml.load(yaml_file)
    network_config_list = (config_yaml['resources']['OsNetConfigImpl'][
                               'properties']['config']['str_replace'][
                               'params']['$network_config']['network_config'])
    for config in network_config_list:
        config_type = config.get('type')
        # if its neither ivs_bridge or ovs_bridge, move on
        if config_type != 'ivs_bridge' and config_type != 'ovs_bridge':
            continue

        # for ivs_bridge, no other checks required. return True
        if config_type == 'ivs_bridge':
            valid_bridge = True
            break

        # for ovs_bridge, check that bridge name is br-ex
        if config_type == 'ovs_bridge':
            if config.get('name') != 'br-ex':
                continue
            members = config.get('members')
            for member in members:
                # also check that type of bond for interface is supported
                if member.get('type') not in SUPPORTED_BOND:
                    continue
                # everythig checks out, return True
                valid_bridge = True
                break

    if valid_bridge:
        print ("VALID bridge configuration in %s" % yaml_file_path)
    else:
        # we looped through the config, did not find anything matching completely
        # return False
        print ("INVALID bridge configuration in %s. Please check "
               "deployment guide before proceeding." % yaml_file_path)


def check_yaml_syntax(f):
    """ Check the syntax of the given YAML file.
        return: True if valid, False otherwise
    """
    with open(f, 'r') as stream:
        try:
            yaml.load(stream)
        except yaml.YAMLError as exc:
            print "%s: Invalid YAML syntax.\n%s\n" % (f, exc)
            return False
    return True


def check_yaml_syntax_dir(yaml_dir):
    if not os.path.isdir(yaml_dir):
        print "ERROR: Invalid directory %s" % yaml_dir
        sys.exit(EXIT_ERROR)

    all_valid = True
    for root, dirs, files in os.walk(yaml_dir):
        for f in files:
            if YAML_FILE_EXT in f:
                fname = root + "/" + f
                valid = check_yaml_syntax(fname)
                if valid:
                    print "%s: Valid YAML syntax" % fname
                else:
                    all_valid = False
        break

    if all_valid:
        print "All files have valid YAML syntax"
    else:
        print "Some files have invalid YAML syntax"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bridge", required=False,
                        help="RHOSP controller.yaml or compute.yaml with "
                             "the bridge configuration to be validated.")
    parser.add_argument("--syntax", required=False,
                        help="Find all YAML files in the input directory and "
                             "validate their syntax.")
    args = parser.parse_args()

    if not args.bridge and not args.syntax:
        print ("Please specify at least one option - either --bridge or "
               "--syntax")
        return

    if args.bridge and args.syntax:
        print ("Please use only one option - either --bridge or --syntax")
        return

    if args.bridge:
        validate_yaml_bridge(args.bridge)
        return

    if args.syntax:
        check_yaml_syntax_dir(args.syntax)
        return


if __name__ == "__main__":
    main()

