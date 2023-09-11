#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

# Import these attributes into other files as needed to
# identify the project version at runtime.
try:
    from .version import git_revision as __git_revision__
    from .version import version as __version__
except ImportError:
    __git_revision__ = 'Unknown'
    __version__ = 'Unknown'
