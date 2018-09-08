import json
import re

def string_transformer(event, context):

    # Get the strings out of the dict and into more convenient variables
    prefix_string = event['prefix_string']
    object_string = event['object_string']
    # Get the substring that stops at the first vowel
    devoweled_prefix_array = re.split('[AEIOU]', prefix_string, maxsplit=1, flags=re.IGNORECASE)[0]
    # Convert it back into a string
    devoweled_prefix_string = ''.join(devoweled_prefix_array)
    # Strip letters from the object string until we hit our first vowel
    strings_to_delete_from_object = re.split('[AEIOU]', object_string, maxsplit=1, flags=re.IGNORECASE)[0]
    devoweled_object_string = re.sub(strings_to_delete_from_object, '', object_string)
    # Ellide/Concatenate the strings
    concatenated_string = devoweled_prefix_string.title() + devoweled_object_string.lower()

    body = {
        "message": concatenated_string,
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
