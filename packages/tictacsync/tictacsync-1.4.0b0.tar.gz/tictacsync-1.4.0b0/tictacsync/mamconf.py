import argparse, platformdirs, configparser, sys
from loguru import logger
from pprint import pformat
from pathlib import Path
from rich import print

# [TODO] add in the doc:
# RAWROOT (sources with TC): "/Users/foobar/movies/MyBigMovie/"
# SYNCEDROOT (where RAWROOT will be mirrored, but with synced clips): "/Users/foobar/synced"
# SNDROOT (destination of ISOs sound files): "/Users/foobar/MovieSounds"
# then
# "/Users/foobar/synced/MyBigMovie" and "/Users/foobar/MovieSounds/MyBigMovie" will be created


CONF_FILE = 'mamsync.cfg'
LOG_FILE = 'mamdone.txt'

logger.remove()
# logger.add(sys.stdout, level="DEBUG")
# logger.add(sys.stdout, filter=lambda r: r["function"] == "write_conf")


def print_out_conf(raw_root, synced_root, snd_root, proxies=''):
    print(f'RAWROOT (sources with TC): "{raw_root}"')
    print(f'SYNCEDROOT (where RAWROOT will be mirrored, but with synced clips): "{synced_root}"')
    print(f'SNDROOT (destination of ISOs sound files): "{snd_root}"')
    if proxies != '':
        print(f'PROXIES (NLE proxy clips folder): "{proxies}"')

def write_conf(conf_key, conf_val):
    # args are pahtlib.Paths.
    # RAWROOT: files with TC (and ROLL folders), as is from cameras
    # SYNCEDROOT: synced and no more TC (ROLL flattened)
    # Writes configuration on filesystem for later retrieval
    # Clears log of already synced clips.
    conf_dir = platformdirs.user_config_dir('mamsync', 'plutz', ensure_exists=True)
    current_values = dict(zip(['RAWROOT', 'SYNCEDROOT', 'SNDROOT', 'PROXIES'],
                        get_proj()))
    logger.debug(f'old values {current_values}')
    current_values[conf_key] = conf_val
    logger.debug(f'updated values {current_values}')
    conf_file = Path(conf_dir)/CONF_FILE
    logger.debug('writing config in %s'%conf_file)
    # print(f'\nWriting folders paths in configuration file "{conf_file}"')
    # print_out_conf(raw_root, synced_root, snd_root)
    conf_prs = configparser.ConfigParser()
    conf_prs['SECTION1'] = current_values
    with open(conf_file, 'w') as configfile_handle:
        conf_prs.write(configfile_handle)
    with open(conf_file, 'r') as configfile_handle:
        logger.debug(f'config file content: \n{configfile_handle.read()}')

def get_proj(print_conf_stdout=False):
    # check if user started a project before.
    # stored in platformdirs.user_config_dir
    # returns a tuple of strings (RAWROOT, SYNCEDROOTS, SNDROOT, PROXIES)
    # if any, or a tuple of 4 empty strings '' otherwise.
    # print location of conf file if print_conf_stdout
    # Note: only raw_root contains the name project
    conf_dir = platformdirs.user_config_dir('mamsync', 'plutz')
    conf_file = Path(conf_dir)/CONF_FILE
    logger.debug('try reading config in %s'%conf_file)
    if print_conf_stdout:
        print(f'Will read configuration from file {conf_file}')
    if conf_file.exists():
        conf_prs = configparser.ConfigParser()
        conf_prs.read(conf_file)
        try:
            RAWROOT = conf_prs.get('SECTION1', 'RAWROOT')
        except configparser.NoOptionError:
            RAWROOT = ''
        try:
            SYNCEDROOT = conf_prs.get('SECTION1', 'SYNCEDROOT')
        except configparser.NoOptionError:
            SYNCEDROOT = ''
        try:
            PROXIES = conf_prs.get('SECTION1', 'PROXIES')
        except configparser.NoOptionError:
            PROXIES = ''
        try:
            SNDROOT = conf_prs.get('SECTION1', 'SNDROOT')
        except configparser.NoOptionError:
            SNDROOT = ''
        logger.debug('read from conf: RAWROOT= %s SYNCEDROOT= %s SNDROOT=%s PROXIES=%s'%
                                    (RAWROOT, SYNCEDROOT, SNDROOT, PROXIES))
        return RAWROOT, SYNCEDROOT, SNDROOT, PROXIES
    else:
        logger.debug(f'no config file found at {conf_file}')
        print('No configuration found.')
        return '', '', '', ''

def new_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rr',
                        nargs = 1,
                        dest='rawroot',
                        help='Sets new value for raw root folder (i.e.: clips with TC)')
    parser.add_argument('--sr',
                        nargs = 1,
                        dest='syncedroot',
                        help="""Sets where the synced files will be written, to be used by the NLE. Will contain a mirror copy of RAWROOT """)
    parser.add_argument('--pr',
                        nargs = 1,
                        dest='proxies',
                        help='Sets where the proxy files are stored by the NLE')
    parser.add_argument('--sf',
                        nargs = 1,
                        dest='sndfolder',
                        help='Sets value for sound folder (will contain a mirror copy of RAWROOT, but with ISO files only)')
    parser.add_argument('--clearconf',
                    action='store_true',
                    dest='clearconf',
                    help='Clear configured values.')
    parser.add_argument('--showconf',
                    action='store_true',
                    dest='showconf',
                    help='Show current configured values.')
    return parser

def main():
    parser = new_parser()
    args = parser.parse_args()
    logger.debug(f'arguments from argparse {args}')
    if args.rawroot:
        val = args.rawroot[0]
        write_conf('RAWROOT', val)
        print(f'Set source folder of unsynced clips (rawroot) to:\n{val}')
        sys.exit(0)
    if args.syncedroot:
        val = args.syncedroot[0]
        write_conf('SYNCEDROOT', args.syncedroot[0])
        print(f'Set destination folder of synced clips (syncedroot) to:\n{val}')
        sys.exit(0)
    if args.proxies:
        val = args.proxies[0]
        write_conf('PROXIES', args.proxies[0])
        print(f'Set proxies folder to:\n{val}')
        sys.exit(0)
    if args.sndfolder:
        val = args.sndfolder[0]
        write_conf('SNDROOT', args.sndfolder[0])
        print(f'Set destination folder of ISOs sound files (sndfolder) to:\n{val}')
        sys.exit(0)
    if args.clearconf:
        write_conf('RAWROOT', '')
        write_conf('SYNCEDROOT', '')
        write_conf('SNDROOT', '')
        write_conf('PROXIES', '')
        print_out_conf('','','','')
        sys.exit(0)
    if args.showconf:
        get_proj()
        print_out_conf(*get_proj(True))
        sys.exit(0)

if __name__ == '__main__':
    main()
