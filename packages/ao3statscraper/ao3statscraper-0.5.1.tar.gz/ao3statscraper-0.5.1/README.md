# AO3StatScraper

`AO3StatScraper` is a small python package that provides command line scripts to
fetch your AO3 (*Archive Of Our Own*) statistics to store and display them. See
the [Examples section](#examples) for some screenshots of what it can do for
you.

## Installation

`AO3StatScraper` is available on
[PyPI](https://pypi.org/project/ao3statscraper/), and can obtained any regular
way you'd install a python package, e.g. using `pip`, `conda`, etc.

For example, using `pip`:

**On Linux/OSX**:

- First, open a terminal/the "Terminal" app. It will wait for you to type in a
command and hit `Enter` to execute it.
- Type in the following command and execute it by hitting `Enter`:
```
python3 -m pip install ao3statscraper
```
- That's it, you've installed `ao3statscraper`!


**On Windows**:

- make sure you [install Python](https://www.python.org/downloads/windows/) first.
- open the `command prompt`. It will wait for you to type in a command and hit
  `Enter` to execute it. (PowerShell works too, but you'll need to [enable
  execution of scripts](https://stackoverflow.com/questions/64633727/how-to-fix-running-scripts-is-disabled-on-this-system).)
- Type in the following command:
```
py -m pip install ao3statscraper
```
- That's it, you've installed `ao3statscraper`!


Alternately, the source code is available on
[gitlab](https://gitlab.com/athenaslilowl1/AO3StatScraper).
You can install a local version by cloning the repository using git.
On OSX and Linux, you can use (again in the terminal)

```
git clone https://gitlab.com/athenaslilowl1/AO3StatScraper.git    # get the git repository
cd AO3StatScraper                                                 # go into the directory
python3 -m pip install .                                          # install package
```


On Windows (make sure you [install Python](https://www.python.org/downloads/windows/) and
[git](https://git-scm.com/downloads) first), the equivalent steps in the
`command prompt` are:

```
git clone https://gitlab.com/athenaslilowl1/AO3StatScraper.git
cd AO3StatScraper
py -m pip install .
```







## User Guide

The commands listed below can be executed by typing them into a terminal
(Linux), the Terminal app (OSX), or the `command prompt` (Windows) and hitting
`Enter` after you've installed them following the steps above.


### TL;DR

- Run the `ao3get` command to display the differences to the last time you stored
your stats with AO3StatScraper.
- When running for the very first time, use `ao3get --all` instead.
- Run `ao3plot` to plot the results.



### Overview: How It Works

`AO3StatScraper` simply downloads your AO3 stats page (pretty much the same as
opening it in your browser and hitting `Save this page...`) and then extract the
stats from that html content. To be able to access your stats, you need to log
in to AO3, which is why `AO3StatScraper` will ask you for your username and
password.


By default `AO3StatScraper` (i.e. the script `ao3get`) will store your current
stats as a snapshot. This includes both your total user statistics as well as
your individual work statistics. The data is written in
the csv (Comma Separated Values) format, so plenty of other software and
packages should be able to read it in easily. Your total user statistics are
stored in a separate file from your work statistics.



### Getting Started

The main use case for `AO3StatScraper` is to fetch and display your current AO3
statistics using scripts provided by `AO3StatScraper`. Currently, there are 5
scripts:

- `ao3get` : The main script to fetch and display your AO3 stats.
- `ao3plot`: Plots the stats stored with `ao3get`.
- `ao3diff`: Show the difference in stats compared to an earlier date.
- `ao3_hits_to_kudos`: List all your works in ascending order of their
  hits/kudos ratio
- `ao3_purge`: Deletes saved stats such that there is a minimum time between the
  remaining ones

The scripts are discussed in more detail further below.


**IMPORTANT**: Before you can run the other scripts, you first need to configure
`AO3StatScraper`. This is done by calling `ao3get`. It will launch the
configuration dialogue automatically if it hasn't been configured yet. You can
always re-configure it by invoking `ao3get -c`.

**IMPORTANT**: By default, `ao3get` will try and display the difference in your
stats. This can't be done if there are no previous stats stored. For that reason,
the very first time you call `ao3get`, use `ao3get --all` instead.





### `ao3get`

This is the main script to fetch and store your AO3 stats. There are several
running modes. When in doubt, invoke `ao3get --help` to see the available
options.

The default running mode is `--diff`.

- `--all`: Fetch and store current stats from AO3 into a snapshot, and display
  stats for all works.
- `--repeat`: Don't fetch new stats, but show the changes between the last two
  stored stats snapshots.
- `--diff`: Fetch and store current stats from AO3 into a snapshot, and display
  only stats for works that have changed since the last snapshot. If there were
  no changes in work stats, it will display only the user's total stats.
- `--config`: Run the configuration dialogue and exit.
- `--remove-last`: Deletes the last snapshot `ao3get` stored and exits. May come
  in handy if you're nervously re-downloading your stats every minute.
- `--no-write`: This flag modifies the behaviour for `--all` and `--diff`
  running modes. While current stats are fetched from AO3, they won't be written
  into a snapshot.
- `--file`: Instead of using the `ao3get` mechanism to log in to AO3 and
  download your current stats, read them in from a file. This can be handy when
  AO3 ups their defenses and prevents `ao3get` to log in, which may happen on
  occasion. This option allows you to manually save your stats page (simply
  open your AO3 stats page in a browser and use `ctrl`/`cmd` + s in your
  browser and save the page wherever) and read that file in with `ao3get` by
  providing the path to wherever it was you saved it.

The list above does not cover all the available options. Please use
`ao3get --help` to see all the available options.

Using `ao3get` requires you to log in to your AO3 account. You can either type
in your username and password each time you invoke it, or you can store it with
`AO3StatScraper`, locked behind a master password. There are no restrictions on
how sophisticated your master password needs to be, so if you can't be
inconvenienced, you can even leave it empty. Alternately, you can opt out of
using a master password at all, although this is not encouraged. But it would
allow you to e.g. set up an automated way to fetch your stats at regular times.


### `ao3plot`

`ao3plot` will display some simple graphs based on the stored snapshots. It
never stores snapshots itself, you will need to do that using `ao3get`.

By default, `ao3plot` will ask you to select which work you would like to see
graphs of stats for. You can also select to plot your total user statistics.

Alternately, you can skip that dialogue by using the following flags:

- `-u`: Show total user statistics.
- `-i <ID>`: Show the statistics for the work with AO3 ID `<ID>`. For example,
  if your work is under the link `https://archiveofourown.org/works/24280306`,
  the `<ID>` would be `24280306`.
- `<number>`: Show the statistics for the work with index `<number>`, where the
  index refers to the number of the work as shown in the selection dialogue
  when running `ao3plot` without any command line arguments.
  You can also provide a list of indices as a comma separated list of integers,
  e.g. `ao3plot 3,4,5` to plot indices 3, 4, and 5 in the same plot.

It is possible that the stats graphs aren't displayed nicely on all screens. If
that is the case for you, you may want to try the `--no-prettify` flag to obtain
a bare-bones plot without any prettifications. It may not look as nice, but at
least you should be able to see the data.

Finally, you can also try the `--diff` option to additionally display the
*difference* in stats over time in the plot as opposed to their actual value. By
default, it shows the weekly differences between the stats.



### `ao3diff`

Fetch (but do not store) your AO3 stats and compare them to stats from the past.
It never stores snapshots itself, you will need to do that using `ao3get`.
By default, it will compare to your stats from a week ago, but you can also
select a day, a week, a month, or a year back using the `-d`, `-w`, `-m`, or `-y`
flag, respectively. Alternately, you can specify a date in the `YYYY-MM-DD`
format.



### `ao3_hits_to_kudos`

This script just reads in the last stored snapshot and prints out all your works
in ascending order of their hits/kudos ratio.



### `ao3_purge`

In case you find yourself in a situation where you feel you have stored way too
many snapshots, `ao3_purge` offers you the option to delete stats snapshots such
that there is some minimal time between them. By default, this frequency is set
to 12h. You can provide the frequency you like using the `--frequency` flag.




## Examples

This is example output what `ao3get` will show you when you run it:

![default running mode, diff](webdata/ao3get-diff.png)

It will only list the works that have changes since you last checked (i.e. stored
a snapshot).

But you can also view all your works:

![show all works](webdata/ao3get-all.png)


Plotting the total user statistics with `ao3plot` will show you something like
this:

![plotting user stats](webdata/plot-user.png)


Running `ao3plot` for a specific work will give you 2 plots:

![plotting work, Figure 1](webdata/plot-work1.png)
![plotting work, Figure 2](webdata/plot-work2.png)





# Having issues?

Please let me know by raising an issue on
[gitlab](https://gitlab.com/athenaslilowl1/AO3StatScraper/-/issues) or reach out
to me on bluesky: [@athenaslilowl](https://bsky.app/profile/athenaslilowl.bsky.social).

I'm using Linux exclusively, so there may be issues on other operating systems.
Testers and devs on OSX and windows are also very welcome to let me know what's
working and what needs fixing.


## Troubleshooting on Windows


### `ImportError: DLL load failed while importing _cext: The specified module could not be found.`


```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Users\USER\testVenv\Lib\site-packages\matplotlib\__init__.py", line 263, in <module>
    _check_versions()
  File "C:\Users\USER\testVenv\Lib\site-packages\matplotlib\__init__.py", line 257, in _check_versions
    module = importlib.import_module(modname)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\USER\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\USER\testVenv\Lib\site-packages\kiwisolver\__init__.py", line 8, in <module>
    from ._cext import (
ImportError: DLL load failed while importing _cext: The specified module could not be found.
```


The error appears to be related to the matplotlib installation. Try installing
`msvc-runtime` **system wide, i.e. outside of a virtual environment**:


```
py -m pip install msvc-runtime
```





# Roadmap and Contributing

Help and contributions to maintain and extend this tool are very welcome!

Some ideas what might be added in the future include
- Writing/reading of file formats other than csv.
- Maybe add a GUI for CLI-averse users. This tool was always intended to be a
  command line tool on my end. Having never programmed a GUI in my life, I don't
  intend to start now. However, if anybody is willing to pack this up in a nice
  simple portable GUI, you are very welcome and encouraged to do so! I'll gladly
  add it to the repository.

I'm using Linux exclusively, so there may be issues on other operating systems.
Testers and devs on OSX and windows are also very welcome to let me know what's
working and what needs fixing.



# Acknowledgements

Parts of the AO3 fetching mechanism is lifted from the [AO3 API
package](https://github.com/ArmindoFlores/ao3_api).

