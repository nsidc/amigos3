import logging

KEY_FILE = '/root/.ssh/id_rsa_windows'

logger = logging.getLogger(__name__)


class SSH:
    def __init__(self, username, hostname):
        """Init

        Arguments:
            username {str} -- user name of the client server
            hostname {str} -- the Ip of the client server as '00.00.00.00'
        """
        self.hosname = hostname
        self.username = username

    def copy(self, source, dest, recursive=False):
        """copy file from/to host

        Arguments:
            filename {str} -- path to the file
            dest {str} -- destination path

        Keyword Arguments:
            recursive {bool} -- A recursive copy  (default: {False})

        Returns:
            [list] -- Result of the copy
        """
        from subprocess import check_call

        cmd = "scp {opts} -i {key} {user}@{host}:{source} {dest}".format(
            opts='-r' if recursive else '',
            key=KEY_FILE,
            user=self.username,
            host=self.hosname,
            source=source,
            dest=dest,
        )

        logger.info('Executing {cmd}'.format(cmd=cmd))
        check_call(cmd, shell=True)

    def execute(self, command):
        """Execute a command of client

        Arguments:
            command {str} -- command to execute remotely

        Returns:
            out -- Result of the execution
        """
        from subprocess import check_call

        cmd = 'ssh -i {key} {user}@{host} "{command}"'.format(
            key=KEY_FILE, user=self.username, host=self.hosname, command=command
        )

        logger.info('Executing {cmd}'.format(cmd=cmd))
        check_call(cmd, shell=True)
