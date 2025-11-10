#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from typing import Union
import os
import datetime

from .statsdata import WorkStatsData, TotStatsData
from .configuration import Config
from .ao3requester import requester


def _clean_fieldname(field: str, titularise=False):
    """
    Trim, strip, replace underscores with spaces.
    If titularise is True, capitalize all words.
    """

    s = field.strip()
    s = s.replace("_", " ")
    if titularise:
        s = s.title()

    return s


def _get_work_stats(soup: BeautifulSoup, conf: Config):
    """
    Extract the work stats from the BeautifulSoup container of the
    AO3 user stats page.

    returns
    -------

    new_workstats: WorkStatsData
        A WorkStatsData object containing the data from the BeautifulSoup
    """

    worklist = []

    # Loop over all fandoms
    for flig in soup.find_all("li", {"class": "fandom listbox group"}):
        fandom = _clean_fieldname(flig.h5.text)

        #  print(fandom)

        for work in flig.find_all("li"):
            workdata = {}

            work_link = work.a["href"]
            work_number = work_link.lstrip("'https://archiveofourown.org/works/")
            work_name = work.a.text

            words_text = work.find("span", {"class": "words"})
            words = words_text.text.lstrip("(").rstrip("words )")
            words = words.replace(",", "")

            if not work_number.isnumeric():
                raise ValueError(f"Error with work number: {work_number}")
            if work_name is None or work_name == "":
                raise ValueError(f"Error with work name: {work_name}")
            if not words.isnumeric():
                raise ValueError(f"Error with word number: {words}")

            workdata["ID"] = work_number
            workdata["Title"] = work_name
            workdata["Words"] = words
            workdata["Fandom"] = fandom
            workdata["Hits"] = 0
            workdata["Kudos"] = 0
            workdata["Comment Threads"] = 0
            workdata["Bookmarks"] = 0
            workdata["Subscriptions"] = 0

            for field in work.findAll("dt"):
                if field.span is not None:
                    # skip Work title.
                    continue
                fieldname = field.getText()[:-1]
                dataname = _clean_fieldname(fieldname, titularise=True)
                if (
                    field.next_sibling is not None
                    and field.next_sibling.next_sibling is not None
                ):
                    value = field.next_sibling.next_sibling.getText().replace(",", "")
                    if value.isdigit():
                        workdata[dataname] = int(value)

            worklist.append(workdata)

    new_workstats = WorkStatsData(conf, worklist)

    return new_workstats


def _get_total_stats(soup: BeautifulSoup, conf: Config):
    """
    Extract the total stats from the BeautifulSoup container of the
    AO3 user stats page.

    returns
    -------

    new_totstats: TotStatsData
        A TotStatsData object containing the data from the BeautifulSoup
    """

    total_stats = {}

    dt = soup.find("dl", {"class": "statistics meta group"})
    if dt is not None:
        for field in dt.findAll("dt"):
            name = field.getText()[:-1].lower().replace(" ", "_")
            name = _clean_fieldname(name, titularise=True)
            if (
                field.next_sibling is not None
                and field.next_sibling.next_sibling is not None
            ):
                value = field.next_sibling.next_sibling.getText().replace(",", "")
                if value.isdigit():
                    total_stats[name] = [int(value)]

    new_totstats = TotStatsData(conf, total_stats)

    return new_totstats


