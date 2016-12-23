# OneView-Monasca

Document Version: v1.0

#### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
    - [Example of configuration file](#example-of-configuration-file)
- [High Availability Mode](#high-availability-mode)
- [Running the agent](#running-the-agent)
- [Metrics](#metrics)
    - [Examples of measurements](#examples-of-measurements)
- [Components](#components)
    - [Keeper](#keeper)
    - [EventBus](#eventbus)
    - [Puller](#puller)
    - [SCMB](#scmb)
    - [Plugins](#plugins)
    - [Managers](#managers)
- [License](#license)

## Overview

The oneview-monasca is a daemon written in Python that collects, processes and
publishes health status from nodes of interest (from now on referred as nodes) on
OneView and sends these information to Monasca.

To obtain the nodes information, the oneview-monasca uses Node Discovery plugins.
Currently, there are two plugins implemented: ovm-ironic (ovm stands for
oneview-monasca), and ovm-serverlist. These plugins can be installed [using pip](#installation).
Oneview-monasca requires at least one plugin installed in order to run. A Node
Discover plugin identifies the nodes and informs them to the oneview-monasca.

## Installation

**See versions on PyPI:**
- https://pypi.python.org/pypi/oneview-monasca/

**Install It:**

    $ sudo pip install oneview-monasca

**Alternative Manual Installation Steps:**

    $ git clone https://github.com/HewlettPackard/oneview-monasca
    $ cd oneview-monasca
    $ sudo pip install -r requirements.txt
    $ python setup.py install

**Note**:  To avoid problems when publishing metrics to Monasca, it’s strongly
recommended to synchronize the clock on all machines that runs the agent and
Monasca. Therefore, run the /tools/install_chrony.sh file to synchronize the
machine's clock with an NTP service. If you set your Monasca as a NTP server, run:

    $ install_chrony.sh <monasca-address>


Or, if you have another NTP service, run:

    $ install_chrony.sh <ntp-server>

## Configuration

A configuration file is required to run the oneview-monasca. You can create it by
running the following command:

    $ oneview-monasca genconfig

This command above allows you to provide all necessary information to run the
agent, you can also set your configuration file’s name and the path where it will
be stored, by default its name will be oneview_monasca.conf and will be saved at
the home of the current user.

The plugins sections are optional according to the installed ones. The example
below shows a configuration file for an agent running with both plugins:
ovm-ironic and ovm-serverlist.

#### Example of configuration file

```
[DEFAULT]
debug=false
retry_interval = 300
batch_publishing_interval = 60
periodic_refresh_interval = 180
auth_retry_limit = 5
scmb_certificate_dir = /var/run/oneview-monasca

[openstack]
auth_url = http://17.7.7.107:5000/v3
auth_user = mini-mon
auth_password = password
auth_tenant_name = mini-mon
monasca_api_version = 2_0

[oneview]
host = 170.177.87.177
manager_url = https://170.177.87.177
username = administrator
password = pass-oneview
allow_insecure_connections = true
max_polling_attempts = 20
tls_cacert_file =

[ironic]
auth_url = http://17.7.7.7:5000/v2.0/
admin_user = admin
admin_password = password
admin_tenant_name = admin
insecure = false
ironic_api_version = 1.11
project_name = example-project
region_name = regionExample
user_domain_id = default
project_domain_id = default
project_id = default
user_domain_name = exampleDomain
project_domain_name = exampleDomain
ironic_url = http://17.7.7.107:6385/v1
[serverlist]
mac_file_path = ~/mac-file.yaml
```

## High Availability Mode

To ensure that the agent will not stop publishing metrics from OneView when the
machine or the process crash for some reason, it is possible to activate the HA
mode. Oneview-monasca uses the tooz library from OpenStack as a python client to communicate
with drivers that have support for fault tolerance applications (e.g. zake, a
driver for Zookeeper). You can find all the middleware supported by tooz [here](http://docs.openstack.org/developer/tooz/).

It is strongly recommended to use odd numbers of participants in your group and
at least 3 participants. Only one agent will be running each time and this agent
will be the coordinator of the group. When the coordinator agent fails a new
leader will be elected and the new coordinator agent will keep publishing metrics
from OneView.

To activate the HA mode, add a tooz configuration section in the configuration
file following the pattern:

```
[tooz]
group_name=<oneview_group>
coordinator_url=<driver_name>:<ip>:<port>
```

As the example bellow:

```
[tooz]
group_name = oneview-monasca
coordinator_url = zake:127.0.0.1
```

## Running the agent

Before starting the agent make sure you have installed at least one plugin to
discover the nodes to be monitored. The currently supported plugins can be
installed using pip (Section [plugins](#plugins)).

There are two ways to run the agent. You can pass a configuration file by
running:

    $ oneview-monasca -c /path/to/config_file.conf

The second one does not need to receive a configuration file already filled up,
instead the agent will ask for all settings and then it will automatically
generate the file.

    $ oneview-monasca

## Metrics

Oneview-monasca provides metrics about the health status of OneView's monitored
Server Hardwares  enriched with information from OneView Alerts.

The metric name sent to Monasca is oneview.node_status. There are five possible
numeric values of measurement that represent the health status of a node.
The values are:

| Metric Value | OneView Status | Description  |
|:------------:|:--------------:|:-------------|
| 0            | OK             | Indicates normal / Informational behavior. |
| 1            | Disabled       | Indicates that a resource is not operational. |
| 2            | Warning        | Needs attention soon. |
| 3            | Critical       | Needs immediate attention. |
| 4            | Unknown        | Should be avoided, but there may be rare occasions where status is Unknown. |

If the value is not 0 (zero),  the oneview-monasca sends additional information
on the field value_meta. The value_meta contains a link to all alerts associated
with the node.

#### Examples of measurements:

Measurement without an associated value_meta:

```
{
    'name': 'oneview.node_status',
    'value': 0,
    'timestamp': '1472561795947.719',
    'dimensions': {
        'service': 'storage',
        'backend' : 'ceph'
    },
    'value_meta': {}
}


Measurement with an associated value_meta:
{
    'name': 'oneview.node_status',
    'value': 2,
    'timestamp': '1472561795947.719',
    'dimensions': {
        'service': 'storage',
        'backend' : 'ceph'
    },
    'value_meta': {
        '/rest/alerts/124780': 'http://17.7.7.7:5000/v2.0/#/activity/r/rest/alerts/124780',
        '/rest/alerts/124790': 'http://17.7.7.7:5000/v2.0/#/activity/r/rest/alerts/124790'
    }
}
```

## Components

Oneview-monasca has a modular structure composed by six components: Keeper,
Puller, EventBus, SCMB, plugins, and the managers. Check below the description of
each component.

### Keeper

The Keeper is the main component of the oneview-monasca. It receives measurements
from  Puller,  SCMB and EventBus, makes these values compliant with monasca-api
and sends them periodically to monasca. In addition the Keeper also adds a
value_meta field if the measurement is different of '0', which means not 'OK' for
OneView.

### EventBus

The EventBus loads all installed plugins and initializes them. After initializing
all plugins, it subscribes itself for each driver to receive
information about new nodes and  publishes them for all its listeners.

### Puller

The Puller a listener of the EventBus. It receives a list of new nodes and
keeps track of them. The first time the Puller receives a list, it collects the
status of each new node and sends them immediately to the Keeper. After that, it
keeps track of the status of each new nodes and periodically send them to the
Keeper. The sending interval can be configured as needed. See the installation
section for more information about the sending interval.

### SCMB

The SCMB is a listener of the [State-Change Message Bus](http://h17007.www1.hpe.com/docs/enterprise/servers/oneviewhelp/oneviewRESTAPI/content/c_SCMB-subscribe.html).
It stands waiting for any status change of any node of the oneview-monasca. If a change is detected, the SCMB sends this information to Keeper.

### Plugins

The Node Discoverer plugins are responsible for identifying the nodes
and informing them the oneview-monasca. Currently, there are two plugins that
discover new nodes and provide their information to oneview-monasca.

- ovm-ironic:

    Responsible for finding ironic nodes that are managed by [ironic oneview drivers](http://docs.openstack.org/developer/ironic/drivers/oneview.html).
To install this plugin, use $ pip install ovm-ironic

- ovm-serverlist:  

    Responsible for finding serverlist nodes in oneview from a file with a list of servers.
To install this plugin, use $ pip install ovm-serverlist

### Managers

Managers abstract the communication with monasca-api and OneView REST API.

- Manager Monasca:

    Used by oneview-monasca to send metrics to monasca-api using
python-monascaclient, which calls the monasca-api service via REST.

- Manager OneView:

    Used by oneview-monasca to get the health status, verify
if the node is managed by OneView using the OneView REST API, get alerts, and subscribe to the SCMB

## Contributing

You know the drill. Fork it, branch it, change it, commit it, and pull-request it. We are passionate about improving this project, and glad to accept help to make it better. However, keep the following in mind:

- We reserve the right to reject changes that we feel do not fit the scope of this project, so for feature additions, please open an issue to discuss your ideas before doing the work.

## ChangeLog
- 1.0.0: initial version

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
