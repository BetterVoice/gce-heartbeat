#!/usr/bin/python

from argparse import ArgumentParser
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from subprocess import CalledProcessError, check_call

import os
import time

class HeartBeat(object):
  Primary = 0
  Secondary = 1

  def __init__(self, *args, **kwargs):
    self.credentials = GoogleCredentials.get_application_default()
    self.compute = build('compute', 'v1', credentials = self.credentials)
    self.owner = HeartBeat.Primary
    self.interval = kwargs['interval'][0]
    self.project = kwargs['project'][0]
    self.region = kwargs['region'][0]
    self.address_name = kwargs['address_name'][0]
    self.primary = kwargs['primary'][0]
    self.primary_zone = kwargs['primary_zone'][0]
    self.secondary = kwargs['secondary'][0]
    self.secondary_zone = kwargs['secondary_zone'][0]
    self.pri_nic = self.__get_network_interfaces__(self.project,
                                                   self.primary,
                                                   self.primary_zone)[0]
    self.sec_nic = self.__get_network_interfaces__(self.project,
                                                   self.secondary,
                                                   self.secondary_zone)[0]

  def __add_access_config__(self, project, instance, zone, nic_name,
                            address = None):
    body = {
      'kind': 'compute#accessConfig',
      'type': 'ONE_TO_ONE_NAT',
    }
    if address:
      body.update({ 'natIP': address })
    result = self.compute \
                 .instances() \
                 .addAccessConfig(project = project,
                                  instance = instance,
                                  zone = zone,
                                  networkInterface = nic_name,
                                  body = body).execute()
    if 'error' in result:
      raise Exception(result['error'])

  def __delete_access_config__(self, project, instance, zone, access_config_name,
                             nic_name):
    result = self.compute \
                 .instances() \
                 .deleteAccessConfig(project = project,
                                     instance = instance,
                                     zone = zone,
                                     accessConfig = access_config_name,
                                     networkInterface = nic_name).execute()
    if 'error' in result:
      raise Exception(result['error'])

  def __get_address__(self, project, region, address_name):
    result = self.compute.addresses().get(address = address_name,
                                          project = project,
                                          region = region).execute()
    if 'error' in result:
      raise Exception(result['error'])
    return result

  def __get_network_interfaces__(self, project, instance, zone):
    result = self.compute.instances().get(project = project,
                                          instance = instance,
                                          zone = zone).execute()
    if 'error' in result:
      raise Exception(result['error'])
    return result['networkInterfaces']

  def __ping__(self, address, interval):
    check_call(['ping', '-c', '1', '-W', '1', address])

  def start(self):
    while True:
      try:
        self.__ping__(self.pri_nic['networkIP'], self.interval)
        if self.owner == HeartBeat.Secondary:
          # Remove the address from the secondary.
          self.__delete_access_config__(self.project, self.secondary,
                                        self.secondary_zone,
                                        self.sec_nic['accessConfigs'][0]['name'],
                                        self.sec_nic['name'])
          self.__add_access_config__(self.project, self.secondary, self.secondary_zone,
                                     self.sec_nic['name'])
          # Assign the address to the primary.
          self.pri_nic = self.__get_network_interfaces__(self.project,
                                                         self.primary,
                                                         self.primary_zone)[0]
          if len(self.pri_nic['accessConfigs']) > 0:
            self.__delete_access_config__(self.project, self.primary,
                                          self.primary_zone,
                                          self.pri_nic['accessConfigs'][0]['name'],
                                          self.pri_nic['name'])
          address = self.__get_address__(self.project, self.region,
                                         self.address_name)
          self.__add_access_config__(self.project, self.primary, self.primary_zone,
                                     self.pri_nic['name'], address = address['address'])
          self.pri_nic = self.__get_network_interfaces__(self.project,
                                                         self.primary,
                                                         self.primary_zone)[0]
          self.sec_nic = self.__get_network_interfaces__(self.project,
                                                         self.secondary,
                                                         self.secondary_zone)[0]
          self.owner = HeartBeat.Primary
      except CalledProcessError as error:
        if self.owner == HeartBeat.Primary:
          # Make sure the address is not in use.
          address = self.__get_address__(self.project, self.region,
                                         self.address_name)
          if address['status'] == 'IN_USE':
            self.__delete_access_config__(self.project, self.primary,
                                          self.primary_zone,
                                          self.pri_nic['accessConfigs'][0]['name'],
                                          self.pri_nic['name'])
          # Assign the address to the secondary.
          if len(self.sec_nic['accessConfigs']) > 0:
            self.__delete_access_config__(self.project, self.secondary,
                                          self.secondary_zone,
                                          self.sec_nic['accessConfigs'][0]['name'],
                                          self.sec_nic['name'])
          self.__add_access_config__(self.project, self.secondary, self.secondary_zone,
                                     self.sec_nic['name'], address = address['address'])
          self.sec_nic = self.__get_network_interfaces__(self.project,
                                                         self.secondary,
                                                         self.secondary_zone)[0]
          self.owner = HeartBeat.Secondary

      time.sleep(self.interval)

if __name__ == "__main__":
  parser = ArgumentParser(description = 'Establish a heartbeat between two ' +
                                        'instances for external IP failover.')
  parser.add_argument('--interval', dest = 'interval', nargs = 1,
                      required = True, type = int,
                      help = 'The heartbeat interval in seconds.')
  parser.add_argument('--project', dest = 'project', nargs = 1,
                      required = True, help = 'The project ID.')
  parser.add_argument('--region', dest = 'region', nargs = 1,
                      required = True, help = 'The name of the region.')
  parser.add_argument('--address-name', dest = 'address_name', nargs = 1,
                      required = True,
                      help = 'Name of the static address.')
  parser.add_argument('--primary', dest = 'primary', nargs = 1,
                      required = True,
                      help = 'The name of the primary instance.')
  parser.add_argument('--primary-zone', dest = 'primary_zone', nargs = 1,
                      required = True,
                      help = 'The primary instance zone.')
  parser.add_argument('--secondary', dest = 'secondary', nargs = 1,
                      required = True,
                      help = 'The name of the secondary instance.')
  parser.add_argument('--secondary-zone', dest = 'secondary_zone', nargs = 1,
                      required = True,
                      help = 'The secondary instance zone.')
  args = parser.parse_args()
  # Start the hearbeat service.
  HeartBeat(**vars(args)).start()