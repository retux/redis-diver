**usage**: redis-diver.py Explores redis and looks for entries older than a given threshold (-o | --older-than).  


**WARNING**: if -d | --delete-entries flag is provided, -o | --older-than must be provided too.


```bash
-i            | --help                        Show this message.
-o <time>     | --older-than <time>           List entries with idle time greater than <time> (in seconds or Nd e.g 15d).
-d            | --delete-entries              Deletes entries with idletime (Requires -o <time>)
-h <hostname> | --hostname <hostname>
-p <port>     | --port <port>
-k <keyspace> | --keyspace <keyspace>         Specifies keyspace name.
-l            | --list-keyspaces              List existing keyspaces. 
-s            | --dump-keys                   Only show (stdout) or dump keys.
-n            | --no-ttl                      Together with -s or --dump-keys displays only the keys that don't expire
```                                           (TTL = -1).


**Examples**:

```bash
$ redis-diver.py --older-than 2592000 --delete-entries
```

Will delete entries with idletime >= 2592000 and TTL is not set (-1).

```bash
$ redis-diver.py --older-than 15d --delete-entries
```

Will delete entries with idletime >= 15 days and TTL is not set (-1).

```bash
$ redis-diver.py --dump-keys
```

Will dump all keys


Important: bear in mind when -d | --delete-entries flag is set, entries will only be deleted if no expire time had been
set ttl(key) == -1.

This script is provided as it is. Don't try to blame @retux if you have screwed up your cache.
