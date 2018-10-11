"""Responds to a custom Slack slash command that takes any number of strings,
truncates the first before the first instance of any vowel then left-strips
the next string until the first instance of any vowel (preserves the vowel)
and concatenates the strings. This is done for any number of pairs of words,
then joins them all with ' ' and returns it in-line in Slack.

Usage:
/slack_command_name arg1 arg2 arg3 arg4"""

import json
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

def split_string(str):
    """Return an array containing [start_string, end_string]."""
    str = str.lower()
    start = ''
    end = list(str)
    str = list(str)

    # Add all preceding vowels to the start string and remove them from
    # the start of the rest.
    while len(str) > 0 and str[0] in 'aeiou:':
        start += str.pop(0)

    # Add all consonants up to the first vowel in the remaining str to
    # the start string and remove from the start of the rest.
    while len(str) > 0 and not str[0] in 'aeiou':
        start += str.pop(0)

    # Add a 'u' if the start ends with a 'q'
    if start[-1] == 'q':
        start += 'u'

    # Remove all preceding consonants from the end string
    while len(end) > 0 and not end[0] in 'aeiou':
        end.pop(0)

    return [''.join(start), ''.join(end)]

def string_transformer(event, context):
    """Handle the incoming strings sent from a custom Slack slash command,
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

    strings = request_data['text'].split(' ')
    out = []

    # Add pairs of merged strings to the output
    while len(strings) > 1:
        out.append(split(strings.pop(0))[0], split(strings.pop(0))[1])

    # Add a trailing spare word if there is one
    if len(strings) > 0:
        out.append(strings[0])

    response = {
        "response_type": "in_channel",
        "text": ''.join(out).capitalize(),
    }

    return {
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"},
        "statusCode": 200,
    }
