#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
import os.path

from ingen.validation.send_email import send_email

log = logging.getLogger()


def get_attributes(params, validation_action):
    validate_action_to_adr = validation_action.get("send_email")
    run_date = params.get("run_date")
    file_name = params.get("infile")
    if file_name:
        file_name = os.path.basename(file_name)
    validate_action_attributes = {
        "run_date": run_date,
        "validate_action_to_adr": validate_action_to_adr,
        "file_name": file_name,
    }
    return validate_action_attributes


def email_attributes(params, validation_action, validation_summary):
    """
    sends an email if to_address is mentioned
    :param params : Has all the attributes required to send the email
    :param validation_action: list of email
    :param validation_summary: Dictionary of source name and their validation summary
    """
    validation_action_attributes = get_attributes(params, validation_action)
    validation_action_to_address = validation_action_attributes.get(
        "validate_action_to_adr"
    )
    run_date = str(validation_action_attributes.get("run_date"))
    file_name = str(validation_action_attributes.get("file_name"))
    subject = "Data Validation Failure (" + run_date + ")"
    validation_failure = False
    email_body = str()

    for source_name, validation_result in validation_summary.items():
        # Popping the severity to reach the logs
        validation_result = validation_result[1:]

        if validation_result:
            validation_failure = True
            email_body += "\nValidation Status for source: " + str(source_name) + "\n"
            if file_name:
                email_body += "File Name: " + file_name + "\n\n"
            for log_messages in validation_result:
                email_body += log_messages + "\n"

    if validation_failure:
        send_email(validation_action_to_address, email_body, subject)
    if "blocker" in str(validation_summary):
        raise ValueError(
            f"Error while Validating interface file for the columns having severity as blocker"
        )
