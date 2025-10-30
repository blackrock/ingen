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
    infile = params.get('infile') if params else None
    if infile is None:
        return ''

    if isinstance(infile, dict):
        if args is None or args == '':
            raise ValueError("infile interpolator requires a key when --infile is provided as a mapping")
        if args not in infile:
            raise KeyError(f"No infile override found for '{args}'")
        return os.path.basename(infile[args])
    
    # Handle the case when infile is a simple string path
    return os.path.basename(infile)


def get_overrides(args, params):
    """
    return overrides from command line parameters
    """
    override_params = params.get('override_params') if params else None
    return override_params.get(args, '') if override_params else ''


COMMON_INTERPOLATORS = {
    'token': Properties.get_property,
    'token_secret': token_secret,
    'timestamp': timestamp,
    'uuid': uuid_func,
    'infile': get_infile,
    'override': get_overrides

}
