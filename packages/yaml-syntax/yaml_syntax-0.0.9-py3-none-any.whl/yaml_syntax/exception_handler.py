
from pydantic import ValidationError


# TODO: alsoe handle for type error
# like if version must be str but input version is int in yaml file
def default_syntax_error_message(error: ValidationError) -> str:
    """
    get erro message of from pydantic parser

    Args:
        error (ValidationError): validation error of pydantic

    Returns:
        str: return of helpful message
    """

    error_messages = []
    for err in error.errors():

        loc = ".".join(str(l) for l in err["loc"])
        error_type = err["type"]
        input_value = err.get("input", "unknow")

        match error_type:
            case "missing":
                error_messages.append(
                    f"error on {loc}: this field is required and can not be empty."
                )

            case "extra_forbidden":
                input_value = loc.split(".")[-1]
                error_messages.append(
                    f"error on {loc}: The '{input_value}' field is not valid."
                )

            case _ if error_type.startswith("type_error"):
                error_messages.append(
                    f"error on {loc}: The type of '{input_value}' is not valid. Error because type of field."
                )
            case _:
                error_messages.append(
                    f"error on {loc}: unexcepted error!"
                )

    return "\n".join(error_messages)

