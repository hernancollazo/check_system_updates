# check_system_updates
Simple Nagios plugin to check using YUM/apt for package updates.

### Installation

Since it's an active check, it's best used with NRPE. 

```sh
$ cd /tmp/
$ git clone [git-repo-url] check_system_updates
$ cd check_system_updates
$ cp check_system_updates.py /usr/lib/nagios/plugins/check_system_updates.py
```
And then, add to your NRPE config:

```sh
command[check_updates]=/usr/lib/nagios/plugins/check_system_updates.py
```
