class SSH:
    def __init__(self, username, hostname):
        """Init

        Arguments:
            username {str} -- user name of the client server
            hostname {str} -- the Ip of the client server as '00.00.00.00'
        """
        self.hosname = hostname
        self.username = username

    def copy(self, filename, dest, recursive=False, from_host=False):
        """copy file from/to host

        Arguments:
            filename {str} -- path to the file
            dest {str} -- destination path

        Keyword Arguments:
            recursive {bool} -- A recursive copy  (default: {False})
            from_host {bool} -- Direction of copy (default: {False})

        Returns:
            [list] -- Result of the copy
        """
        from subprocess import PIPE, Popen

        out = None
        if not from_host:
            if not recursive:
                p = Popen(
                    "scp -i id_rsa_windows {0}@{1}:{2} {3}".format(
                        self.username, self.hosname, filename, dest
                    ),
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                    shell=True,
                )
                out = p.communicate()
                recursive = False
                return out
            p = Popen(
                "scp -i id_rsa_windows -r {0}@{1}:{2} {3}".format(
                    self.username, self.hosname, filename, dest
                ),
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                shell=True,
            )
            out = p.communicate()
        else:
            if not recursive:
                p = Popen(
                    "scp -i id_rsa_windows {3} {0}@{1}:{2}".format(
                        self.username, self.hosname, filename, dest
                    ),
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                    shell=True,
                )
                out = p.communicate()
                recursive = False
                return out
            p = Popen(
                "scp -i id_rsa_windows -r  {3} {0}@{1}:{2} {3}".format(
                    self.username, self.hosname, filename, dest
                ),
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                shell=True,
            )
            out = p.communicate()

        return out

    def execute(self, commands):
        """Execute a command of client

        Arguments:
            command {str} -- commands; can be a list of command

        Returns:
            [list] -- Result of the execution
        """
        from subprocess import PIPE, Popen
        from time import sleep

        outt = ""
        if isinstance(commands, list):
            for index, command in enumerate(commands):
                p = Popen(
                    "ssh -i /root/id_rsa_windows {0}@{1} {2}".format(
                        self.username, self.hosname, command
                    ),
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                    shell=True,
                )
                outt = outt + str(p.communicate())
                sleep(1)
            return outt
        p = Popen(
            "ssh -i id_rsa_windows {0}@{1} {2}".format(
                self.username, self.hosname, commands
            ),
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
        )
        out = p.communicate()
        return out
