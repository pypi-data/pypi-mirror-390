def snake_to_camel(src: str) -> str:
    words = src.split("_")
    if len(words) > 0:
        return words[0] + "".join(word.title() for word in words[1:])
    return src


def snake_to_pascal(src: str) -> str:
    words = src.split("_")
    if len(words) > 0:
        return "".join(word.title() for word in words)
    return src
