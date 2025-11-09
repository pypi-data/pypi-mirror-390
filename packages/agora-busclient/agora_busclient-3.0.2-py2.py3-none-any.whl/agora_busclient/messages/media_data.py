from datetime import datetime
import random
import time

class MediaData:
    """
    Represents media data with various attributes such as type, IDs, 
    filenames, MIME type, alternate text, and timestamps.
    """

    # Static variable for tracking media data IDs
    mediaData_id = -1

    def __init__(self):
        """
        Initialize a MediaData instance with default attributes.

        Attributes:
            Type (str): The type of media data (e.g., 'image', 'video').
            Id (int): Unique identifier for the media data.
            ZoneId (str): Zone identifier.
            CameraId (str): Camera identifier.
            MotTrackerId (int): Motion tracker identifier.
            EdgeFilename (str): Filename for edge storage.
            MotEdgeFilename (str): Filename for motion edge storage.
            MIMEType (str): MIME type of the media.
            AltText (str): Alternate text description.
            RawData (str): Base64 encoded binary data.
            DetectedStart_tm (float): Start time of detection.
            DetectedEnd_tm (float): End time of detection.
        """

        self.Type: str = ""

        # MediaData ID logic
        if MediaData.mediaData_id == -1:
            MediaData.mediaData_id = self.__get_media_data_id()
        MediaData.mediaData_id = MediaData.mediaData_id + 1
        self.Id: int = MediaData.mediaData_id

        # Initialize other attributes
        self.ZoneId: str = ""
        self.CameraId: str = ""
        self.MotTrackerId: int = None
        self.EdgeFilename: str = ""
        self.MotEdgeFilename: str = ""
        self.MIMEType: str = ""
        self.AltText: str = ""
        self.RawData: str = ""  # Base64 encoded binary data
        self.DetectedStart_tm: float = 0
        self.DetectedEnd_tm: float = 0

    def __get_media_data_id(self) -> int:
        """
        Generate a media data ID using current unix time to cap messageId within int32 positive range.
	    This is done as a temporary workaround until legacy modules (e.g. modbus module) are deprecated
        and message ID can be an int64. See current cloud implemention below:
        https://dev.azure.com/slb-swt/sliic/_git/iiot-cloud-common-go-library?path=/commontools/common-functions.go&version=GBmaster&line=92&lineEnd=99&lineStartColumn=1&lineEndColumn=2&lineStyle=plain&_a=contents
        
        Returns:
            int: A message ID that is not globally unique, but collision-resistant within a short time window
        """
        
        time_now_unix = int(time.time())  # Current Unix timestamp as an integer
        random_number = random.randint(1, 255)  # 8 bits of randomness
        return ((time_now_unix << 8) | random_number) & 0xFFFFFFFF  # Combine and fit into 32 bits using modulo
