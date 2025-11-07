import sys
from syutils import cmd_parse
from .extzip import ExtZip
if __name__ == '__main__':
    cmd=cmd_parse(sys.argv)
    if 'path' not in cmd.keys():
        raise Exception('Path not specified')
    extend=cmd.get('extend',False)
    paths=cmd.get('path').split(',')
    proc_num=int(cmd.get('proc',1))
    dryrun=int(cmd.get('dryrun',False))
    noprint=int(cmd.get('noprint',False))
    for path in paths:
        extzip=ExtZip(path,extend,proc_num,dryrun,noprint)
        extzip.run()
