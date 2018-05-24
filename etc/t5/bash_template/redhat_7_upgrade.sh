#!/bin/bash
# Copyright 2018 Big Switch Networks, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

is_controller=%(is_controller)s

controller() {

    PKGS=/tmp/upgrade/*
    for pkg in $PKGS
    do
        if [[ $pkg == *"python-networking-bigswitch"* ]]; then
            rpm -ivhU $pkg --force
            systemctl daemon-reload
            neutron-db-manage upgrade heads
            systemctl enable neutron-server
            systemctl restart neutron-server
            break
        fi
    done

    for pkg in $PKGS
    do
        if [[ $pkg == *"openstack-neutron-bigswitch-lldp"* ]]; then
            rpm -ivhU $pkg --force
            systemctl daemon-reload
            systemctl enable  neutron-bsn-lldp
            systemctl restart neutron-bsn-lldp
            break
        fi
    done

    for pkg in $PKGS
    do
        if [[ $pkg == *"openstack-neutron-bigswitch-agent"* ]]; then
            rpm -ivhU $pkg --force
            systemctl stop neutron-bsn-agent
            systemctl disable neutron-bsn-agent
            break
        fi
    done

    for pkg in $PKGS
    do
        if [[ $pkg == *"python-horizon-bsn"* ]]; then
            rpm -ivhU $pkg --force
            systemctl restart httpd
            break
        fi
    done

}

compute() {

    PKGS=/tmp/upgrade/*
    for pkg in $PKGS
    do
        if [[ $pkg == *"python-networking-bigswitch"* ]]; then
            rpm -ivhU $pkg --force
            break
        fi
    done

    for pkg in $PKGS
    do
        if [[ $pkg == *"openstack-neutron-bigswitch-agent"* ]]; then
            rpm -ivhU $pkg --force
            systemctl daemon-reload
            systemctl stop neutron-bsn-agent
            systemctl disable neutron-bsn-agent
            break
        fi
    done

    for pkg in $PKGS
    do
        if [[ $pkg == *"openstack-neutron-bigswitch-lldp"* ]]; then
            rpm -ivhU $pkg --force
            systemctl daemon-reload
            systemctl enable neutron-bsn-lldp
            systemctl restart neutron-bsn-lldp
            break
        fi
    done
}


set +e

# Make sure only root can run this script
if [ "$(id -u)" != "0" ]; then
    echo -e "Please run as root"
    exit 1
fi

if [[ $is_controller == true ]]; then
    controller
else
    compute
fi

set -e

exit 0