class UserSession:
    """
    Mostly lifted from https://github.com/ArmindoFlores/ao3_api

    If file is provided, read from file instead of logging in and downloading.
    File should be a saved stats page.
    """

    def __init__(self, conf: Config, file: Union[str, None] = None):
        self.file = file
        conf.prep_scrape()
        self.username = conf.username

        if file is not None:
            # we don't need anything else.
            return

        self.is_authed = True
        self.authenticity_token = None
        self.session = requests.Session()

        self.url = f"https://archiveofourown.org/users/{self.username}"

        soup = self.request("https://archiveofourown.org/users/login")

        token = soup.find("input", {"name": "authenticity_token"})

        if token is None:
            raise ValueError(
                "Something went wrong when connecting to AO3. Try again later."
            )

        self.authenticity_token = token["value"]

        payload = {
            "user[login]": conf.username,
            "user[password]": conf.password,
            "authenticity_token": self.authenticity_token,
        }

        post = self.post(
            "https://archiveofourown.org/users/login",
            params=payload,
            allow_redirects=False,
        )

        if not post.status_code == 302:
            raise ValueError("LoginError: Invalid username or password")

        return

    def __getstate__(self):
        d = {}
        for attr in self.__dict__:
            if isinstance(self.__dict__[attr], BeautifulSoup):
                d[attr] = (self.__dict__[attr].encode(), True)
            else:
                d[attr] = (self.__dict__[attr], False)
        return d

    def __setstate__(self, d):
        for attr in d:
            value, issoup = d[attr]
            if issoup:
                self.__dict__[attr] = BeautifulSoup(value, "lxml")
            else:
                self.__dict__[attr] = value

    def refresh_auth_token(self):
        """Refreshes the authenticity token.
        This function is threadable.

            # TODO: this shouldn't work. I don't have HTTPErrors.
        Raises:
            utils.UnexpectedResponseError: Couldn't refresh the token
        """

        # For some reason, the auth token in the root path only works if you're
        # unauthenticated. To get around that, we check if this is an authed
        # session and, if so, get the token from the profile page.

        if self.is_authed:
            req = self.session.get(f"https://archiveofourown.org/users/{self.username}")
        else:
            req = self.session.get("https://archiveofourown.org")

        if req.status_code == 429:
            # TODO: this shouldn't work. I don't have HTTPErrors.
            raise utils.HTTPError(
                "We are being rate-limited. Try again in a while or reduce the number of requests"
            )

        soup = BeautifulSoup(req.content, "lxml")
        token = soup.find("input", {"name": "authenticity_token"})
        if token is None:
            # TODO: this shouldn't work. I don't have HTTPErrors.
            raise utils.UnexpectedResponseError("Couldn't refresh token")
        self.authenticity_token = token.attrs["value"]

    def get(self, *args, **kwargs):
        """Request a web page and return a Response object"""

        if self.session is None:
            req = requester.request("get", *args, **kwargs)
        else:
            req = requester.request("get", *args, **kwargs, session=self.session)
        if req.status_code == 429:
            # TODO: this shouldn't work. I don't have HTTPErrors.
            raise utils.HTTPError(
                "We are being rate-limited. Try again in a while or reduce the number of requests"
            )
        return req

    def request(self, url):
        """Request a web page and return a BeautifulSoup object.

        Args:
            url (str): Url to request

        Returns:
            bs4.BeautifulSoup: BeautifulSoup object representing the requested page's html
        """

        req = self.get(url)
        soup = BeautifulSoup(req.content, "lxml")
        return soup

    def read_htmlfile(self):
        """
        Read a stored web page and return a BeautifulSoup object.

        Returns:
            bs4.BeautifulSoup: BeautifulSoup object representing the requested page's html
        """

        fp = open(self.file, "r")
        soup = BeautifulSoup(fp, "lxml")
        return soup

    def post(self, *args, **kwargs):
        """Make a post request with the current session

        Returns:
            requests.Request
        """

        req = self.session.post(*args, **kwargs)
        if req.status_code == 429:
            # TODO: this shouldn't work. I don't have HTTPErrors.
            raise utils.HTTPError(
                "We are being rate-limited. Try again in a while or reduce the number of requests"
            )
        return req

    def __del__(self):
        if self.file is None:
            self.session.close()

    def get_stats(self, conf: Config):
        """
        Fetch the actual data.
        """

        if self.file is not None:
            soup = self.read_htmlfile()
        else:
            stats_url = f"https://archiveofourown.org/users/{conf.username}/stats"
            soup = self.request(stats_url)

        errors = soup.find_all(attrs={"class": "flash error"})

        # List is empty if div with flash error is not found
        for e in errors:
            etext = e.get_text()
            if (
                etext
                == "Sorry, you don't have permission to access the page you were trying to reach. Please log in."
            ):
                print("Error logging in. Try again. Did you mistype your AO3 password?")
                quit()

        if len(errors) > 0:
            print("Caught some errors which aren't handled. Output is:")
            print(errors)
            quit()

        total_stats = _get_total_stats(soup, conf)
        work_stats = _get_work_stats(soup, conf)

        if self.file is not None:
            # overwrite time stamp to time stamp of downloaded file
            # creation time
            ctime = os.path.getctime(self.file)
            # modification time in case the system doesn't store overwrites as new files
            mtime = os.path.getmtime(self.file)
            time = max(ctime, mtime)
            timestamp = datetime.datetime.fromtimestamp(time)

            total_stats.timestamp = timestamp
            work_stats.timestamp = timestamp

        return total_stats, work_stats
