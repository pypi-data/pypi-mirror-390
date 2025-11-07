from syutils import cmd_parse,mrun
import sys,os
# python extzip.py -path "/mnt/c/code,/home/fund" -extend 'py,pl'

from pathlib import Path

class ExtZip():
    def __init__(self,path,extend=False,proc=1,dryrun=False,noprint=False):
        self.path=path
        self.proc=int(proc)
        self.dryrun=bool(dryrun)
        self.noprint=bool(noprint)
        if extend:
            if ',' in extend:
                self.extend=extend.split(',')
            else:
                self.extend=[extend]
        else:
            self.extend=['txt','csv']
        if not self.check_path():
            print(f'Path {self.path} not exist or not a directory', file=sys.stderr)
            self.files=[]
            return
        self.get_file()
    def check_path(self):
        path_to_check = Path(self.path)
        if path_to_check.exists():
            if path_to_check.is_dir():
                return True
        return False
    def get_file(self):
        self.files = []
        for file in os.listdir(self.path):
            if any(file[-1 * (1 + len(e)) :] == f'.{e}' for e in self.extend):
                self.files.append(file)
    def run(self):
        cmds=[f"""7za a "{self.path}/{file}.7z" "{self.path}/{file}" -sdel >/dev/null 2>&1""" for file in self.files]
        zfiles=[f"{self.path}/{file}.7z" for file in self.files]
        file_for_del=[file for file in zfiles if os.path.exists(file)]
        if self.dryrun:
            for cmd in cmds:
                print(f'Cmd for run: {cmd}')
            for file in file_for_del:
                print(f'File for remove: {file}')
            return
        else:
            if file_for_del:
                for file in file_for_del:
                    try:
                        os.remove(file)
                    except Exception:                    
                        print(f"Fail on delete {file}")

            mrun(cmds,proc_count=self.proc,noprint=self.noprint,stop_on_error=False)

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
