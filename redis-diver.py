import redis
import getopt
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisDiver:
    host = 'localhost'
    port = 6379
    older_than = None
    delete_entries = False
    dump_keys = True
    no_ttl = False
    list_keyspaces = False
    keyspace = 0


    def __init__(self, config_options):
        if not config_options:
            usage()
        if config_options.has_key('port'):
            self.port = config_options['port']
        if config_options.has_key('host'):
            self.host = config_options['host']
        if config_options.has_key('older'):
            try:
                if 'd' in config_options['older']:
                    config_options['older'] = config_options['older'].replace('d','')
                    config_options['older'] = int(config_options['older']) * 86400
                self.older_than = int(config_options['older'])
            except ValueError:
                logger.error("-o <value> must be an integer.")
                sys.exit(1)
        if config_options.has_key('delete'):
            self.delete_entries = True
        if config_options.has_key('dump'):
            self.dump_keys = True
        if config_options.has_key('nottl'):
            self.no_ttl = True
        if config_options.has_key('list-keyspaces'):
            self.list_keyspaces = True
        if config_options.has_key('keyspace'):
            try:
                self.keyspace = int(config_options['keyspace'])
            except ValueError:
                logger.error("-k <value> must be an integer to identify keyspace number.")
                sys.exit(1)
        logger.debug("config_options={0}".format(config_options))
        if self.delete_entries and not self.older_than:
            logging.error("-d | --delete-entries requires -o | --older-than flag. Stopping.")
            sys.exit(1)
        self.__getConnected()
        if not self.list_keyspaces:
            self.__getKeys()
        else:
            self.__list_keyspaces()


    def __getConnected(self):
        self.r = redis.StrictRedis(self.host, self.port, db=self.keyspace)


    def __list_keyspaces(self):
        for k, v in self.r.info(section='Keyspace').items():
            print ("keyspace {0}: keys: {1}, expires: {2}, avg_ttl: {3}".format(k, v['keys'], v['expires'], v['avg_ttl']))


    def __getKeys(self):
        sys.stderr.write("key : idletime : ttl \n")
        sys.stderr.flush()
        for key in self.r.scan_iter(match='*'):
            if self.older_than:
                if self.r.object('idletime', key) >= self.older_than:
                    if self.no_ttl:
                        if self.r.ttl(key) == -1:
                            if not self.delete_entries:
                                print("{0} : {1} : {2}".format(key,self.r.object('idletime', key), self.r.ttl(key)))
                    else:
                        if not self.delete_entries:
                            print("{0} : {1} : {2}".format(key,self.r.object('idletime', key), self.r.ttl(key)))
                    if self.delete_entries:
                        if self.r.ttl(key) == -1:
                            self.r.delete(key)
                            logger.info("{0} was deleted.".format(key))
            else:
                if self.no_ttl:
                    if self.r.ttl(key) == -1:
                        print("{0} : {1} : {2}".format(key,self.r.object('idletime', key), '-1'))
                else:
                    print("{0} : {1} : {2}".format(key,self.r.object('idletime', key), self.r.ttl(key)))



def main():
    my_redis = RedisDiver(parse_command_line())


def parse_command_line():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ih:p:o:dsnk:l", ["help", "host=", "port=", "older-than=", "delete-entries", \
                                                                "dump-keys", "no-ttl", "keyspace=", "list-keyspaces"])
    except getopt.GetoptError as err:
        logging.error (str(err))
        usage()
    opts_results = {}
    for o, a in opts:
        if o in ("-i", "--help"):
            usage()
        elif o in ("-o", "--older-than"):
            opts_results['older'] = a
        elif o in ("-d", "--delete-entries"):
            opts_results['delete'] = True
        elif o in ("-h", "--host"):
            opts_results['host'] = a
        elif o in ("-p", "--port"):
            opts_results['port'] = a
        elif o in ("-k", "--keyspace"):
            opts_results['keyspace'] = a
        elif o in ("-s", "--dump-keys"):
            opts_results['dump'] = True
        elif o in ("-n", "--no-ttl"):
            opts_results['nottl'] = True
        elif o in ("-l", "--list-keyspaces"):
            opts_results['list-keyspaces'] = True
        else:
            assert False, "unhandled option"
    return opts_results


def usage():
    usage_text="""    
usage: redis-diver.py Explores redis and looks for entries older than a given threshold (-o | --older-than).  


WARNING: if -d | --delete-entries flag is provided, 

-i            | --help                        Show this message.
-o <time>     | --older-than <time>           List entries with idle time greater than <time> (in seconds or days. E.g.: 3d).
-d            | --delete-entries              Deletes entries with idletime (Requires -o <time>)
-h <hostname> | --hostname <hostname>
-p <port>     | --port <port>
-k <keyspace> | --keyspace <keyspace>         Specifies keyspace name.
-l            | --list-keyspaces              List existing keyspaces. 
-s            | --dump-keys                   Only show (stdout) or dump keys.
-n            | --no-ttl                      Together with -s or --dump-keys displays only the keys that don't expire
                                              (TTL = -1).


Examples:

$ redis-diver.py --older-than 2592000 --delete-entries

Will delete entries with idletime >= 2592000 and TTL is not set (-1).

$ redis-diver.py --older-than 15d --delete-entries
Will delete entries with idletime >= 15 days and TTL is not set (-1).

$ redis-diver.py --dump-keys

Will dump all keys.


Important: bear in mind when -d | --delete-entries flag is set, entries will only be deleted if no expire time had been
set ttl(key) == -1.

This script is provided as it is. Don't try to blame @retux if you have screwed up your cache.
"""
    print(usage_text)
    sys.exit(1)



if __name__ == "__main__":
    main()
