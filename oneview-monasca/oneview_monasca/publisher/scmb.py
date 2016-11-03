# -*- encoding: utf-8 -*-
#
# (c) Copyright 2016 Hewlett Packard Enterprise Development LP
# Copyright 2016 Universidade Federal de Campina Grande
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

"""
This module represents the SCMB component from oneview_monasca agent.
"""

from oneview_monasca.shared.exceptions import SCMBConnectionFailException
from oneview_monasca.eventbus.base import DiscoveryNodeSubscriber
from oneview_monasca.shared.exceptions import LoginFailException
from oneview_monasca.publisher.base import PublisherProvider
from oneview_monasca.shared import constants as const
from oneview_monasca.shared import log as logging
from pika.credentials import ExternalCredentials
from oneview_monasca.model.status import Status
from pika.exceptions import AMQPConnectionError
from pika.exceptions import AMQPChannelError
from oneview_monasca.shared import utils
from threading import Thread
from threading import Lock

import json
import pika

LOG = logging.get_logger(__name__)


class SCMB(PublisherProvider, DiscoveryNodeSubscriber, Thread):
    """
    The SCMB class to provider a RabbitMQ messages callbacks

    Thread control:
        stopped: Manage the thread state (running or stopped).
        lock: Manage the access of another publishers to shared data structs to avoid race condition.
    """
    def __init__(self, manager_oneview, host, max_retry_attempts, crash_callback, debug=False):
        super(SCMB, self).__init__()
        Thread.__init__(self)

        self.debug = debug
        # Agent attributes usage
        self._host = host
        self._monitored_nodes = set()
        self._crash_callback = crash_callback
        self._manager_oneview = manager_oneview
        self._max_retry_attempts = int(max_retry_attempts)

        # Thread attributes control
        self._lock = Lock()
        self._stopped = True

        # RabbitMQ attributes manage
        self._channel = None
        self._connection = None
        self._reload_certs = True

    def stop(self):
        """ Stop the Thread.
        """
        self._stop_scmb()
        self._stopped = True

        self._Thread__stop()

    def publish(self):
        """ Initialize the process of Component.
        """
        utils.print_log_message('Info', 'Initialize SCMB', LOG)

        self._stopped = False
        self.start()

    def available(self, nodes):
        """ Receive a set of nodes to be monitored.

        :param nodes: A set of Node objects.
        """
        updated_nodes = set()
        for node in nodes:
            updated_nodes.add(node.server_hardware_uuid)
            utils.log_actions(node, "discovered", self.debug, LOG)

        self._lock.acquire()
        self._monitored_nodes.update(updated_nodes)
        self._lock.release()

    def unavailable(self, nodes):
        """ Receive a set of nodes and very if these nodes should be removed
        from monitored nodes.

        To verify, the puller looks at metrics in nodes: if metrics is empty,
        it will remove the node, else it will keep the node in monitored nodes.

        :param nodes: A set of Node objects.
        """
        updated_nodes = set()
        for node in nodes:
            if not node.metrics:
                updated_nodes.add(node.server_hardware_uuid)
                utils.log_actions(node, "removed", self.debug, LOG)

        self._lock.acquire()
        self._monitored_nodes.difference_update(updated_nodes)
        self._lock.release()

    @property
    def connection(self):
        """ Private function to create a connection with RabbitMQ using the Pika library.

        :return: A instance of pika connection
        """
        if self._connection is None:
            # Validate current certificate
            self._manager_oneview.validate_certificates()

            # Setup our ssl options
            ssl_options = self._manager_oneview.get_certificates()

            # Connect to RabbitMQ
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    self._host,
                    const.MB_PORT,
                    credentials=ExternalCredentials(),
                    ssl=True,
                    ssl_options=ssl_options
                )
            )
        return self._connection

    @connection.setter
    def connection(self, value):
        if self._connection is not None and self._connection.is_open:
            utils.print_log_message('Info', 'Closing connection with RabbitMQ', LOG)
            self._connection.close()

        # Set connection to None value
        self._connection = value

    def _initialize_scmb(self):
        """ Function to open a communication channel between the Monasca/OneViewD and OneView SCMB.

        :raises: A instance of SCMBConnectionFailException when burst the max_attempts to connect with RabbitMQ
        """
        utils.print_log_message('Info', 'Starting agent for listening changes in monitored nodes', LOG)

        # Create a connection with RabbitMQ and Create and bind to queue
        self._channel = self.connection.channel()

        result = self._channel.queue_declare()
        queue_name = result.method.queue

        self._channel.queue_bind(exchange=const.EXCHANGE_NAME, queue=queue_name, routing_key=const.ROUTING_KEY)

        self._channel.basic_consume(self._scmb_callback, queue=queue_name, no_ack=True)

        utils.print_log_message('Info', 'Start listening for SCMB messages', LOG)
        self._reload_certs = True
        self._channel.start_consuming()

    def _stop_scmb(self):
        """ Shutdown the connection to Oneview SCMB by stopping the consumer with RabbitMQ.
        When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection.
        """

        # Stop listening for messages
        if self._channel is not None:
            utils.print_log_message('Info', 'Stopping the RabbitMQ channel', LOG)
            self._channel.stop_consuming()

        self._channel = None
        self.connection = None
        utils.print_log_message('Info', 'Connection with RabbitMQ was stopped successfully', LOG)

    def on_cancelok(self, unused_frame):
        """ This method is invoked by pika when RabbitMQ acknowledges the cancellation of a consumer.

        :param unused_frame:
        """
        utils.print_log_message('Info', 'Closing the RabbitMQ channel', LOG)
        self._channel.close()

    def run(self):
        """ Default method the start a thread
        """
        while not self._stopped and self._max_retry_attempts > 0:
            try:
                self._initialize_scmb()
            except (LoginFailException, OSError) as ex:
                self._stopped = True
                self._crash_callback(ex)
            except (AMQPConnectionError, AMQPChannelError) as ex:
                self._retry_reconnect(ex)
            except Exception as ex:
                self._retry_reconnect(ex, 0)

        if self._max_retry_attempts == 0:
            self._crash_callback(
                SCMBConnectionFailException('Fail to open a connection with SCMB, fixed it and trying again')
            )

    def _get_status(self, resource_uuid, str_status, str_timestamp):
        """ Function the get the status associated a node resource

        :param resource_uuid: The UUID associated a node resource
        :param str_status: the status associated a input node resource
        :param str_timestamp: the timestamp of status input
        :return: a Status object
        """
        try:
            status = self._manager_oneview.get_server_hardware_status(resource_uuid, str_status)
            # Converting timestamp
            timestamp = utils.parse_timestamp(str_timestamp)

            return Status(resource_uuid, status, timestamp)
        except Exception as ex:
            self._crash_callback(ex)

    def _scmb_callback(self, ch, method, properties, body):
        """ Function to SCMB callbacks

        :param ch: the channel to connect SCMB and RabbitMQ
        :param method: the method used to get the messages
        :param properties: the message properties
        :param body: the body of message
        """
        # Parsing State-Change Message Bus message body
        message = json.loads(body)
        # Get interest resource
        resource = message['resource']

        message = 'Pull metric to resource with key %(resource_key)s' % {
            "resource_key": method.routing_key
        }
        utils.print_log_message('Info', message, LOG)

        self._lock.acquire()
        if resource['uuid'] not in self._monitored_nodes:
            message = 'Resource %(uuid)s not found in current monitored, waiting for node discoverer update' % {
                'uuid': resource['uuid']
            }
            utils.print_log_message('Info', message, LOG)

        else:
            uuid = resource['uuid']
            # Get Resource status and timestamp
            status, timestamp = resource['status'], resource['modified']
            # Pulling Status Metric
            self.status_update({self._get_status(uuid, status, timestamp)})

        self._lock.release()

    def _retry_reconnect(self, exc_obj, mode=1):
        """ Function to try reconnect agent with SCMB when a exception is raised

        :param exc_obj: the raised exception
        :param mode: If mode equal to one try re-validate SCMB certificates, else apply default behavior
        """
        self._stop_scmb()
        utils.print_log_message('Error', exc_obj, LOG)

        if self._reload_certs and mode:
            self._reload_certs = False
            utils.print_log_message(
                'Info', "Connection with SCMB closed, trying validate the certificates again", LOG)
            return

        self._max_retry_attempts -= 1
        if self._max_retry_attempts > 0:
            utils.print_log_message('Info', "Trying reconnect to OneView SCMB", LOG)
