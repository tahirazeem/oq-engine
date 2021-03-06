# Upgrading the OpenQuake Engine on RedHat Linux 7 and its clones

To upgrade the OpenQuake Engine and its libraries run

```bash
sudo yum upgrade python-oq-*
```

### Coming from release 1.0

The following dependencies are not used anymore by the OpenQuake Engine 2.0:
- postgresql-server and postgis
- other minor dependencies

They can be removed, if not used by any other software installed on your machine, by running

```
sudo yum erase --remove-leaves postgresql-server postgis python-psycopg2
```

To be able to use the `--remove-leaves` feature you need a `yum` plugin called `yum-plugin-remove-with-leaves`. If it's unavailable on your system, it can be installed via `yum`

```
sudo yum install yum-plugin-remove-with-leaves
```

## Getting help
If you need help or have questions/comments/feedback for us, you can:
  * Subscribe to the OpenQuake users mailing list: https://groups.google.com/forum/?fromgroups#!forum/openquake-users
  * Contact us on IRC: irc.freenode.net, channel #openquake
