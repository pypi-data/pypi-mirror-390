''' opencos.utils.subprocess_helpers -- wrappers for subprocess to support background/tee'''

import os
import shutil
import subprocess
import sys

import psutil
from opencos.util import debug, error, info, warning, progname, global_log

IS_WINDOWS = sys.platform.startswith('win')

# For non-Windows, we track the background parent PIDs, because some tools (vivado XSim,
# most Modelsim/Questa variants) tend to spawn children PIDs that don't always respond
# nicely to a friendly *nix SIGTERM. So we'll remember what our parent PIDs are, and
# eda.py's (or other CLI opencos script) can use signal to cleanup any remaining
# parents + children using subprocess_helpers.cleanup_all()
ALL_PARENT_PIDS = set()

def subprocess_run(
        work_dir: str, command_list: list, fake: bool = False, shell: bool = False
) -> int:
    ''' Run command_list in the foreground, with preference to use bash if shell=True'''

    proc_kwargs = {
        'shell': shell
    }
    if work_dir:
        proc_kwargs['cwd'] = work_dir

    bash_exec = shutil.which('bash')
    if shell and bash_exec and not IS_WINDOWS:
        proc_kwargs.update({'executable': bash_exec})

    if not IS_WINDOWS and shell:
        c = ' '.join(command_list)
    else:
        c = command_list

    if fake:
        info(f"subprocess_run FAKE: would have called subprocess.run({c}, **{proc_kwargs}")
        return 0

    debug(f"subprocess_run: About to call subprocess.run({c}, **{proc_kwargs}")
    proc = subprocess.run(c, check=True, **proc_kwargs)
    # Note - we do not get PID management for subprocess_run(...)
    return proc.returncode


def subprocess_run_background( # pylint: disable=too-many-branches
        work_dir: str, command_list: list, background: bool = True, fake : bool = False,
        shell: bool = False, tee_fpath: str = ''
) -> (str, str, int):
    ''' Run command_list in the background, with preference to use bash if shell=True

    tee_fpath is relative to work_dir.

    Note that stderr is converted to stdout, and stderr is retuned as '':
        Returns tuple of (stdout str, '', int return code)
    '''

    debug(f'subprocess_run_background: {background=} {tee_fpath=} {shell=}')

    if fake:
        # let subprocess_run handle it (won't run anything)
        rc = subprocess_run(work_dir, command_list, fake=fake, shell=shell)
        return '', '', rc

    proc_kwargs = {'shell': shell,
                   'stdout': subprocess.PIPE,
                   'stderr': subprocess.STDOUT,
                   }
    if work_dir:
        proc_kwargs['cwd'] = work_dir

    bash_exec = shutil.which('bash')
    if shell and bash_exec and not IS_WINDOWS:
        # Note - windows powershell will end up calling: /bin/bash /c, which won't work
        proc_kwargs.update({'executable': bash_exec})

    if not IS_WINDOWS and shell:
        c = ' '.join(command_list)
    else:
        c = command_list # leave as list.

    debug(f"subprocess_run_background: about to call subprocess.Popen({c}, **{proc_kwargs})")
    proc = subprocess.Popen(c, **proc_kwargs) # pylint: disable=consider-using-with
    if not background:
        info(f'PID {proc.pid} for {command_list[0]}')
    add_running_parent_pid(proc.pid)

    stdout = ''
    tee_fpath_f = None
    if tee_fpath:
        tee_fpath = os.path.join(work_dir, tee_fpath)
        try:
            tee_fpath_f = open( # pylint: disable=consider-using-with
                tee_fpath, 'w', encoding='utf-8'
            )
        except Exception as e:
            error(f'Unable to open file "{tee_fpath}" for writing, {e}')

    for line in iter(proc.stdout.readline, b''):
        line = line.rstrip().decode("utf-8", errors="replace")
        if not background:
            print(line)
        if tee_fpath_f:
            tee_fpath_f.write(line + '\n')
        if global_log.file:
            global_log.write(line, '\n')
        stdout += line + '\n'

    proc.communicate()
    remove_completed_parent_pid(proc.pid)

    rc = proc.returncode
    if tee_fpath_f:
        tee_fpath_f.write(f'INFO: [{progname}] subprocess_run_background: returncode={rc}\n')
        tee_fpath_f.close()
        if not background:
            info('subprocess_run_background: wrote: ' + os.path.abspath(tee_fpath))

    return stdout, '', rc


def add_running_parent_pid(pid: int) -> None:
    '''Adds pid (if still alive) to ALL_PARENT_PIDS'''
    try:
        p = psutil.Process(pid)
        ALL_PARENT_PIDS.add(p.pid)
    except psutil.NoSuchProcess:
        pass
    except Exception as e:
        error(f'{pid=} exception {e}')

def remove_completed_parent_pid(pid: int) -> None:
    '''Removes pid (if no longer alive) from ALL_PARENT_PIDS.'''
    try:
        p = psutil.Process(pid)
        warning(f'PID {p.pid} still running')
    except psutil.NoSuchProcess:
        ALL_PARENT_PIDS.remove(pid)
    except Exception as e:
        error(f'{pid=} exception {e}')


def cleanup_all() -> None:
    '''Kills everything from ALL_PARENT_PIDS.'''
    for parent in ALL_PARENT_PIDS:
        kill_proc_tree(parent)


def kill_proc_tree(pid: int, including_parent: bool = True) -> None:
    '''Kills a process and its entire descendant tree'''
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        info(f'{pid=} {parent=} {children=}')
        for child in children:
            if psutil.Process(child.pid):
                info(f'parent {pid=} killing {child=}')
                child.kill()
        _, still_alive = psutil.wait_procs(children, timeout=5)
        if still_alive:
            warning(f'parent {pid=} {still_alive=}')
        if including_parent:
            info(f'parent {pid=} killing {parent=}')
            parent.kill()
            parent.wait(5)
    except psutil.NoSuchProcess:
        pass # Process already terminated
