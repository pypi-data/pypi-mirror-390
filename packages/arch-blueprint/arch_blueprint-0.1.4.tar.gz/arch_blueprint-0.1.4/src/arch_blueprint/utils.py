def filter_substr(string_set: set[str]):
    sorted_strings = sorted(string_set, key=len, reverse=True)
    result = set()

    for i, string in enumerate(sorted_strings):
        is_substring = False
        for longer_string in list(result):
            if string in longer_string:
                is_substring = True
                break

        if not is_substring:
            result.add(string)

    return result
