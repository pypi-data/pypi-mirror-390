#!/usr/bin/env python3


import os
import platform
import yaml
import pathlib
from getpass import getpass
from packaging.version import Version
import datetime


from .utils import clear_terminal
from .pw import get_credentials, read_secrets, store_secrets
from .__version__ import __version__ as ao3SSversion


min_compatible_version = Version("0.3.2")


class PlottingConfig(object):
    """
    Configuration for the plotting script.
    """

    def __init__(self):
        self.prettify = True
        self.diff = False
        self.diff_delta = "weekly"
        return


class Config(object):
    username = "Your AO3 Username"
    password = "Don't type your password in plain text"

    store_login = None
    use_master_pw = None

    ao3dir = None
    datadir = None
    conffile = None
    pklfile = None
    timestamp = None

    plotting = None

    def __init__(self, reset_conffile=False):
        """
        Initialize configuration.
        If `reset_conffile` is True, then write a new config file from scratch
        and exit.
        """

        # Get config directory
        userdir = pathlib.Path.home()
        ao3dir = os.path.join(userdir, ".ao3statscraper")
        self.ao3dir = ao3dir

        # Make sure it exists.
        try:
            os.mkdir(ao3dir)
        except FileExistsError:
            pass

        self.plotting = PlottingConfig()

        # Set full paths for config files.
        conffilename = "ao3statscraper.conf.yml"
        conffile = os.path.join(ao3dir, conffilename)
        self.conffile = conffile
        pklfilename = "ao3statscraper.conf.pkl"
        pklfile = os.path.join(ao3dir, pklfilename)
        self.pklfile = pklfile

        if not os.path.exists(conffile):
            clear_terminal()
            input(
                "Didn't find a configuration file. We need to set one up. Press <Enter> to coninue.\n"
            )
            self.setup_config_file()
        else:
            if reset_conffile:
                self.setup_config_file()
                quit()

        # get contents of config file.
        self._read_config_file()

        # Make sure everything is set.
        self._check_config()

        return

    def _check_config(self):
        """
        Check that no attributes are None. Mainly intended as a dev tool to make
        sure everything's intialized properly.
        """

        d = self.__dir__()

        for key in d:
            if key.startswith("__"):
                continue
            if getattr(self, key) is None:
                raise ValueError(f"Attribute {key} not initialized.")
        return

    def set_credentials(self, username, password):
        """
        Store username and password.
        """

        self.username = username
        self.password = password

        return

    def setup_config_file(self):
        """
        Set up permanent configuration and dump them in the configure file.
        """

        t = datetime.datetime.now()
        self.timestamp = f"{t.year:04d}-{t.month:02d}-{t.day:02d}-{t.hour:02d}-{t.minute:02d}-{t.second:02d}"

        clear_terminal()
        print("Welcome to the configuration setup for the AO3 Stat Scraper.")
        print(
            f"After this setup, a configuration file will be written in `{self.conffile}`"
        )
        print("You can freely modify it on your own without calling this dialogue.")
        print(
            "Select a directory to store downloaded statistics. Hit <Enter> to use default."
        )
        datadir = input(f"(default: '{self.ao3dir}')\n")

        clear_terminal()
        print("Optionally, you can store your AO3 login on your local machine.")
        print("Your username and password will be encrypted and locked with a ")
        print("master password that you'll be asked to set next.")
        print("(If you forget the master password, you'll need to re-run this")
        print("configuration dialogue. You can do that by running `ao3get -c`.)")
        store_login_str = "b"
        a = 0
        while not store_login_str.startswith(("n", "N", "y", "Y")):
            if a > 0:
                print("Invalid input. Please select 'y' or 'n'.")
            store_login_str = input(
                "Do you want to store your AO3 login on your local machine? [y/n]\n"
            )
            a += 1
            if a > 10:
                print("Too many attempts. Exiting.")
                quit()

        store_login = True
        if store_login_str.startswith(("n", "N")):
            store_login = False

        # Get master password settings
        use_master = True
        master_pwd = self.timestamp

        if store_login:
            clear_terminal()

            print("You can store your AO3 login encrypted using a master password.")
            print("This is strongly recommended.")

            a = 0
            use_master_str = "b"
            while not use_master_str.startswith(("n", "N", "y", "Y")):
                if a > 0:
                    print("Invalid input. Please select 'y' or 'n'.")
                use_master_str = input(
                    "Do you want to set up a master password? [Y/n]\n"
                )
                a += 1
                if a > 10:
                    print("Too many attempts. Exiting.")
                    quit()

            if use_master_str.startswith(("n", "N")):
                use_master = False

            if use_master:
                # Get master password.

                rcount = 0
                retry = True

                while retry:
                    retry = False

                    clear_terminal()
                    if rcount > 0:
                        print("Error: Passwords do not match.")

                    print("Enter a master password (not your AO3 login password).")
                    master_pwd = getpass(
                        "(For security reasons, the letters won't be shown as you type.)\n"
                    )

                    clear_terminal()
                    master_pwd2 = getpass("Enter the password again:\n")

                    if master_pwd != master_pwd2:
                        rcount += 1
                        if rcount < 4:
                            retry = True
                        else:
                            print("Too many attempts. Aborting.")
                            quit()

            # Grab AO3 credentials.
            username, password = get_credentials()
            # And store them.
            self.set_credentials(username, password)
            store_secrets(master_pwd, username, password, self.pklfile)

        if datadir == "":
            datadir = self.ao3dir

        try:
            os.mkdir(datadir)
        except FileExistsError:
            pass

        # Store the config
        self.datadir = datadir
        self.store_login = store_login
        self.use_master_pw = use_master

        # Now write the config file.
        confdict = {}
        global_conf = {
            "config_time": self.timestamp,
            "data_directory": self.datadir,
            "extended_output": self.use_master_pw,
            "version": ao3SSversion,
        }

        confdict = {
            "Globals": global_conf,
        }

        ymlfp = open(self.conffile, "w")
        yaml.dump(confdict, ymlfp)
        ymlfp.close()

        print("Configuration complete.")

        return

    def _read_config_file(self):
        """
        Read in contents of the config file.
        """
        ymlfp = open(self.conffile, "r")
        confdata = yaml.load(ymlfp, Loader=yaml.Loader)
        ymlfp.close()

        refresh_config = False
        # Catch versions too old to even keep track of config version
        try:
            version = confdata["Globals"]["version"]
        except KeyError:
            refresh_config = True

        if Version(ao3SSversion) < min_compatible_version:
            refresh_config = True

        if refresh_config:
            print(
                "ERROR: Your config file is set up for an older version of AO3StatScraper."
            )
            print("Please re-configure it using `ao3get -c`")
            quit(1)

        try:
            self.datadir = confdata["Globals"]["data_directory"]
            self.timestamp = confdata["Globals"]["config_time"]
            self.use_master_pw = confdata["Globals"]["extended_output"]
        except KeyError:
            print("ERROR: Some fields are missing from your config file.")
            print("It might be out of date.")
            print("Re-configure it using `ao3get -c`")
            quit(1)

        # if login file exists, login is stored.
        self.store_login = os.path.exists(self.pklfile)

        return

    def prep_scrape(self):
        """
        Ensure everything is set for a scrape.
        """

        if self.store_login:
            master_pwd = self.timestamp
            if self.use_master_pw:
                master_pwd = getpass(
                    "Enter master password (not your AO3 login password):\n"
                )
            username, password = read_secrets(master_pwd, self.pklfile, retry=True)
        else:
            username, password = get_credentials()

        self.set_credentials(username, password)

        return
