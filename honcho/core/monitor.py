from honcho.util import fail_gracefully


@fail_gracefully
def execute():
    raise NotImplementedError


if __name__ == '__main__':
    execute()
