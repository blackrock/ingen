#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os.path
import uuid
from datetime import datetime

from ingen.utils.properties import Properties


def token_secret(token_name, params=None):
    """
    Gets secret file path from token value
    Decrypts the file content
    @param token_name: Name of the token containing path of the encrypted file
    """
    filepath = Properties.get_property(token_name)
    if filepath is None:
        raise ValueError(f"'{token_name}' not found")
    raise Exception('Not implemented. Dependent on BLK libraries.')
    # return decrypt(infile=filepath)


def timestamp(format, params=None):
    """
    Gets date format from the user and returns timestamp in that format
    """

    datetimeobj = datetime.now()
    if format is None:
        raise ValueError(f"'{format}' not given by the user")
    timestampstr = datetimeobj.strftime(format)
    return timestampstr


def uuid_func(args=None, params=None):
    """
    Creates a random UUID
    """

    return str(uuid.uuid4())


def get_infile(args, params):
    """
    return file name from command line parameters
    """

    file_name = os.path.basename(params['infile'])
    return file_name


COMMON_INTERPOLATORS = {
    'token': Properties.get_property,
    'token_secret': token_secret,
    'timestamp': timestamp,
    'uuid': uuid_func,
    'infile': get_infile

}
