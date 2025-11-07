class HiddenString(str):
    def __repr__(self):
        return "**********"


def calculate_list_indent(lst):
    indentation = 1
    count = len(lst)
    start = 1
    while start < count:
        start *= 10
        indentation += 1
    return indentation

def user_confirmation(prompt: str, options: str = '("yes" to confirm) [no]:') -> bool:  # pragma: no cover  (manually tested on Oct 30, 2023)
    """Confirm some action with the user. User has to fully type out "Yes" for this to return true (case insensitive).

    Args:
        prompt (str): The prompt to display to the user.
        options (str): These options is a simple string that is concatenated to the end of the prompt.

    Returns:
        bool: True only if the user responded "Yes" to the prompt (case insensitive).
    """
    user_response = (
        input(f'\n>>>    {prompt} {options} ')
        or 'no'
    )
    return user_response.lower().strip().startswith('yes')


def pluralize(class_name: str) -> str:
    name = class_name
    plural_already_words = [
        "Contacts",
        "Info",
        "RR",
        "RRADDR",
        "RRCNAME",
        "RRDS",
        "RRHINFO",
        "RRLOC",
        "RRMX",
        "RRNAPTR",
        "RRNS",
        "RRPTR",
        "RRSRV",
        "RRTXT",
        "Queries",
        "pants",
    ]
    if any(
        name.lower().endswith(plural_word.lower())
        for plural_word in plural_already_words
    ):
        # If a word is already plural, do nothing to it
        return name
    elif name.endswith("Alias"):
        return f"{name[:-5]}Aliases"
    elif name.endswith("Status"):
        return f"{name[:-6]}Statuses"
    elif name.endswith("ss") or name.endswith("sh") or name.endswith("ch"):
        #  6. If the singular noun ends in  -ss, -sh, or -ch, you usually add -es to the end to make it plural.
        return f"{name}es"
    elif name.endswith("is"):
        #  5. If the singular noun ends in -is, the plural ending is -es.
        return f"{name[:-2]}es"
    elif (
        name.endswith("y")
        and not name.endswith("ay")
        and not name.endswith("ey")
        and not name.endswith("iy")
        and not name.endswith("oy")
        and not name.endswith("uy")
    ):
        #  4. If a singular noun ends in -y and the letter before the -y is a consonant, you usually change the ending to -ies to make the noun plural.
        return f"{name[:-1]}ies"
    elif name.endswith("o"):
        #  3. If the singular noun ends in -o, you usually add -es to make it plural.
        return f"{name}es"
    elif name.endswith("s") or name.endswith("x") or name.endswith("z"):
        #  7. If the singular noun ends in -s, -x, or -z, you usually add -es to the end to make it plural.
        return f"{name}es"
    else:
        #  2. If the singular noun ends in -y and the letter before the -y is a vowel, simply add an -s to make it plural.
        #  1. Also, to make regular nouns plural, add -s to the end.
        return f"{name}s"
