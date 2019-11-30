from honcho.config import DATA_LOG_FILENAME


def log_data(s, tag):
    if not s.endswith('\n'):
        s += '\n'

    with open(DATA_LOG_FILENAME(tag), 'a') as f:
        f.write(s)
