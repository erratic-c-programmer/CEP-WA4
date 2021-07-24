#! /usr/bin/python3

import os
import hashlib
import random, string


def get_salt():
    return "".join(random.choices(string.ascii_letters + string.digits, k=128))


def hash_passwd(plain, salt):
    """
    Salt and hash input password. Length 128.
    """
    return hashlib.pbkdf2_hmac(
        "sha512", plain.encode(), salt.encode(), 100000, 64
    ).hex()  # ?!?!


def hash_uname(plain):
    """
    Hash username into hash digest of length 128
    """
    return hashlib.sha512(plain.encode()).hexdigest()


######


class userfile:  # why is this a class... gonna have to rewrite this someday
    def __init__(self, passwdfilename, shadowfilename):
        self.pwfname = passwdfilename
        self.sfname = shadowfilename

    def __enter__(self):
        return self

    def add_user(self, username, passwd):
        with open(self.pwfname, "a") as pwfile, open(self.sfname, "a") as sfile:
            salt = get_salt()
            # Write the username and
            # Fixed-length usernames of 128 characters
            pwfile.write(hash_uname(username))  # write hash
            pwfile.write(salt)  # write salt
            sfile.write(hash_passwd(passwd, salt))  # write hash
            return

    def del_user(self, username):
        # Sanity
        if len(username) == 0:
            return

        # Init values
        storedas = 1
        with open(self.pwfname, "r+") as pwfile, open(self.sfname, "r+") as sfile:
            # If it's the first
            cur_read = pwfile.read(128 + 128)
            cur_uname = cur_read[:128]

            t = hash_uname(username)  # don't leak position-- might be important?
            while cur_uname != t:
                storedas += 1
                if len(cur_read) == 0:
                    return  # that failed; don't exist
                cur_read = pwfile.read(128 + 128)
                cur_uname = cur_read[:128]

            pwfile.seek(0)
            x = pwfile.read()
            pwfile.seek(0)
            pwfile.write(
                x[: (storedas - 1) * (128 + 128)] + x[storedas * (128 + 128) :]
            )

            sfile.seek(0)
            x = sfile.read()
            sfile.seek(0)
            sfile.write(
                x[: (storedas - 1) * 128] + x[storedas * 128 :]
            )

    def check(self, username, passwd):
        # Sanity
        if len(username) * len(passwd) == 0:
            return False

        # Init values
        storedas = 1
        with open(self.pwfname, "r") as pwfile, open(self.sfname, "r") as sfile:
            # If it's the first
            cur_read = pwfile.read(128 + 128)
            cur_uname = cur_read[:128]
            cur_salt = cur_read[128:]

            t = hash_uname(username)
            while cur_uname != t:
                storedas += 1
                cur_read = pwfile.read(128 + 128)
                if len(cur_read) == 0:
                    hash_passwd("hohoho", "teehee")  # prevent timing attacks I guess?
                    return False
                cur_uname = cur_read[:128]
                cur_salt = cur_read[128:]

            hashed = hash_passwd(passwd, cur_salt)

            # Check against the true hash
            # I need to fix this someday
            # This is hella inefficient XD
            truehash = None
            for _ in range(storedas):
                truehash = sfile.read(128)

            return hashed == truehash
