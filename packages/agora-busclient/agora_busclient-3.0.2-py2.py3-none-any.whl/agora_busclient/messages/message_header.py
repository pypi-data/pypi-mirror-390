import random
import time
from agora_config import config
from agora_utils import AgoraTimeStamp

class MessageHeader:
    """ 
    Represents a MessageHeader that includes source module, message type, 
    config version, message ID, and timestamp.
    """
  
    # Static variable for tracking the message ID
    message_id = -1

    def __init__(self):
        """
        Initialize a MessageHeader instance with default attributes.
        
        Attributes:
            SrcModule (str): Source module name, taken from the application config.
            MessageType (str): Type of the message, default is 'NotSet'.
            ConfigVersion (int): Configuration version, default is -1.
            MessageID (int): Unique identifier for the message.
            TimeStamp (float): Timestamp for the message, based on AgoraTimeStamp.
        """
        
        self.SrcModule: str = config["Name"]
        self.MessageType: str = "NotSet"
        self.ConfigVersion: int = -1
        if MessageHeader.message_id == -1:
            MessageHeader.message_id = MessageHeader.__get_message_id()
        MessageHeader.message_id = MessageHeader.message_id + 1
        self.MessageID: int = MessageHeader.message_id
        self.TimeStamp: float = AgoraTimeStamp()

    @staticmethod
    def __get_message_id() -> int:
        """
        Generate a message ID using current unix time to cap messageId within int32 positive range.
	    This is done as a temporary workaround until legacy modules (e.g. modbus module) are deprecated
        and message ID can be an int64. See current cloud implemention below:
        https://dev.azure.com/slb-swt/sliic/_git/iiot-cloud-common-go-library?path=/commontools/common-functions.go&version=GBmaster&line=92&lineEnd=99&lineStartColumn=1&lineEndColumn=2&lineStyle=plain&_a=contents
        
        Returns:
            int: A message ID that is not globally unique, but collision-resistant within a short time window
        """
        
        time_now_unix = int(time.time())  # Current Unix timestamp as an integer
        random_number = random.randint(1, 255)  # 8 bits of randomness
        return ((time_now_unix << 8) | random_number) & 0xFFFFFFFF  # Combine and fit into 32 bits using modulo
