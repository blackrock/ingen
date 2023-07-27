import os

ENVIRONMENT_VAR_PATTERN = "$$"


def var_starts_with(var, pattern) -> bool:
    """
    Helper function to check if variable starts with the given pattern
    :param var: string
    :param pattern: string
    :return: boolean
    """
    return var.startswith(pattern)


def get_environment_value(var: str) -> str:
    """
    Helper function to get environment variable
    :param var: key of environment variable
    :return: environment variable value
    """
    return os.getenv(var)
