class LightspeedError(Exception):
    pass


def validate(expr: bool, exception: str = chr(32)) -> None:
    if not expr:
        raise LightspeedError(exception)
