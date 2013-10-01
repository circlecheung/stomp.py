import uuid

import utils
from listener import *
from backward import pack, encode, hasbyte
from constants import *


class Protocol10(ConnectionListener):
    def __init__(self, transport):
        self.transport = transport
        transport.set_listener('protocol-listener', self)
        self.version = 1.0

    def __send_frame(self, cmd, headers = {}, body = ''):
        frame = utils.Frame(cmd, headers, body)
        self.transport.send_frame(frame)

    def abort(self, transaction, headers = {}, **keyword_headers):
        assert transaction is not None, "'transaction' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        headers[HDR_TRANSACTION] = transaction
        self.__send_frame(CMD_ABORT, headers)

    def ack(self, id, transaction = None):
        assert id is not None, "'id' is required"
        headers = { HDR_ID : id }
        if transaction:
            headers[HDR_TRANSACTION] = transaction
        self.__send_frame(CMD_ACK, headers)

    def begin(self, transaction = None, headers = {}, **keyword_headers):
        headers = utils.merge_headers([headers, keyword_headers])
        if not transaction:
            transaction = str(uuid.uuid4())
        headers[HDR_TRANSACTION] = transaction
        self.__send_frame(CMD_BEGIN, headers)
        return transaction

    def commit(self, transaction = None, headers = {}, **keyword_headers):
        assert transaction is not None, "'transaction' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        headers[HDR_TRANSACTION] = transaction
        self.__send_frame('COMMIT', headers)

    def connect(self, username=None, passcode=None, wait=False):
        cmd = CMD_CONNECT
        headers = {
            HDR_ACCEPT_VERSION : self.version
        }
        
        if username is not None:
            headers[HDR_LOGIN] = username

        if passcode is not None:
            headers[HDR_PASSCODE] = passcode

        self.__send_frame(cmd, headers)
        
        if wait:
            self.transport.wait_for_connection()

    def disconnect(self, receipt = str(uuid.uuid4()), headers = {}, **keyword_headers):
        headers = utils.merge_headers([headers, keyword_headers])
        if receipt:
            headers[HDR_RECEIPT] = receipt
        self.__send_frame(CMD_DISCONNECT, headers)

    def send(self, destination, body, content_type = None, headers = {}, **keyword_headers):
        assert destination is not None, "'destination' is required"
        assert body is not None, "'body' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        headers[HDR_DESTINATION] = destination
        if content_type:
            headers[HDR_CONTENT_TYPE] = content_type
        body = encode(body)
        if HDR_CONTENT_LENGTH not in headers:
            headers[HDR_CONTENT_LENGTH] = len(body)
        self.__send_frame(CMD_SEND, headers, body)

    def subscribe(self, destination, id=None, ack = 'auto', headers = {}, **keyword_headers):
        assert destination is not None, "'destination' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        headers[HDR_DESTINATION] = destination
        if id:
            headers[HDR_ID] = id
        headers[HDR_ACK] = ack
        self.__send_frame(CMD_SUBSCRIBE, headers)

    def unsubscribe(self, destination = None, id = None, headers = {}, **keyword_headers):
        assert id is not None or destination is not None, "'id' or 'destination' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        if id:
            headers[HDR_ID] = id
        if destination:
            headers[HDR_DESTINATION] = destination
        self.__send_frame(CMD_UNSUBSCRIBE, headers)


class Protocol11(HeartbeatListener, ConnectionListener):
    def __init__(self, transport, heartbeats = (0, 0)):
        HeartbeatListener.__init__(self, heartbeats)
        self.transport = transport
        transport.set_listener('protocol-listener', self)
        self.version = 1.1

    def __send_frame(self, cmd, headers = {}, body = ''):
        frame = utils.Frame(cmd, headers, body)
        self.transport.send_frame(frame)

    def abort(self, transaction, headers = {}, **keyword_headers):
        assert transaction is not None, "'transaction' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        headers[HDR_TRANSACTION] = transaction
        self.__send_frame(CMD_ABORT, headers)

    def ack(self, id, transaction = None):
        assert id is not None, "'id' is required"
        headers = { HDR_ID : id }
        if transaction:
            headers[HDR_TRANSACTION] = transaction
        self.__send_frame(CMD_ACK, headers)

    def begin(self, transaction = None, headers = {}, **keyword_headers):
        headers = utils.merge_headers([headers, keyword_headers])
        if not transaction:
            transaction = str(uuid.uuid4())
        headers[HDR_TRANSACTION] = transaction
        self.__send_frame(CMD_BEGIN, headers)
        return transaction

    def commit(self, transaction = None, headers = {}, **keyword_headers):
        assert transaction is not None, "'transaction' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        headers[HDR_TRANSACTION] = transaction
        self.__send_frame('COMMIT', headers)

    def connect(self, username=None, passcode=None, wait=False):
        cmd = CMD_STOMP
        headers = {
            HDR_ACCEPT_VERSION : self.version
        }
        
        if self.transport.vhost:
            headers[HDR_HOST] = self.transport.vhost

        if username is not None:
            headers[HDR_LOGIN] = username

        if passcode is not None:
            headers[HDR_PASSCODE] = passcode

        self.__send_frame(cmd, headers)
        
        if wait:
            self.transport.wait_for_connection()

    def disconnect(self, receipt = str(uuid.uuid4()), headers = {}, **keyword_headers):
        headers = utils.merge_headers([headers, keyword_headers])
        if receipt:
            headers[HDR_RECEIPT] = receipt
        self.__send_frame(CMD_DISCONNECT, headers)

    def nack(self, id, transaction = None):
        assert id is not None, "'id' is required"
        headers = { HDR_ID : id }
        if transaction:
            headers[HDR_TRANSACTION] = transaction
        self.__send_frame(CMD_NACK, headers)

    def send(self, destination, body, content_type = None, headers = {}, **keyword_headers):
        assert destination is not None, "'destination' is required"
        assert body is not None, "'body' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        headers[HDR_DESTINATION] = destination
        if content_type:
            headers[HDR_CONTENT_TYPE] = content_type
        body = encode(body)
        if HDR_CONTENT_LENGTH not in headers:
            headers[HDR_CONTENT_LENGTH] = len(body)
        self.__send_frame(CMD_SEND, headers, body)

    def subscribe(self, destination, id, ack = 'auto', headers = {}, **keyword_headers):
        assert destination is not None, "'destination' is required"
        assert id is not None, "'id' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        headers[HDR_DESTINATION] = destination
        headers[HDR_ID] = id
        headers[HDR_ACK] = ack
        self.__send_frame(CMD_SUBSCRIBE, headers)

    def unsubscribe(self, id, headers = {}, **keyword_headers):
        assert id is not None, "'id' is required"
        headers = utils.merge_headers([headers, keyword_headers])
        headers[HDR_ID] = id
        self.__send_frame(CMD_UNSUBSCRIBE, headers)


class Protocol12(Protocol11):
    def __init__(self, transport, heartbeats = (0, 0)):
        Protocol11.__init__(self, transport, heatbeats = (0, 0))
        self.version = 1.2