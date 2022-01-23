#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from sisnet import sinca
from sisnet import ds2dc

def using_sinca():

    log.info('Testing SINCA module...')

    # Compressed message with checksum
    msg = "9A127FF40|53FCBFFC0/1717BB97B80|51F44C380*9F"

    # Decompress
    log.info('Decompressing and compressing message...')
    msg_decompressed = sinca.decompress(msg)
    msg_checksum = sinca.checksum(msg_decompressed)
    # msg_decompressed = "9A127FF4000003FCBFFC0000000000000000000000017BB97B8000001F44C380"
    if msg_decompressed==-1:
        return -1
    log.info("Compressed   message = %s",msg)
    log.info("Decompressed message = %s (checksum=%X)",msg_decompressed, msg_checksum)
    # Compress
    msg=sinca.compress(msg_decompressed)
    log.info("Compressed   message = %s",msg)

    # Testing another message
    log.info('Decompressing and compressing message...')
    msg = "9A0D0/243FC3B|B8FB6CE34*18"
    msg_decompressed = sinca.decompress(msg)
    msg_checksum = sinca.checksum(msg_decompressed)
    log.info("Compressed   message = %s",msg)
    log.info("Decompressed message = %s (checksum=%X)",msg_decompressed, msg_checksum)
    log.info("Compressing message...")
    msg=sinca.compress(msg_decompressed)
    log.info("Compressed   message = %s",msg)

def using_ds2dc():

    # What messages to test
    test_messages = {
        'R_AUTH_WITH_RECEIVER_INIT': False,
        'MSG': True,
        'GETMSG': False,

    }
    log.debug("test_messages = %s", test_messages)

    # SisNet Clients creation
    # You can overrride all parameters (prn,username,password,ip,port)
    # from sisnet.conf file passing them as parameters.
    log.info('Creating client...')
    client=ds2dc.Client(config_file='../../private/sisnet.conf')

    # SisNet Clients login
    # Login with R_AUTH_WITH_RECEIVER_INIT request
    if test_messages['R_AUTH_WITH_RECEIVER_INIT']:
        log.info('Login with R_AUTH_WITH_RECEIVER_INIT request...')
        response = client.login(request_message='R_AUTH_WITH_RECEIVER_INIT')
    else:
        log.info('Login with R_AUTH request...')
        client.login()

    # Some request to the DS (Data Server)

    # MSG
    if test_messages['MSG']:
        answer = client.request("MSG")
        answer_decoded = client.decode_egnos_message(answer)
        client.decode_egnos_message(client.request("MSG"))
        client.request("GPS_IONO")

    # GETMSG
    if test_messages['GETMSG']:

        log.info("Satellite information messages...")
        answer = client.request("GETMSG,1,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,3,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,6,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,7,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,9,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,17,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,24,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,25,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,28,0")
        answer_decoded = client.decode_egnos_message(answer)

        log.info("Ionospheric information messages...")
        answer = client.request("GETMSG,18,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,26,1")
        answer_decoded = client.decode_egnos_message(answer)

        log.info("Other messages...")
        answer = client.request("GETMSG,0,0")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,10,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,12,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,27,1")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,62,0")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,63,0")
        answer_decoded = client.decode_egnos_message(answer)

        log.info("SBAS L5 Messages...")
        answer = client.request("GETMSG,31,0")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,32,0")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,34,0")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,35,0")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,36,0")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,39,0")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,37,0")
        answer_decoded = client.decode_egnos_message(answer)
        answer = client.request("GETMSG,47,0")
        answer_decoded = client.decode_egnos_message(answer)


    #

if __name__ == "__main__":

    log = logging.getLogger("sisnet")
    log.info('Testing SisNet Python modules ...')

    # Lets try sinca to decode a message
    #using_sinca()

    # Lets get some EGNOS messages
    using_ds2dc()
