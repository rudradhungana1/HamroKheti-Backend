from rest_framework.response import Response

def combine_error_messages(errors):
    combined_message = ""
    for field, error_messages in errors.items():
        field_name = field.replace('_', ' ').capitalize()
        for error_message in error_messages:
            combined_message += f"{field_name} field: {error_message}\n"
    return combined_message.strip()