#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
ESA DS2DC protocol is a protocol that works with text strings via TCP/IP. A client able to send and receive commands under DS2DC protocol is implemented here.
"""

__author__ = "Jonatan Morales"
__version__ = "beta.20211127"

from sisnet import sinca

import argparse
import configparser
import logging
import os
import socket

log = logging.getLogger(__name__)

class Client(object):
    """Class representing a client implementing the DS2DC protocol. Uses a socket connection to a Sisnet server. This connection can be used to receive Egnos messages from specific PRN."""

    # The UAS is the *User Application Software* and the *DS* is the Data Server.
    # The UAS and the DS interchange messages.

    # R-Messages (RM, Request messages) dictionary. Messages availables to send to DS
    R_MESSAGES = {
        'R_AUTH': "AUTH,%s,%s", # Authentication message
        'R_AUTH_WITH_RECEIVER_INIT': "AUTH,%s,%s,q",
        'R_EPHEM': "EPHEM,%s,%s",
        'R_GETMSG': "GETMSG",
        'R_GPS_IONO': "GPS_IONO",
        'R_MSG': "MSG",
        'R_START': "START",
        'R_STOP': "STOP"
    }

    # S-Messages are messages from the DS to the UAS.
    # S-Messages can be A-Messages (answers) or E-Messages (event triggered).
    # A-Messages (AM, Answer messages to previous RM) dictionary. Posible message types received from DS.
    # E-Messages (EM, Triggered)
    S_MESSAGES = { 'A_AUTH': "*AUTH",
                   'A_EPHEM': "*EPHEM",
                   'A_GETMSG': "*GETMSG",
                   'A_GPS_IONO': "*GPS_IONO",
                   'A_MSG': "*MSG",
                   'A_START': "*START",
                   'A_STOP': "*STOP",
                   'E_ERROR': "*ERR",
                   'E_TXT': "*TXT",
                   }

    # Egnos message as a dictionary with the extracted info
    egnos_message = { 'gps_week': 0,
                      'gps_time': 0,
                      'egnos_msg_hex_compressed': '', # Message is received from SiSnet server sinca-compressed
                      'egnos_msg_hex_uncompressed': '' } # Message sinca-decompressed

    def __init__(self, config_file='sisnet.conf', username='', password='', prn='', server='', port=''):
        """ Constructor for the *client* class.
        By default the config file is *sisnet.conf*. It should be located in the same folder of your python program. You can see a *sisnet.conf* sample file in the documentation.
        """

        # The message dictionary
        self.egnos_message = { 'gps_week': 0, 'gps_time': 0, 'msg_compressed': '', 'msg_uncompressed': '' }

        # The SisNet server parameters
        config = configparser.RawConfigParser()
        config.read(config_file)

        # Lets check if config file exists
        if not os.path.isfile(config_file):
            log.error("Config file '%s' not found" % config_file)
            exit(-1)
        else:
            log.debug("Reading config file...")

        # Set username from config file if not passed as parameter
        if username == '':
            try:
                self.username = config['GLOBAL']['username']
            except KeyError:
                log.error("Error in Config file '%s'. username not found in section [GLOBAL]." % config_file)
                exit(-1)
        else:
            self.username = username

        # Set password from config file if not passed as parameter
        if password == '':
            try:
                self.password = config['GLOBAL']['password']
            except KeyError:
                log.error("Error in Config file '%s'. passwrod not found in section [GLOBAL]." % config_file)
                exit(-1)
        else:
            self.password = password

        # Set PRN from config file GLOBAL section if not passed as parameter
        if prn == '':
            try:
                self.prn = config['GLOBAL']['prn']
            except KeyError:
                log.error("Error in Config file '%s'. Default prn not found in section [GLOBAL]." % config_file)
                exit(-1)
        else:
            self.prn = prn

        # Set Server (IP or Domai name) from config file if not passes as parameter
        # We take server from PRNxxx section and if not found then from GLOBAL section
        if server == '':
            try:
                self.server = config['PRN%s' % self.prn]['server']
            except KeyError:
                try:
                    self.server = config['GLOBAL']['server']
                except KeyError:
                    log.error("Error in Config file '%s'. Server in section [PRN%s] not found." % (config_file, self.prn))
                    exit(-1)
        else:
            self.server = server

        # Set port from config file if not passed as parameter
        # We take port from PRNxxx section and if not found then from GLOBAL section
        if port == '':
            try:
                self.port = int(config['PRN%s' % self.prn]['port'])
            except KeyError:
                try:
                    self.port = int(config['GLOBAL']['port'])
                except KeyError:
                    log.error("Error in Config file '%s'. 'PRN%s' not found." % (config_file, self.prn))
                    exit(-1)
        else:
            self.port = port
        #log.debug("config_file=%s, prn=%s, username=%s, server=%s, port=%s" % (config_file, self.prn,self.username,self.server,self.port) )
        log.info("Config file processed")
        log.debug("config_file=%s, prn=%s, username=****, server=****, port=%s" % (config_file, self.prn,self.port) )

    def login(self, request_message='R_AUTH'):
        """ Connects to server sending a R_AUTH message agains the SisNet server according the DS2DC protocol.
        Usage: login(). The login parameters were already readed from config file when creating the client class instance.
        It returns a response as dictionary, for example:
        response = {
            'message_type': '*ERR',
            'message_code': '3',
            'message_text': 'Unknown DS2DC Command or bad syntax'}
        In case of error connecting to server it returns -1.
        """

        data_from_DS = ""
        CRLF = "\r\n"

        # Check that request_message is one of the two allowed
        if request_message not in ['R_AUTH', 'R_AUTH_WITH_RECEIVER_INIT']:
            log.error("Message not allowed. Only R_AUTH / R_AUTH_WITH_RECEIVER_INIT are allowed for login!")
            return -1

        # Parameters already set by the constructor __init__
        username = self.username
        password = self.password
        server = self.server
        port = self.port

        R_AUTH = self.R_MESSAGES[request_message] % (username, password)
        R_AUTH_protected = self.R_MESSAGES[request_message] % ("*****", "*****")

        # Connect to DS sending AUTH message and receive the answer
        log.debug("Connecting to %s:%s ..." % (server, port))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect( (server, port) )
            log.debug("Connected !")
        except socket.error as e:
            log.error("Error: Socket connection to DS failed")
            log.error("%s" % e)
            return -1

        log.debug("Request: '%s'" % (R_AUTH_protected+CRLF).encode('utf-8'))
        try:
            self.s.send( (R_AUTH+CRLF).encode('utf-8') )
            data_from_DS = self.recv_until_CRLF()
            data_from_DS_list = data_from_DS.split(",")
        except socket.error:
            log.error("Error: Sending authenticating to DS failed")
            return -1

        log.debug("Response: '%s'" % data_from_DS)

        # Analizing message from DS
        message_type = data_from_DS_list[0]
        if len(data_from_DS_list) == 1:
            message_code = ''
            message_text = ''
        else:
            message_code = data_from_DS_list[1]
            message_text = data_from_DS_list[2]
        if message_type == self.S_MESSAGES['E_ERROR']:
            message_type = data_from_DS_list[0]
            message_code = data_from_DS_list[1]
            message_text = data_from_DS_list[2]
        elif message_type == self.S_MESSAGES['A_AUTH']:
            message_type = data_from_DS_list[0]

        login_response = {
            'message_type': message_type,
            'message_code': message_code,
            'message_text': message_text
        }
        return login_response

    def logout(self):
        self.s.close()

    def decode_egnos_message(self, message):
        """ Decode an egnos message received as string "*MSG,1042,394088,9A127FF40|53FCBFFC0/1717BB97B80|51F44C380*9F".
            Separate gps info from message and uses decompress function from sisnet.sinca for egnos message decompression. Returns a dictionary with the egnos msg info.
        """
        try:
            message = message.split(',')
        except:
            log.error("Error: Unable to split Message to decode")
            return -1
        log.info("Message: %s" % message)
        if message[0] == "*MSG" or message[0] == "*GETMSG":
            response = { 'gps_week': message[1],
                         'gps_time': message[2],
                         'egnos_msg_hex_compressed': message[3],
                         'egnos_msg_hex': sinca.decompress(message[3]) }
            log.info("Message: %s" % response)
            return response
        else:
            return -1

    def recv_until_CRLF(self):
        """Receives bytes from server through socket until a \r\n (CRLF)."""
        CRLF = '\r\n'
        CRLF_detected = False
        data = ''
        str_received = ''
        while CRLF_detected == False:
            try:
               str_received = self.s.recv(1).decode('utf-8')
            except:
                log.error("Error: Receiving data until CRLF failed")
                return -1
            if str_received == '\r':
                str_received = self.s.recv(1).decode('utf-8')
                if str_received == '\n':
                    CRLF_detected = True
            else:
                data += str_received
        return data

    def recent_egnos_message(self):
        response = self.request(self.R_MESSAGES['R_MSG'])
        return response

    def request(self, message):
        """ Send a request message to the sisnet data server (DS).
        """
        CRLF = '\r\n'
        log.info( "Request (PRN %s): %s" % (self.prn, message) )
        message = (message+CRLF).encode('utf-8')
        try:
            self.s.send(message)
        except:
            log.error("Error: Sending message to DS failed")
            return -1
        response = self.recv_until_CRLF()
        log.info("Answer: %s" % response)
        return response

    # ADM:: Analysis of DS2DC Messages

    # DA:: Decompression Algorithm

if __name__ == "__main__":

    # Arguments definition
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Output log info", action="store_true")
    parser.add_argument("-c", "--config", help="Configuration file. By default will be 'sisnet.conf'. Check more details on the documentation https://github.com/jonatanmv/sisnet#configuration")
    parser.add_argument("-r", "--request", help="Request message to be sent to the EGNOS SisNet server")

    # Parsing arguments
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    if args.config:
        print("Config file:", args.config)
        config_file = args.config
    else:
        config_file='sisnet.conf'

    if args.request:
        request = args.request
    else:
        request = None

    # Client and request
    if request:
        client = Client(config_file=config_file)
        client.login()
        answer = client.request(request)
        answer_decoded = client.decode_egnos_message(answer)
