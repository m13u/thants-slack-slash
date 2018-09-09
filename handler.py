# 'Inspired' liberally by https://grundleborg.github.io/posts/mattermost-custom-slash-command-aws-lambda/
import json
import re
from urllib.parse import parse_qsl

def parse_input(data):
    parsed = parse_qsl(data, keep_blank_values=True)
    result = {}
    for item in parsed:
        result[item[0]] = item[1]
    return result

def string_devoweler(input_string):
    output_string = re.split('[AEIOU]', input_string, maxsplit=1, flags=re.IGNORECASE)[0]
    return output_string

def string_transformer(event, context):
    try:
        request_data = parse_input(event['body'])
    except:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": "{}",
        }

    request_text = request_data['text']
    prefix_string = request_text.split(' ', 1)[0]
    object_string = request_text.split(' ', 1)[1]
    # Get the substring that stops at the first vowel
    devoweled_prefix_array = string_devoweler(prefix_string)
    # Convert it back into a string
    devoweled_prefix_string = ''.join(devoweled_prefix_array)
    # Strip letters from the object string until we hit our first vowel
    strings_to_delete_from_object = string_devoweler(object_string)
    devoweled_object_string = re.sub(strings_to_delete_from_object, '', object_string)
    # Ellide/Concatenate the strings
    concatenated_string = devoweled_prefix_string.title() + devoweled_object_string.lower()

    response = {
        "response_type": "in_channel",
        "text": concatenated_string,
    }

    return {
        "body": json.dumps(response),
        "headers": { "Content-Type": "application/json" },
        "statusCode": 200,
    }
