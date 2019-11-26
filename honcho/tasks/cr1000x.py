from honcho.util import fail_gracefully, log_execution


@fail_gracefully
@log_execution
def execute():
    raise NotImplementedError


if __name__ == '__main__':
    execute()
