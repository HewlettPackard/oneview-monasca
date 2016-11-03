# ovm-serverlist

Document Version: v1.0

#### Table of Contents

- [About](#about)
- [Installation](#installation)
- [Changelog](#changelog)
- [License](#license)

## About

The ovm_serverlist is a Node Discoverers Plugin identify which are the nodes in
OpenStack's Compute that are associated with OneView and inform this to oneview-monasca.

It process a file looking for interested nodes. To work
properly this driver requires a yaml file with the mac address of each node to be
monitored. That yaml has a set of mac addresses to be processed by the
ovm-serverlist. If the mac address belongs to a machine that is associated with
OneView, the driver inform to oneview-monasca.

The yaml file needs to have a section servers to be readed by the ovm-serverlist.
This file looks like the following example:

```
servers:
    - mac-addr: "00:19:Z9:FB:E5:57"
      dimensions:
         service: "compute"
         hostname: "hostname"
    - mac-addr: "00:19:B9:FB:E2:57"
      dimensions:
         service: "storage"
         hostname: <hostname>
         cluster: x
         backend: ceph

```

When installed, the location of the yaml file should be written in the
configuration file of the oneview-monasca in the section `server_list`, according
the next example.

```
# Section server_l
[server_list]
mac_file_path = <yaml_file>
```

## Installation

The ovm-serverlist can be installed using pip, with the following command:

    pip install ovm-serverlist

## Changelog

## License

(c) Copyright 2016 Hewlett Packard Enterprise Development LP  
(c) Copyright 2016 Universidade Federal de Campina Grande  

Licensed under the Apache License, Version 2.0 (the "License");  
You may not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
