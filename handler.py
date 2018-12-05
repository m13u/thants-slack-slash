"""Responds to a custom Slack slash command that takes two parameters: a prefix
string and an object (target) string. Truncate the prefix string before the
first instance of any vowel. Then left-strip the object string until the first
instance of any vowel (preserve the vowel). Then concatenate the strings and
return it in-line in Slack.

Usage:
/slack_command_name prefix_string object_string"""

import json
import re
import os
from urllib.parse import parse_qsl

def parse_input(data):
    """Convert data of type application/x-www-form-urlencoded received from
    Slack into a dict of values for easier access."""
    parsed = parse_qsl(data, keep_blank_values=True)
    result = {}
    for item in parsed:
        result[item[0]] = item[1]
    return result

def validate_token(request_slack_token):
    """Make sure the Slack token being sent in the request matches the one
    we've set as an environment variable."""
    if request_slack_token == os.environ['SLACK_TOKEN']:
        return
    else:
        raise ValueError

def string_devoweler(input_string):
    """Return a substring that has all the characters up to (but not including)
    the first instance of any vowel"""
    # Always preserve the first letter, even if it's a vowel, so exclude it from the substitution
    string_to_disemvowel = input_string[1:]
    # re.split returns an array, not a string, so we have to convert it back into a string
    output_array = re.split('[AEIOU]', string_to_disemvowel, maxsplit=1, flags=re.IGNORECASE)[0]
    # Add the first letter back in and concatenate it with the devoweled-chomped string
    output_string = input_string[:1] + ''.join(output_array)
    return output_string

def string_transformer(event, context):
    """Handle the two incoming strings sent from a custom Slack slash command,
    modify and concatenate the strings and return it in-line in Slack."""
    try:
        request_data = parse_input(event['body'])
    except SyntaxError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": "{}",
        }

    request_slack_token = request_data['token']

    try:
        validate_token(request_slack_token)
    except ValueError:
        return {
            "statusCode": 403,
            "headers": {"Content-Type": "application/json"},
            "body": "{}",
        }

    request_text = request_data['text']
    prefix_string = request_text.split(' ', 1)[0]
    object_string = request_text.split(' ', 1)[1]

    devoweled_prefix_string = string_devoweler(prefix_string)
    # If the object string starts with a vowel, just keep the entire string
    if set('aeiou').intersection(object_string[0].lower()):
        concatenated_string = devoweled_prefix_string.title() + object_string.lower()
    else:
        # Strip letters from the object string until we hit our first vowel
        string_to_delete_from_object = string_devoweler(object_string)
        devoweled_object_string = re.sub(string_to_delete_from_object, '', object_string, 1)
        # Ellide/Concatenate the strings
        concatenated_string = devoweled_prefix_string.title() + devoweled_object_string.lower()

    response = {
        "response_type": "in_channel",
        "text": concatenated_string,
    }

    return {
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"},
        "statusCode": 200,
    }
