"""glob2regex main file."""

__version__ = "0.1.0"

def glob2regex(glob: str, *, extended: bool = False, glob_star: bool = False, flags: str = "") -> str:
    r"""Glob to regex function.

    :param glob:  Glob String
    :param extended: # Extended:
    # Whether we are matching so called 'extended' globs (like bash) and should
    # support single character matching, matching ranges of characters, group
    # matching, etc.
    # If we are doing extended matching, this boolean is true when we are inside
    # a group (eg {*.html,*.js}), and false otherwise.
    :param glob_star: # When glob_star is False (default), '/foo/*' is translated a regexp like
    # '^\/foo\/.*$' which will match any string beginning with '/foo/'
    # When glob_star is True, '/foo/*' is translated to regexp like
    # '^\/foo\/[^/]*$' which will match any string beginning with '/foo/' BUT
    # which does not have a '/' to the right of it.
    # E.g. with '/foo/*' these will match: '/foo/bar', '/foo/bar.txt' but
    # these will not '/foo/bar/baz', '/foo/bar/baz.txt'
    # Lastly, when glob_star is True, '/foo/**' is equivalent to '/foo/*' when
    # glob_star is False
    :param flags: RegExp flags (eg 'i' ) to pass in to RegExp constructor.
    :return: str.
    """
    glob_list = list(glob)
    glob_list_len = len(glob_list)

    # The regexp we are building, as a string.
    regex_str = ""


    in_group = False

    for i, c in enumerate(glob_list):
        if c in ["/", "$", "^", "+", ".", "(", ")", "=", "!", "|"]:
            regex_str += "\\" + c
        elif c == "?":
            if extended:
                regex_str += "."
        elif c in ["[", "]"]:
            if extended:
                regex_str += c
        elif c == "{":
            if extended:
                in_group = True
                regex_str += "("
        elif c == "}":
            if extended:
                in_group = False
                regex_str += ")"
        elif c == ",":
            if in_group:
                regex_str += "|"
            regex_str += "\\" + c
        elif c == "*":
            # Move over all consecutive '*''s.
            # Also store the previous and next characters
            prev_char = glob_list[i - 1]
            start_count = 1

            while (i - 1) < glob_list_len and glob_list[i - 1] == "*":
                start_count += 1
                i += 1

            next_char = glob_list[i + 1] if (i + 1) < glob_list_len else None

            if not glob_star:
                # glob_star is disabled, so treat any number of '*' as one
                regex_str += ".*"
            else:
                # glob_star is enabled, so determine if this is a glob_star segment
                is_glob_star = start_count > 1 and (prev_char == "/" or not prev_char) and (next_char == "/" or not next_char)
                if is_glob_star:
                    regex_str += r"((?:[^/]*(?:\/|$))*)"
                    i += 1
                else:
                    regex_str += "([^/]*)"
        else:
            regex_str += c

    # When regexp 'g' flag is specified don't
    # constrain the regular expression with ^ & $
    if not flags or "g" not in flags:
        regex_str = f"^{regex_str}$"

    return regex_str
