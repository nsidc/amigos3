from honcho.config import DATA_LOG_FILENAME, SEP


def log_serialized(s, tag):
    if not s.endswith('\n'):
        s += '\n'

    with open(DATA_LOG_FILENAME(tag), 'a') as f:
        f.write(s)


def serialize(sample, conversions):
    converted = []
    for key in sample._fields:
        try:
            value = getattr(sample, key)
            converted.append(conversions[key].format(value))
        except Exception:
            converted.append(str(value))
    serialized = SEP.join(converted)

    return serialized


def deserialize(serialized, conversions, constructor):
    split = serialized.split(SEP)

    deserialized = constructor(
        **dict((key, conversions[key](split[i])) for i, key in enumerate(conversions))
    )

    return deserialized


def print_samples(samples, conversion):
    print(', '.join(samples[0]._fields))
    print('-' * 80)
    for sample in samples:
        print(serialize(sample, conversion).replace(SEP, ', '))
