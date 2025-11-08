from enum import StrEnum, IntEnum
from xdg import BaseDirectory
from himitsu.query import Query
import os
import socket

class HimitsuException(Exception):
    def __init__(self, error):
        self.error = error

class Status(StrEnum):
    HARD_LOCKED = "hard_locked"
    SOFT_LOCKED = "soft_locked"
    UNLOCKED = "unlocked"

class RememberType(IntEnum):
    SESSION = 1
    TIMEOUT = 2
    SKIP = 3
    REFUSE = 4

class RememberOption:
    def __init__(self, type, timeout: int = 0):
        self.type = type
        self.timeout = timeout

    @classmethod
    def session(self):
        return self(RememberType.SESSION)

    @classmethod
    def timeout(self, timeout):
        return self(RememberType.TIMEOUT, timeout)

    @classmethod
    def skip(self):
        return self(RememberType.SKIP)

    @classmethod
    def refuse(self):
        return self(RememberType.REFUSE)

    def __str__(self):
        if (self.type==RememberType.SESSION):
            return "session"
        elif (self.type==RememberType.TIMEOUT):
            return str(self.timeout)
        elif (self.type==RememberType.SKIP):
            return "skip"
        elif (self.type==RememberType.REFUSE):
            return "refuse"


class Client:
    def __init__(self, conn):
        self.conn = conn

    def query(self, query, strict=False, decrypt=False, remembers: list[RememberOption] = []) -> list[Query]:
        """Queries himitsu for entries. 'query' may be a himitsu.Query or string."""

        cmd = "query"
        if strict:
            cmd += " -s"
        if decrypt:
            cmd += " -d"

        cmd += self.__remembers_arg(remembers)
        cmd += " " + str(query)
        cmd += "\n"
        self.conn.sendall(cmd.encode())

        return self.__read_keys()

    def add(self, key: Query|str) -> list[Query]:
        """Adds a new key to the store."""

        cmd = "add " + str(key) + "\n"
        self.conn.sendall(cmd.encode())

        return self.__read_keys()

    def update(self, query: Query|str, changes: Query|str, strict=False) -> list[Query]:
        """Updates entries in the store that are matched by the 'query' with the
           values provided by 'changes'. Keys that have values in changes will
           be added to or update existing ones. Keys that don't have values will
           delete the matching keys.
        """

        cmd = "update"
        if strict:
            cmd += " -s"
        cmd += " " + str(query) + "\n"
        self.conn.sendall(cmd.encode())
        status = self.conn.recv(1024).decode('utf8')
        self.__check_error(status)
        if status != "update\n":
            raise HimitsuException("internal agent error")

        cmd = "set " + str(changes) + "\n"
        self.conn.sendall(cmd.encode())

        return self.__read_keys()

    def delete(self, key, strict=True) -> list[Query]:
        """Deletes a key."""

        cmd = "del"
        if strict:
            cmd += " -s"

        cmd += " " + str(key) + "\n"
        self.conn.sendall(cmd.encode())

        return self.__read_keys()

    def __read_keys(self) -> list[Query]:
        entries = []
        prev = ""
        end = False
        while not end:
            response = prev + self.conn.recv(4096).decode('utf8')

            self.__check_error(response)

            strentries = response.split("\n")
            if strentries[-1] == "":
                strentries = strentries[:-1]

            if not response.endswith("\n"):
                prev = strentries[-1]
                strentries = strentries[:-1]
            elif strentries[-1] == "end":
                end = True
                strentries = strentries[:-1]

            for strentry in strentries:
                if not strentry.startswith("key "):
                    raise Exception("invalid response")

                s = strentry[len("key "):]
                entries.append(Query(s))

        return entries

    def __remembers_arg(self, remembers: list[RememberOption]) -> str:
        s = ""
        if len(remembers):
            s += " -r "
            for r in remembers:
                s += str(r) + ","
            s = s[:-1]
        return s
    
    def __check_error(self, response):
        if response.startswith("error "):
            raise HimitsuException(response[len("error "):])


    def lock(self, soft=False) -> None:
        """Locks the himitsu daemon, which removes all values from memory
        
        If soft is provided, the daemon will keep public attributes.
        """

        cmd = "lock"
        if (soft):
            cmd += " -s"
        cmd += "\n"

        self.conn.sendall(cmd.encode())
        status = self.conn.recv(128).decode('utf8')

        self.__check_error(status)

        if status != "locked\n":
            raise Exception("invalid response")

    def status(self) -> Status:
        """Queries the status of the himitsu daemon"""

        self.conn.sendall(b"status\n")
        status = self.conn.recv(128).decode('utf8')

        self.__check_error(status)

        if len(status) == 0:
            raise Exception("connection closed")

        if not status.endswith("\n"):
            raise Exception("invalid response")

        parts = status.rstrip("\n").split()
        if len(parts) != 2 or parts[0] != "status":
            raise Exception("invalid response")

        try:
            return Status[parts[1].upper()]
        except KeyError:
            raise Exception("invalid response")

def connect() -> Client:
    """Connects to the himitsu socket and returns a client object"""

    socketpath = os.path.join(BaseDirectory.get_runtime_dir(), "himitsu")

    conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn.connect(socketpath)

    return Client(conn)


