import os
from agora_config import config
from agora_logging import logger
from agora_redis_client import redis as Redis
from .message_queue import MessageQueue, IoDataReportMsg
from typing import Set


class BaseNatsClient():
    """
    Base class for NATS Client, providing the core functionalities.
    Allows the use of a mock NATS client when configured.
    Refer to the configuration 'AEA2:BusClient:Mock' to set the mock state.

    Attributes:
        messages (MessageQueue): Queue to store messages.
        server (str): Server address. Defaults to "127.0.0.1".
        token (str): Token for the NATS client to authenticate with server.
        password (str): Password for the NATS client.
        topics (dict): Dictionary of topics for the client to subscribe to.
        connected (bool): Connection state of the NATS client.
    """
    def __init__(self):
        """Initialize NATS client with default settings."""
        self.messages: MessageQueue = MessageQueue()
        self.server = "nats://127.0.0.1:4222"
        self.nats_user = None
        self.nats_password = None
        self.topics: dict = dict()
        self.targets: dict = dict()
        self.subscriptions: dict = dict()
        self.connected: bool = False        

    def is_connected(self) -> bool:
        """Check if the NATS client is connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.connected

    def disconnect(self):
        """Disconnect the NATS client."""
        self.connected = False

    def connect(self, limit_sec: int) -> None:
        """Connect the NATS client, with a time limit.

        Args:
            limit_sec (int): Time limit in seconds for the connection.
        """
        self.connected = True

    async def update_topics(self, topics: dict, targets: dict) -> None:
        """Update the topics for the NATS client to subscribe to.

        Args:
            topics (Dict): New set of topics to subscribe to.
            targets (Dict): New set of targets to publish to.
        """

        # update only if it has values
        if len(topics.keys()) > 0:
            self.topics = topics    
        if len(targets.keys()) > 0:
            self.targets = targets
        
    def send_message(self, topic: str, payload):
        """Send a message to a specified topic.

        Args:
            topic (str): The topic to send the message to.
            payload: The message payload.
        """
        if self.is_connected():
            if "dataout" in topic.lower():
                self.messages.store_to_queue("DataIn", topic, payload.encode("utf-8"))
            elif "requestout" in topic.lower():
                self.messages.store_to_queue("RequestIn", topic, payload.encode("utf-8"))
            elif "eventout" in topic.lower():
                self.messages.store_to_queue("EventIn", topic, payload.encode("utf-8"))
            else:
                self.messages.store_to_queue(topic, topic, payload.encode("utf-8"))
        else:
            logger.warn("Trying to send_message, but bus_client is not connected. (BaseNatsClient)")

    @staticmethod
    def convert_to_int(value, default) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    async def configure(self) -> None:
        '''
        Configures the BusClient. Initially load AEA.json on disk that is shipped with consuming app. Then, using the app 'Name', lookup a more
        updated config file in redis. If found, reconfigure by loading the newer config and subscribing to the redis key. If not, use config on disk.
        
        Configuration settings used:

        - 'Name': The name used to represent the client to the NATS sever.\n
        - 'AEA2:BusClient':
            - 'Server': (optional) The full URL, including scheme, host name or IP, and port, of the NATS server.  Default is 'nats://127.0.0.1:4222'
            - 'Subscriptions': (optional) List of topics to subscribe to. Ex. ["DataIn", "RequestIn", "EventIn"]
            - 'NatsUser': (optional) The user to connect with if requiring authentication.  Default is ''
            - 'NatsPassword': (optional) The token to connect with if requiring authentication.  Default is ''
            - 'Targets': (optional) List of topics to publish to. Ex. "DataOut": ["slbapps.targetapp1.DataIn", "slbapps.targetapp2.DataIn", "slbapps.stratus.DataIn"]
        '''        
        
        self.server = os.getenv("NATS_ADDRESS")
        if self.server is None:
            self.server = config.get("AEA2:BusClient:Server", "nats://127.0.0.1:4222")
        self.nats_user = os.getenv("NATS_USER")
        if self.nats_user is None:
            self.nats_user = config.get("AEA2:BusClient:NatsUser", "")
        self.nats_password = os.getenv("NATS_PASSWORD")
        if self.nats_password is None:
            self.nats_password = config.get("AEA2:BusClient:NatsPassword")
            if self.nats_password is None or self.nats_password == '':
                self.nats_password = Redis.get("/secrets/sdk-token")

        topics: dict = dict()

        subscriptions = config["AEA2:BusClient:Subscriptions"]
        if len(subscriptions) != 0:
            for sub in subscriptions:
                for key in sub.keys():
                    topics[key] = sub[key]

        targets = config["AEA2:BusClient:Targets"]
        if len(targets) != 0:
            for target in targets:
                for key in target.keys():
                    self.targets[key] = target[key]     

        await self.update_topics(topics, targets=self.targets)

    async def log_config(self) -> None:
        """Log the current configuration to the console."""
        logger.info(f"NATS Client Name: {config['Name']}")
        logger.info("AEA2:BusClient:")
        logger.info(f"--- Server: {self.server}")
        if len(self.topics) > 0:
            logger.info("--- Subscriptions:")
            for sub in self.topics.keys():
                logger.info(f"   --- {sub}")
                for topic in self.topics[sub]:
                    logger.info(f"      --- {topic}")
        else:
            logger.info("--- Subscriptions: <None>")
        if len(self.targets) > 0:
            logger.info("--- Targets:")
            for target in self.targets.keys():
                logger.info(f"   --- {target}")
                for topic in self.targets[target]:
                    logger.info(f"      --- {topic}")
        else:
            logger.info("--- Targets: <None>")
            
