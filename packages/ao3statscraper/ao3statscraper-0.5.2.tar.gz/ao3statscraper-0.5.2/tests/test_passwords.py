#!/usr/bin/env python3

from ao3statscraper import store_secrets, read_secrets

passwords = [
    "abc",
    "alksdhasdnaonaosdfhalkshfalhfaouhfaf ha aofh a\j809& ",
    "abcdefghijklmnopqwertuvwxyzABCDEFGHIJKLMNOPQWERTUVWXYZ0123456789 !\"£$%^&*()_+{}:@~<>?-=[];'#.,/\s\t\r\n"
    "",
]

i = 0
for p1 in passwords:
    if p1 != "":
        master = "master_" + p1
    else:
        master = p1

    for p2 in passwords:
        if p2 != "":
            user = "user_" + p2
        else:
            user = p2

        for p3 in passwords:
            if p3 != "":
                pwd = "pwd_" + p3
            else:
                pwd = p3

            i += 1

            filename = "testPasswords" + str(i) + ".pkl"

            store_secrets(master, user, pwd, filename)
            u_restored, p_restored = read_secrets(master, filename, retry=False)

            assert user == u_restored
            assert pwd == p_restored
