import ssl
from threading import Lock
import logging
from .base_nats_client import BaseNatsClient
from agora_logging import logger
from agora_config import config
from nats.aio.client import Client as NATS


class NatsClient(BaseNatsClient):
    """
    Provides NATS client capabilities for sending and receiving NATS messages to NATS server.

    The Client ID for the NATS Client is the 'Name' configuration setting.
    """

    def __init__(self):
        super().__init__()
        self.client = NATS()

    def is_connected(self) -> bool:
        return self.client.is_connected

    async def disconnect(self):
        await self.client.flush()
        await self.client.close()

    async def on_message(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        logger.trace(f"Received a message on {subject} {reply}: {data}")
        group = self.subscriptions[subject][0]
        self.messages.process_message(group, msg)

    async def update_topics(self, topics, targets):
        if self.is_connected():
            # only drop subcriptions and resubscribe if topics is not empty
            if len(topics.keys()) > 0: 
                for tp in self.subscriptions.keys():
                    try:
                        # the sub is the second item in the tuple
                        sub = self.subscriptions[tp][1]
                        await sub.unsubscribe()
                    except Exception as err:
                        logger.warn(f"failed to unsubscribe from topic '{tp}': {err}")
                        continue

                for group in topics.keys():
                    for topic in topics[group]:
                        sub = await self.client.subscribe(subject=topic, cb=self.on_message)
                        # store group and sub as a tuple
                        self.subscriptions[topic] = (group, sub)
            
        await super().update_topics(topics=topics, targets=targets)

    async def connect(self, limit_sec: int):
        async def error_cb(e):
            logger.warn(f"failed to establish connection to nats: {e}")

        async def closed_cb():
            logger.warn("connection to nats is closed")

        async def reconnected_cb():
            logger.info(f"connection to nats re-established at {self.server}")

        # Create an SSL context for the connection
        ssl_context = ssl.create_default_context()

        # Skip certificate verification (Insecure)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        logger.info(f"bus_client connecting to {self.server}")
        try:                
            await self.client.connect(
                error_cb=error_cb,
                closed_cb=closed_cb,
                reconnected_cb=reconnected_cb,
                name=config["Name"],
                password=self.nats_password,
                servers=[self.server],
                connect_timeout=limit_sec,
                tls=ssl_context,
                user=self.nats_user,
                max_reconnect_attempts=5,
        )
        except Exception as e:
            logger.error(f"Failed to connect to {self.server}:{e}")

        if self.is_connected():
            logger.info(f"bus_client connected to {self.client.servers[0].scheme}://{self.client.servers[0].hostname}:{self.client.servers[0].port}")
            await self.__subscribe()            
        else:
            logger.info(f"bus_client failed to connect to {self.server}")

    async def __subscribe(self):
        if self.is_connected():
            try:
                if len(self.topics.keys()) > 0:
                    logger.trace(f"NATS Client: Subscribing to topics: ({self.topics})")
                    for group in self.topics.keys():
                        for topic in self.topics[group]:
                            sub = await self.client.subscribe(
                                subject=topic, cb=self.on_message
                            )
                            self.subscriptions[topic] = (group, sub)
                else:
                    logger.trace(f"NATS Client: No subscriptions specified.")
            except Exception as e:
                logging.exception(e, f"Error configuring NATS client: {str(e)}")
        else:
            logger.error("NATS Client: Subscribe requested while not connected.")

    async def send_message(self, topic: str, payload: str) -> None:
        try:
            bytes_payload = payload.encode()
            if topic in self.targets.keys():
                if len(self.targets[topic]) > 0:
                    for tpc in self.targets[topic]:
                        logger.trace(f"NATS Client: Publishing payload to: {tpc}")
                        await self.client.publish(subject=tpc, payload=bytes_payload)
                else:
                    logger.warn(f"NATS Client: Publishing payload failed. No targets found for topic: {topic}")
        except Exception as e:
            logger.error(e, f"Error trying to publish the message : {str(e)}")
