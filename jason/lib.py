VERBOSE = False


def log(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)
