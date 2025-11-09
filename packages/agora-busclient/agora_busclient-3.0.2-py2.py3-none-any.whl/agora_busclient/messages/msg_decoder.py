import json
from .iodatareport_message import IoDataReportMsg, IoDeviceData, IoPoint
from .io_tag_data_dict import IoTagDataDict
from .message_header import MessageHeader
from .media_data import MediaData
from .work_flow import WorkFlow
from .request_msg import RequestMsg
from .event_msg import EventMsg
from agora_logging import logger


class MessageDecoder:
    def decode(self, jsn, o):
        return self.__decode(json.loads(jsn), o)

    def __decode(self, d, o):
        if o == IoPoint:
            ret = IoPoint()
            try:
                if "quality_code" in d:
                    ret.quality_code = int(str(d["quality_code"]))
            except Exception as e:
                logger.exception(
                    e,
                    f"Cannot decode IoPoint with 'quality_code' of '{d['quality_code']}'",
                )

            try:
                if "value" in d:
                    ret.value = float(str(d["value"]))
            except Exception as e:
                logger.exception(
                    e, f"Cannot decode IoPoint with 'value' of '{d['value']}"
                )

            if "value_str" in d:
                ret.value_str = d["value_str"]

            try:
                if "timestamp" in d:
                    ret.timestamp = float(str(d["timestamp"]))
            except Exception as e:
                logger.exception(
                    e, f"Cannot decode IoPoint with 'timestamp' of '{d['timestamp']}"
                )

            try:
                if "metadata" in d:
                    ret.metadata = dict(d["metadata"])
                
                    for key, value in ret.metadata.items():
                        if not isinstance(key, str) or not isinstance(value, str):
                            raise TypeError("metadata must contain only string keys and values.")
            except TypeError as e:
                logger.exception(
                    e, f"Invalid types in 'metadata' in IoPoint: '{d['metadata']}"
                )
            except Exception as e:
                logger.exception(
                    e, f"Invalid 'metadata' in IoPoint: '{d['metadata']}"
                )

            return ret
        if o == IoDeviceData:
            ret = None
            try:
                if "id" in d:
                    id = str(d["id"])
                ret = IoDeviceData(id)
                if "tags" in d:
                    ret.tags = self.__decode(d["tags"], IoTagDataDict)
            except Exception as e:
                logger.exception(
                    e, f"Cannot decode IoDeviceData with 'id' of '{d['id']}'"
                )
            if ret is None:
                ret = IoDeviceData("-1")
            return ret
        if o == IoTagDataDict:
            ret = IoTagDataDict()
            for key, value in d.items():
                ret[key] = self.__decode(value, IoPoint)
            return ret
        if o == MessageHeader:
            ret = MessageHeader()
            if "SrcModule" in d:
                ret.SrcModule = d["SrcModule"]
            if "MessageType" in d:
                ret.MessageType = d["MessageType"]
            try:
                if "ConfigVersion" in d:
                    ret.ConfigVersion = int(str(d["ConfigVersion"]))
            except Exception as err:
                logger.warn(f"failed to cast ConfigVersion to int: {err}")
                ret.ConfigVersion = -1
            try:
                if "MessageID" in d:
                    ret.MessageID = int(str(d["MessageID"]))
            except Exception as err:
                logger.warn(f"failed to cast MessageID to int: {err}")
                ret.MessageID = -1
            try:
                if "TimeStamp" in d:
                    ret.TimeStamp = float(str(d["TimeStamp"]))
            except Exception as err:
                logger.warn(f"failed to cast TimeStamp to float: {err}")
                ret.TimeStamp = -1
            return ret
        if o == IoDataReportMsg:
            ret = IoDataReportMsg()
            if "header" in d:
                ret.header = self.__decode(d["header"], MessageHeader)
            if "device" in d:
                for dv in d["device"]:
                    ret.device.append(self.__decode(dv, IoDeviceData))
            return ret
        if o == RequestMsg:
            ret = RequestMsg()
            if "header" in d:
                ret.header = self.__decode(d["header"], MessageHeader)
            if "payload" in d:
                ret.payload = d["payload"]
            if "response" in d:
                ret.response = d["response"]
            if "device" in d:
                for dv in d["device"]:
                    ret.device.append(self.__decode(dv, IoDeviceData))
            return ret
        if o == MediaData:
            ret = MediaData()
            if "Type" in d:
                ret.Type = d["Type"]
            if "Id" in d:
                ret.Id = d["Id"]
            if "ZoneId" in d:
                ret.ZoneId = d["ZoneId"]
            if "CameraId" in d:
                ret.CameraId = d["CameraId"]
            try:
                if "MotTrackerId" in d:
                    ret.MotTrackerId = int(str(d["MotTrackerId"]))
            except Exception as err:
                logger.warn(f"failed to cast MotTrackerId to int: {err}")
                ret.MotTrackerId = -1
            if "EdgeFilename" in d:
                ret.EdgeFilename = d["EdgeFilename"]
            if "MotEdgeFilename" in d:
                ret.MotEdgeFilename = d["MotEdgeFilename"]
            if "MIMEType" in d:
                ret.MIMEType = d["MIMEType"]
            if "AltText" in d:
                ret.AltText = d["AltText"]
            if "RawData" in d:
                ret.RawData = d["RawData"]
            try:
                if "DetectedStart_tm" in d:
                    ret.DetectedStart_tm = float(str(d["DetectedStart_tm"]))
            except Exception as err:
                logger.warn(f"failed to cast DetectedStart_tm to float: {err}")
                ret.DetectedStart_tm = -1
            try:
                if "DetectedEnd_tm" in d:
                    ret.DetectedEnd_tm = float(str(d["DetectedEnd_tm"]))
            except Exception as err:
                logger.warn(f"failed to cast DetectedEnd_tm to float: {err}")
                ret.DetectedEnd_tm = -1
            return ret
        if o == EventMsg:
            ret = EventMsg()
            if "EventId" in d:
                ret.EventId = d["EventId"]
            if "GroupId" in d:
                ret.GroupId = d["GroupId"]
            if "GatewayId" in d:
                ret.GatewayId = d["GatewayId"]
            if "SlaveId" in d:
                ret.SlaveId = d["SlaveId"]
            if "ControllerId" in d:
                ret.ControllerId = d["ControllerId"]
            try:
                if "Start_tm" in d:
                    ret.Start_tm = float(str(d["Start_tm"]))
            except Exception as err:
                logger.warn(f"failed to cast Start_tm to float: {err}")
                ret.Start_tm = -1
            try:
                if "End_tm" in d:
                    ret.End_tm = float(str(d["End_tm"]))
            except Exception as err:
                logger.warn(f"failed to cast End_tm to float: {err}")
                ret.End_tm = -1
            try:
                if "DetectedStart_tm" in d:
                    ret.DetectedStart_tm = float(str(d["DetectedStart_tm"]))
            except Exception as err:
                logger.warn(f"failed to cast DetectedStart_tm to float: {err}")
                ret.DetectedStart_tm = -1
            try:
                if "DetectedEnd_tm" in d:
                    ret.DetectedEnd_tm = float(str(d["DetectedEnd_tm"]))
            except Exception as err:
                logger.warn(f"failed to cast DetectedEnd_tm to float: {err}")
                ret.DetectedEnd_tm = -1
            try:
                if "Sent_tm" in d:
                    ret.Sent_tm = float(str(d["Sent_tm"]))
            except Exception as err:
                logger.warn(f"failed to cast Sent_tm to float: {err}")
                ret.Sent_tm = -1
            try:
                if "Created_tm" in d:
                    ret.Created_tm = float(str(d["Created_tm"]))
            except Exception as err:
                logger.warn(f"failed to cast Created_tm to float: {err}")
                ret.Created_tm = -1
            try:
                if "Detected_tm" in d:
                    ret.Detected_tm = float(str(d["Detected_tm"]))
            except Exception as err:
                logger.warn(f"failed to cast Detected_tm to float: {err}")
                ret.Detected_tm = -1

           
            if "mediaData" in d:
                for md in d["mediaData"]:
                    ret.mediaDataRef.append(self.__decode(md, MediaData))
            
            if "workFlow" in d:
                ret.workflow = WorkFlow()
                if "Type" in d["workFlow"]:
                    ret.workFlow.Type = d["workFlow"]["Type"]
                if "Properties" in d["workFlow"]:
                    ret.workFlow.Properties = d["workFlow"]["Properties"]
            if "Version" in d:
                ret.Version = d["Version"]
            return ret
