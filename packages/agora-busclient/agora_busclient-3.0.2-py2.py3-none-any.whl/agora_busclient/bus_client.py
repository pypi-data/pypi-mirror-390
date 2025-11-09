import os
import asyncio
import json
from threading import Thread, Lock
import tempfile
from time import sleep
from agora_config import config
from agora_logging import logger
from agora_config import config, file_provider
from agora_twin_property import twin_property_observer, Twin as twin
from .messages import IoDataReportMsg, MessageEncoder, RequestMsg, MessageHeader, EventMsg
from .nats_client import NatsClient
from .base_nats_client import BaseNatsClient
import nest_asyncio
nest_asyncio.apply()


class BusClientSingleton:
    _instance = None
    """
    Connects to the nats server and handles sending and receiving messages
    """
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.subscriptions = set()
        self.mocking_busclient = config["AEA2:BusClient"] is None or config["AEA2:BusClient"] == '' or config["AEA2:BusClient:Mock"] == 'True'
        if self.mocking_busclient:
            self.bus = BaseNatsClient()
        else:
            self._loop = asyncio.new_event_loop()
            self._thread = Thread(target=self._start_event_loop ,daemon=True)
            self._thread.start()
            self.bus = NatsClient()
        
        mocking_redis = config["AEA2:RedisClient"] is None or config["AEA2:RedisClient"] == '' or config["AEA2:RedisClient:Mock"] == 'True'
        if not mocking_redis:
            ''' subscribe to redis key for new configs'''
            twin.observe(app_callback=self.handle_twin_callback, tp_group_id="config", property_name=config["Name"])
        
        
        self._initialized = True

    @property
    def messages(self):
        '''
        Returns the internal bus client's queued messages
        '''
        return self.bus.messages

    def connect(self, sec: float) -> None:
        '''
        Connects the BusClient.
        
        Configuration settings used:

        - 'Name': The name used to represent the client to the NATS server.\n
        - 'AEA2:BusClient':
            - 'Server': (optional) The full URL of the NATS server.  Default is 'nats://127.0.0.1:4222'
            - 'Subscriptions': (optional) List of topics to subscribe to. Ex. ["DataIn", "RequestIn", "EventIn"]
            - 'Targets': (optional) List of topics to publish to. Ex. "DataOut": ["slbapps.targetapp1.DataIn", "slbapps.targetapp2.DataIn", "slbapps.stratus.DataIn"]
        '''
        # configure then connect
        asyncio.get_event_loop().run_until_complete(self.bus.configure())
        if self.mocking_busclient:  
            self.bus.connect(sec)
        else:
            # connect
            asyncio.run_coroutine_threadsafe(self.bus.connect(sec), self._loop)

            # return from connect only if actually connected 
            while not self.is_connected():
                sleep(1)

            # then update config from twins, if exists
            self.read_config_twin()

        
    def disconnect(self):
        '''
        Disconnects the BusClient
        '''
        if self.mocking_busclient:
            self.bus.disconnect()
        else:
            if self.bus.is_connected():
                asyncio.run_coroutine_threadsafe(self.bus.disconnect(), self._loop)            

    def reconnect(self, _ = None) -> None:
        '''
        Reconnects the BusClient.  Mostly this happens if the configuration has changed.
        '''
        logger.info(f"bus_client reconnecting...")
        self.disconnect()
        self.connect(30)

    def is_connected(self) -> bool:
        '''
        Returns whether the BusClient is connected or not.
        '''
        return self.bus.is_connected()

    def send_message(self, topic: str, header: MessageHeader, payload: str) -> None:
        '''
        Sends a message to 'topic', combining 'header' and 'payload' into a json representation.
        '''
        if not self.bus.is_connected():
            logger.error(
                "Cannot send message, BusClient is not connected to the server")
            return
        headerJson = json.dumps(header, cls=MessageEncoder)
        payload_str = json.dumps(payload)
        if payload_str[0] != '"':
            payload_str = json.dumps(payload_str)
        message = f"""{{
            "header": {headerJson},
            "payload": {payload_str}
        }}"""
        self.bus.send_message(topic, message)

    def send_raw_message(self, topic: str, payload: str) -> None:
        '''
        Sends a raw message (still a string) to 'topic'
        '''
        if not self.bus.is_connected():
            logger.error(
                "Cannot send message, BusClient is not connected to the server")
            return
        if self.mocking_busclient:
            self.bus.send_message(topic, payload)
        else:
            asyncio.run_coroutine_threadsafe(self.bus.send_message(topic, payload), self._loop)            

    def send_data(self, msg: IoDataReportMsg, msgTopic="DataOut") -> None:
        '''
        Sends an IoDataReportMsg to 'msgTopic' which defaults to 'DataOut' if not specified.
        '''
        payload = json.dumps(msg, cls=MessageEncoder)
        self.send_raw_message(msgTopic, payload)

    def send_request(self, msg: RequestMsg, msgTopic="RequestOut") -> int:
        '''
        Sends a RequestMsg to 'msgTopic' which defaults to 'RequestOut' if not specified.
        '''
        payload = json.dumps(msg, cls=MessageEncoder)
        self.send_raw_message(msgTopic, payload)
        return msg.header.MessageID
    
    def send_event(self, msg: EventMsg, msgTopic="EventOut") -> int:
        '''
        Sends an EventMsg to 'msgTopic' which defaults to 'EventOut' if not specified.
        '''        
        payload = json.dumps(msg, cls=MessageEncoder)
        self.send_raw_message(msgTopic, payload)
        return msg.EventId

    def read_config_twin(self) -> None:
        '''
        Reads redis on startup for any config set via Twins.
        '''
        new_config = False
        app_name = config["Name"]
        group_id = "config"
        twin_config = twin.get_desired_property(prop_name=app_name, tp_group_id=group_id)
        if twin_config:
            new_config = True
            response = twin_property_observer.CallbackResponse(
                    tp_id= group_id,
                    key= app_name,
                    value= twin_config
                )   
        
        if new_config:
            # override with desired properties from redis
            self.handle_twin_callback(response)
                    
        asyncio.run_coroutine_threadsafe(self.bus.configure(), self._loop)

    def handle_twin_callback(self, response: twin_property_observer.CallbackResponse) -> None:  
        twin_aea_json = None
        try:
            # check if valid JSON
            twin_aea_json = json.loads(response.value)
        except json.JSONDecodeError as e:
            logger.warn("found config twin with invalid JSON format in redis, discarding...")
            return
            
        if twin_aea_json:
            logger.info("found newer AEA.json config in redis twin property")
                    
        # Create the full path to AEA.json within a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                custom_file_path = os.path.join(temp_dir, "AEA.json")
                    
                with open(custom_file_path, 'w') as temp_file:
                    temp_file.write(response.value)
                    override_path = temp_dir
            
                if temp_file is not None:
                    # load the config from redis
                    config.primary_config = file_provider.FileProvider("AEA.json", override_path)
                    config.build()
                    logger.info("loaded newer AEA.json config from redis")
                    
                    # update subscriptions and targets
                    topics: dict = dict()
                    targets: dict = dict()
                    
                    subscriptions = config["AEA2:BusClient:Subscriptions"]
                    if len(subscriptions) != 0:
                        for sub in subscriptions:
                            for key in sub.keys():
                                topics[key] = sub[key]

                    ctargets = config["AEA2:BusClient:Targets"]
                    if len(targets) != 0:
                        for ctarget in ctargets:
                            for key in ctarget.keys():
                                targets[key] = ctarget[key]    
                    
                    # update topics
                    asyncio.run_coroutine_threadsafe(self.bus.update_topics(topics=topics, targets=targets), self._loop)

                    # update reported property
                    twin.set_reported_property(prop_name=config["Name"], prop_value=response.value, tp_group_id="config")
                    
                    

    def configure(self) -> None:
        '''
        Configures the internal bus client.
        '''
        asyncio.get_event_loop().run_until_complete(self.bus.configure())

    def _start_event_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

'''
The singleton instance of the bus_client.
'''
bus_client = BusClientSingleton()
