#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
SINCA is The *SIsNet Compression Algorithm*, the compression algorithm used in EGNOS. Before sending EGNOS messages to the users, this compression algorithm
is applied by the SISNeT Data Server. This module implements SINCA related functions: checksum, decode, encode. The SINCA compression algorithm frequently reduces the data size to the 25% of the original size.
"""

__author__ = "Jonatan Morales"
__version__ = "0.1.beta"

from textwrap import wrap

import logging

log = logging.getLogger(__name__)

def checksum(msg_decompressed):
    """Receives a decompressed Egnos message as strig,
    for example data="5363FB8000000000000003BBBBBBA0343004FE7F00A0C57D212FA7FD9274C9C0" (hex bytes).
    Returns the checksum in hex based on xor byte calculation 0x53 ^ 0x63 ^ 0xFB ^ 0x80......
    For the data example would be 0x71
    """

    # Received message should be a decompressed one
    if msg_decompressed.count('|')!=0 or msg_decompressed.count('/')!=0:
        log.error("ERROR: Received message seems to be compressed. Decompress it first.")
        return -1

    bytes_str = []
    checksum = 0x00

    bytes_str = wrap(msg_decompressed,2)
    # if len(bytes_str[-1]) == 1:
    #     bytes_str[-1] = "0"+bytes_str[-1]
    #     log.debug("bytes = %s", bytes_str)
    for byte_str in bytes_str:
        try:
            byte = int(byte_str, 16)
        except:
            return -1
        checksum=checksum ^ byte
    return checksum

def compress(msg):
    """Compress a message consisting on hex digits using sinca method."""

    # Checkcum of received message
    msg_checksum_hex = checksum(msg)
    if msg_checksum_hex == -1:
        return -1

    # Locate at the begining of the string
    i=0

    # SINCA algorithm. Message compression
    msg_compressed=''
    while i<len(msg):
        # Extract next digit
        digit=msg[i]

        # Analyze next digits
        repetitions=1
        j=i+1
        while j<len(msg) and msg[j]==digit:
            repetitions+=1
            j+=1
        if repetitions<4:
            i+=1
            msg_compressed+=digit
        elif repetitions>=4 and repetitions<=15:
            i=j
            msg_compressed+="%s|%X" % (digit,repetitions)
        elif repetitions>15:
            i=j
            msg_compressed+="%s/%X" % (digit,repetitions)

    # Add the checksum
    msg_compressed+="*%X" % msg_checksum_hex

    return msg_compressed

def decompress(msg_compressed_with_checksum, format='hex'):
    """ Decode a SINCA message. The message (msg) structure is:
    hex_data_of_message_compressed_using_SINCA*checksum_in_hex.
    By default message is returned as hexadecimal, but if specified
    format='bin' then it will return it as bits.
    """
    try:
        msg_compressed = msg_compressed_with_checksum.split('*')[0]
        msg_checksum_str = msg_compressed_with_checksum.split('*')[1]
    except:
        return -1
    msg_checksum_hex = int(msg_checksum_str,16)
    msg_decompressed = ''
    checksum_calculated = 0

    msg_compressed_length = len(msg_compressed)
    log.debug(msg_compressed_length)

    if msg_compressed_length == 0:
        log.error("Compressed message length is zero !")
        return -1

    ignore_chars = 0
    for i in range(0, msg_compressed_length):
        if ignore_chars:
            ignore_chars -= 1
        else:
            z = msg_compressed[i]
            if z == "|":
                z = ""
                x = msg_compressed[i-1]
                y = msg_compressed[i+1]
                z = x*(int(y,16)-1) # Previus char was already read
                ignore_chars = 1
            elif z == "/":
                z = ""
                x = msg_compressed[i-1]
                y = msg_compressed[i+1:i+3]
                z += x*(int(y,16)-1)
                ignore_chars = 2
            msg_decompressed += z

    checksum_calculated = checksum(msg_decompressed)

    if msg_checksum_hex != checksum_calculated:
        log.error("Error: Checksum error decompressing message %s", msg_compressed_with_checksum)
        log.info("checksum=%s but calculated=%s", msg_checksum_hex, checksum_calculated)
        return -1

    if format == 'bin':
        return bin(int(msg_decompressed, base=16))
    else:
        return msg_decompressed
