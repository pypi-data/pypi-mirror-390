''' opencos.tools.verilator - Used by opencos.eda for sim and elab commands with --tool=verilator.

Contains classes for ToolVerilator and VerilatorSim, VerilatorElab.
'''

# pylint: disable=R0801 # (calling functions with same arguments)

import multiprocessing
import os
import shutil
import subprocess


from opencos import util
from opencos.eda_base import Tool
from opencos.commands import CommandSim
from opencos.utils.str_helpers import sanitize_defines_for_sh

class ToolVerilator(Tool):
    '''ToolVerilator used by opencos.eda for --tool=verilator'''

    _TOOL = 'verilator'
    _EXE = 'verilator'
    _URL = 'github.com/verilator/verilator'

    verilator_base_path = ''
    verilator_exe = ''
    verilator_coverage_exe = ''

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION
        path = shutil.which(self._EXE)
        if not path:
            self.error(f'"{self._EXE}" not in path or not installed, see {self._URL})')
        else:
            self.verilator_exe = path
            self.verilator_base_path, _ = os.path.split(path)

        # Let's get the verilator_coverage path from the same place as verilator.
        if path:
            self.verilator_coverage_exe = shutil.which(
                os.path.join(self.verilator_base_path, 'verilator_coverage')
            )
        if not self.verilator_coverage_exe:
            util.warning('"verilator_coverage" not in path, need from same path',
                         f'as "{self.verilator_exe}"')

        version_ret = subprocess.run(
            [self.verilator_exe, '--version'],
            capture_output=True,
            check=False
        )
        stdout = version_ret.stdout.decode('utf-8', errors='replace')
        util.debug(f'{path=} {version_ret=}')
        words = stdout.split() # 'Verilator 5.027 devel rev v5.026-92-g403a197e2
        if len(words) < 1:
            self.error(f'{self.verilator_exe} --version: returned unexpected string {version_ret=}')
        version = words[1]
        ver_list = version.split('.')
        if len(ver_list) != 2:
            self.error(f'{self.verilator_exe} --version: returned unexpected',
                       f'string {version_ret=} {version=}')
        self._VERSION = version
        return self._VERSION

    def set_tool_defines(self):
        # We don't need to define VERILATOR, the verilated exe does that itself.
        pass

