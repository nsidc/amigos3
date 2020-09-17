def import_task(name):
    task = __import__('honcho.tasks.{0}'.format(name), fromlist=[None])

    return task