class VerilatorSim(CommandSim, ToolVerilator):
    '''VerilatorSim is a command handler for: eda sim --tool=verilator'''

    def __init__(self, config: dict):
        CommandSim.__init__(self, config=config)
        ToolVerilator.__init__(self, config=self.config)
        self.args.update({
            'gui': False,
            'tcl-file': None,
            'dump-vcd': False,
            'waves-fst': True,
            'waves-vcd': False,
            'lint-only': False,
            'cc-mode': False,
            'verilator-coverage-args': [],
            'uvm': False,
            'x-assign': '',
            'x-initial': '',
        })

        self.args_help.update({
            'waves': (
                'Include waveforms, if possible for Verilator by applying'
                ' simulation runtime arg +trace. User will need SV code to interpret the'
                ' plusarg and apply $dumpfile("dump.fst").'
            ),
            'waves-fst': (
                '(Default True) If using --waves, apply simulation runtime arg +trace.'
                ' Note that if you do not have SV code using $dumpfile, eda will add'
                ' _waves_pkg.sv to handle this for you with +trace runtime plusarg.'
            ),
            'waves-vcd': (
                'If using --waves, apply simulation runtime arg +trace=vcd. User'
                ' will need SV code to interpret the plusarg and apply'
                ' $dumpfile("dump.vcd").'
            ),
            'dump-vcd': 'Same as --waves-vcd',
            'lint-only': 'Run verilator with --lint-only, instead of --binary',
            'gui':       'Not supported for Verilator',
            'cc-mode':   'Run verilator with --cc, requires a sim_main.cpp or similar sources',
            'optimize':  'Run verilator with: -CLAGS -O3, if no other CFLAGS args are presented',
            'x-assign': ('String value to added to verilator call: --x-assign <string>;'
                         ' where valid string values are: 0, 1, unique, fast.'
                         ' Also conditinally adds to verilated exe call:'
                         ' +verilator+rand+reset+[0,1,2] for arg values 0, 1, unique|fast'),
            'x-initial': ('String value to added to verilator call: --x-initial <string>;'
                         ' where valid string values are: 0, unique, fast.'
                         ' Also conditinally adds to verilated exe call:'
                         ' +verilator+rand+reset+[0,2] for arg values 0, unique|fast'),
            'uvm': (
                'Warns on Verilator < 5.042, or missing $UVM_HOME environment var set (or in'
                ' .env, $UVM_HOME/uvm_pkg.sv should exist), and will run verilator with args:'
                ' -Wno-fatal +define+UVM_NO_DPI'
            ),
            'verilator-coverage-args': (
                'Requires --coverage, args to be applied to verilator_coverage, which runs'
                ' after running the compiled executable simulation'
            ),
        })

        self.verilate_command_lists = []
        self.lint_only_command_lists = []
        self.verilated_exec_command_lists = []
        self.verilated_post_exec_coverage_command_lists = []


    def set_tool_defines(self):
        ToolVerilator.set_tool_defines(self)
        self.defines.update(
            self.tool_config.get('defines', {})
        )

    # We do not override CommandSim.do_it()
    def prepare_compile(self):
        self.set_tool_defines()

        # If there are C++ files here, then we will run Verilator in --cc mode:
        if self.files_cpp:
            self.args['cc-mode'] = True

        self.add_waves_pkg_file()

        # Each of these should be a list of util.ShellCommandList()
        self.verilate_command_lists = self.get_compile_command_lists()
        self.lint_only_command_lists = self.get_compile_command_lists(lint_only=True)
        self.verilated_exec_command_lists  = self.get_simulate_command_lists()
        self.verilated_post_exec_coverage_command_lists = self.get_post_simulate_command_lists()

        paths = ['obj_dir', 'logs']
        util.safe_mkdirs(base=self.args['work-dir'], new_dirs=paths)

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='lint_only.sh',
                                      command_lists=self.lint_only_command_lists, line_breaks=True)

        sim_cmd_lists = self.verilated_exec_command_lists + \
            (self.verilated_post_exec_coverage_command_lists
             if self.args.get('coverage', True) else [])

        self.write_sh_scripts_to_work_dir(
            compile_lists=self.verilate_command_lists,
            elaborate_lists=[],
            simulate_lists=sim_cmd_lists
        )


    def compile(self):
        if self.args['stop-before-compile']:
            return
        if self.args.get('lint-only', False):
            # We do not scrape compile logs for "must" strings (use_must_strings=False)
            self.run_commands_check_logs(self.lint_only_command_lists, use_must_strings=False)
        else:
            self.run_commands_check_logs(self.verilate_command_lists, use_must_strings=False)

    def elaborate(self):
        pass

    def simulate(self):
        if self.args.get('lint-only', False):
            return

        if self.args['stop-before-compile'] or self.args['stop-after-compile'] or \
           self.args['stop-after-elaborate']:
            # don't run this if we're stopping before/after compile/elab
            return

        if not os.path.isfile(os.path.join(self.args['work-dir'], 'obj_dir', 'sim.exe')):
            self.error('Verilated executable obj_dir/sim.exe does not exist')
            return

        # Note that this is not returning a pass/fail bash return code,
        # so we will likely have to log-scrape to deterimine pass/fail.
        # Also, if we ran in cc-mode, we will not get the "R e p o r t: Verilator"
        # in the sim.exe results, unless that was added to the C++ main.
        use_must_strings = not self.args['cc-mode'] # disable in --cc mode.
        self.run_commands_check_logs(
            commands=self.verilated_exec_command_lists,
            use_must_strings=use_must_strings
        )

        if self.args.get('coverage', True):
            # do not check logs on verilator_coverage commands:
            self.run_commands_check_logs(
                commands=self.verilated_post_exec_coverage_command_lists,
                check_logs=False
            )

    def get_compile_command_lists(self, **kwargs) -> list:

        # Support for lint_only (bool) in kwargs:
        lint_only = kwargs.get('lint_only', False)

        verilate_command_list = self._get_start_verilator_command_list(lint_only=lint_only)

        # Handle UVM things (return args), but also handles uvm_pkg.sv in self.files_sv:
        # since we run this 2x (lint-only and normal) only do warnings for one of them:
        verilate_command_list += self._verilator_args_uvm(
            warnings=(not lint_only), add_uvm_pkg_if_found=True
        )

        verilate_command_list += self._get_verilator_tool_config_waivers()

        verilate_command_list += self._verilator_args_defaults_cflags_nproc()

        verilate_command_list += self._get_verilator_waves_args(lint_only=lint_only)


        if self.args.get('coverage', True):
            verilate_command_list += self.tool_config.get(
                'compile-coverage-args', '--coverage').split()

        verilate_command_list += [
            '-top', self.args['top'],
        ]

        if not lint_only:
            verilate_command_list += [
                '-o', 'sim.exe',
            ]

        for arg in ('x-assign', 'x-initial'):
            if self.args[arg] and f'--{arg}' not in verilate_command_list:
                # Only add this if arg is set, and not present in verilator call
                # this takes care of it being in our self.tool_config for compile-args.
                verilate_command_list += [
                    f'--{arg}', self.args[arg]
                ]

        # incdirs
        for value in self.incdirs:
            verilate_command_list += [ f"+incdir+{value}" ]

        # defines
        for k,v in self.defines.items():
            if v is None:
                verilate_command_list += [ f'+define+{k}' ]
            else:
                # Generally we should only support int and str python types passed as
                # +define+{k}={v}, but also for SystemVerilog plusargs
                verilate_command_list += [ f'+define+{k}={sanitize_defines_for_sh(v)}' ]

        # parameters
        verilate_command_list.extend(
            self.process_parameters_get_list(arg_prefix='-G')
        )

        if not self.files_sv and not self.files_v:
            if not self.args['stop-before-compile']:
                self.error(f'{self.target=} {self.files_sv=} and {self.files_v=} are empty,',
                           'cannot call verilator')

        verilate_command_list += list(self.files_sv) + list(self.files_v)

        if self.args['cc-mode']:
            # Verilator --cc mode, we have to also add the C++ file to our verilate command:
            verilate_command_list += list(self.files_cpp)

        return [ util.ShellCommandList(verilate_command_list, tee_fpath='compile.log') ]

    def get_elaborate_command_lists(self, **kwargs) -> list:
        return []

    def get_simulate_command_lists(self, **kwargs) -> list:

        # verilator needs the seed to be < 2*31-1
        verilator_seed = int(self.args['seed']) & 0xfff_ffff

        assert isinstance(self.args['sim-plusargs'], list), \
            f'{self.target=} {type(self.args["sim-plusargs"])=} but must be list'

        sim_plusargs = []
        for x in self.args['sim-plusargs']:
            # For Verilator we need to add a +key=value if the + is missing
            if x[0] != '+':
                x = f'+{x}'
            sim_plusargs.append(x)

        # TODO(drew): don't have a use-case yet for self.args['sim-library', 'elab-args'] in the
        # verilated executable 'simulation' command list, but we may need to support them if we
        # have more than 'work' library.

        verilated_exec_command_list = [
            './obj_dir/sim.exe',
        ]

        config_sim_args = self.tool_config.get(
            'simulate-args', ''
        ).split()

        if self.args['waves']:
            sim_waves_args_list = self.tool_config.get('simulate-waves-args', '').split()
            config_sim_args += sim_waves_args_list
            if not any(x.startswith('+trace=') or x == '+trace' for x in \
                        config_sim_args + sim_plusargs + self.args['sim-args']):
                # Built-in support for eda args --waves and/or --dump-vcd to become runtime
                # plusargs +trace or +trace=vcd, if +trace or +trace= was not already in our
                # plusargs.
                if self.args.get('dump-vcd', False) or \
                   self.args.get('waves-vcd', False):
                    sim_plusargs.append('+trace=vcd')
                elif self.args.get('waves-fst', False):
                    sim_plusargs.append('+trace')

        verilated_exec_command_list += config_sim_args + sim_plusargs + self.args['sim-args']


        # We need to set the seed if none of the other args did:
        if not any(x.startswith('+verilator+seed+') for x in verilated_exec_command_list):
            verilated_exec_command_list.append(f'+verilator+seed+{verilator_seed}')

        if any(self.args[arg] in ('unique', 'fast') for arg in ('x-assign', 'x-initial')) and \
           not any(x.startswith('+verilator+rand+reset') for x in verilated_exec_command_list):
            # Only add this if arg is one of x-assign/x-initial is set to "unique" or "fast",
            # we use the encoded value "2" for +verilator+rand+reset+2
            verilated_exec_command_list.append('+verilator+rand+reset+2')

        if self.args['x-assign'] == '1' and \
           not any(x.startswith('+verilator+rand+reset') for x in verilated_exec_command_list):
            # Only add this if --x-assign=1 (not valid for --x-initial),
            # we use the encoded value "1" for +verilator+rand+reset+1
            verilated_exec_command_list.append('+verilator+rand+reset+1')


        return [
            util.ShellCommandList(verilated_exec_command_list, tee_fpath='sim.log')
        ] # single entry list


    def get_post_simulate_command_lists(self, **kwargs) -> list:

        if self.args.get('coverage', True):
            if not self.verilator_coverage_exe:
                self.error(f'verilator_coverage not found in path with {self.verilator_exe}')
                return []

            verilated_post_exec_coverage_command_list = [self.verilator_coverage_exe]
            config_coverage_args = self.tool_config.get(
                'coverage-args',
                '--annotate logs/annotated coverage.dat').split()

            verilated_post_exec_coverage_command_list += \
                config_coverage_args + self.args['verilator-coverage-args']


            return [ util.ShellCommandList(verilated_post_exec_coverage_command_list,
                                           tee_fpath='coverage.log') ] # single entry list

        return []

    def add_waves_pkg_file(self) -> None:
        '''If --waves present, and the user is missing any $dumpfile(), then adds a pre-written
        SystemVerilog package to their source code.
        '''
        if self.args['cc-mode']:
            # We won't do this if the user brought a .cpp file and verilator not
            # called with --binary.
            return

        super().add_waves_pkg_file() # call from CommandSim



    def _get_start_verilator_command_list(self, lint_only: bool = False) -> list:

        verilate_command_list = [
            self.verilator_exe,
        ]
        if self.args['cc-mode']:
            verilate_command_list += [
                '--cc',
                '--build',
                '--exe',
            ]
        elif lint_only:
            verilate_command_list.append('--lint-only')
        else:
            verilate_command_list.append('--binary')

        return verilate_command_list

    def _get_verilator_tool_config_waivers(self) -> list:

        # Add compile waivers from self.config (tools.verilator.compile-waivers list):
        # list(set(mylist)) to get unique.
        ret = []
        for waiver in self.tool_config.get(
                'compile-waivers',
                [ #defaults:
                    'CASEINCOMPLETE',
                    'TIMESCALEMOD', # If one file has `timescale, then they all must
                ]) + self.args['compile-waivers']:
            ret.append(f'-Wno-{waiver}')
        return ret

    def _get_verilator_waves_args(self, lint_only: bool = False) -> list:

        ret = []
        if self.args.get('waves', False) and not lint_only:
            # Skip waves if this is elab or lint_only=True
            config_waves_args = self.tool_config.get(
                'compile-waves-args',
                '--trace-structs --trace-params').split()
            ret += config_waves_args
            if self.args.get('dump-vcd', False):
                ret += [ '--trace' ]
            else:
                ret += [ '--trace-fst' ]
        return ret


    def _verilator_args_defaults_cflags_nproc(self) -> list:
        '''Returns list of args to be added to verilator (compile) step

        Uses self.args['verilate-args'], self.args['compile-args'], and self.tool_config

        Sets -j <value> and -CFLAGS -O<value> if not present in --config-yml, --compile-args,
        or --verilate-args. If present, chooses the first instance (does not present duplicates
        to verilator call).
        '''

        # We can only support one -CFLAGS followed by one -O[0-9] arg in
        # --verilate-args or --compile-args.

        # Add compile args from our self.config (tools.verilator.compile-args str)
        verilate_args = self.args['verilate-args'] + \
            self.args['compile-args'] + \
            self.tool_config.get(
                'compile-args',
                '--timing --assert --autoflush -sv').split()

        util.debug(f"{self.args['verilate-args']=}")
        util.debug(f"{self.args['compile-args']=}")

        dash_j_arg_indices = []
        cflags_dasho_args_indices = []
        for i, arg in enumerate(list(verilate_args)):
            # There can only be one of these: -j <value>, similarly can only be one of
            # -CFLAGS -O<value>
            if (i + 1) < len(verilate_args):
                if arg == '-j':
                    dash_j_arg_indices.extend([i, i + 1])
                if arg == '-CFLAGS':
                    next_arg = verilate_args[i + 1]
                    if next_arg.startswith('-O') and len(next_arg) == 3:
                        cflags_dasho_args_indices.extend([i, i + 1])

        # For -j <value> we'll pick the first one, remove the rest.
        # Same goes for -CFLAGS -O<value>
        for index in dash_j_arg_indices[2:] + cflags_dasho_args_indices[2:]:
            verilate_args[index] = ''

        verilate_args = [x for x in verilate_args if x != ''] # strip empty str.

        # Support for --optimize which will use -CFLAGS -O3, if -CFLAGS is not present at all.
        if cflags_dasho_args_indices:
            # add whatever args were passed via 'compile-args' or 'verilate_args'. Note these will
            # take precedence over the --optimize arg.
            pass
        elif self.args['optimize']:
            # translate CommandSim.args['optimize'] into verilator -CFLAGS -O3.
            # (slower compile, better runtime)
            verilate_args += '-CFLAGS', '-O3'
        else:
            # Default to -O1:
            verilate_args += '-CFLAGS', '-O1'

        # If there was no -j setting, then use max(2, $(nproc) - 1)
        if not dash_j_arg_indices:
            nproc = max(2, multiprocessing.cpu_count() - 1)
            verilate_args += '-j', f'{nproc}'


        return verilate_args


    def _verilator_support_uvm_pkg_fpath(self, add_if_found: bool = True) -> bool:
        '''Returns False if we could not find a suitable uvm_pkg.sv to use, or if --no-uvm.

        This will also auto-add uvm_pkg.sv from $UVM_HOME/uvm_pkg.sv if not present in
        self.files already (adds to front of self.files_sv)
        '''

        if not self.args['uvm']:
            return False

        for fname, exists in self.files.items():
            if exists and os.path.split(fname)[1] == 'uvm_pkg.sv':
                # already present in our source files (assume someone doing it manually
                # or via DEPS)
                return True

        uvm_home = os.environ.get('UVM_HOME', '')
        if not uvm_home:
            return False

        uvm_pkg_fpath = os.path.join(uvm_home, 'uvm_pkg.sv')
        if add_if_found and os.path.isfile(uvm_pkg_fpath):
            uvm_pkg_fpath = os.path.abspath(uvm_pkg_fpath)
            util.info(f'For --uvm, adding to source files: {uvm_pkg_fpath}')
            self.files[uvm_pkg_fpath] = True
            self.files_sv.insert(0, uvm_pkg_fpath)
            self.files_caller_info[uvm_pkg_fpath] = 'verilator.py'
            util.info(f'For --uvm, adding +incdir+: {uvm_home}')
            self.incdirs.append(os.path.abspath(uvm_home))
            return True

        return False


    def _verilator_args_uvm(
            self, warnings: bool = True, add_uvm_pkg_if_found: bool = True
    ) -> list:
        '''Returns list of args to be added to verilator (compile) step if --uvm present

        Warnings on potential issues (Veriltor version, missing uvm_pkg.sv).
        Optionally adds uvm_pkg.sv to source files.
        '''

        # Handle --uvm args:
        if not self.args['uvm']:
            return []

        if warnings:

            # prefers Verilator >= v5.042, $UVM_HOME to be set, or warning.
            version_list = self._VERSION.split('.')
            if int(version_list[0]) < 5 or \
               (int(version_list[0]) == 5 and int(version_list[1]) < 42):
                util.warning(f'Verilator version is {self._VERSION}, --uvm set prefers Verilator',
                             'version > v5.042')

            if not os.environ.get('UVM_HOME', ''):
                util.warning('--uvm set, however env (or .env or --env-file) $UVM_HOME is not set')

        uvm_pkg_found = self._verilator_support_uvm_pkg_fpath(add_if_found=add_uvm_pkg_if_found)
        if warnings and not uvm_pkg_found:
            util.warning(
                '--uvm set, however no suitable uvm_pkg.sv is source files,',
                f'nor in $UVM_HOME/uvm_pkg.sv. $UVM_HOME={os.environ.get("UVM_HOME", "")}'
            )

        return ['-Wno-fatal', '+define+UVM_NO_DPI']


    def artifacts_add(self, name: str, typ: str, description: str) -> None:
        '''Override from Command.artifacts_add, so we can catch known file

        names to make their typ/description better, such as CommandSim using
        sim.log or compile.log
        '''
        _, leafname = os.path.split(name)
        if leafname == 'sim.log':
            description = 'Verilated executable log from stdout/stderr'
        elif leafname == 'compile.log':
            description = 'Verilator compile step log from verilator call'

        super().artifacts_add(name=name, typ=typ, description=description)


class VerilatorElab(VerilatorSim):
    '''VerilatorElab is a command handler for: eda elab --tool=verilator'''
    command_name = 'elab'

    def __init__(self, config: dict):
        super().__init__(config)
        self.args['stop-after-elaborate'] = True
        self.args['lint-only'] = True


class VerilatorLint(VerilatorSim):
    '''VerilatorLint is a command handler for: eda lint --tool=verilator.

    For practical reasons, this is identical to VerilatorElab with --stop-after-compile.'''
    command_name = 'lint'

    def __init__(self, config: dict):
        super().__init__(config)
        self.args['stop-after-compile'] = True
        self.args['stop-after-elaborate'] = True
        self.args['lint-only'] = True
