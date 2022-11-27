#!/usr/bin/env python3
"""
    Script that automatically install Gil projects by:
    - creating a link to project shellscript from main .bashrc.sh

"""
from subprocess import *

import subprocess
import shutil
import json
import sys
import os


try:
    range = xrange
except NameError:
    pass


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    return False


def get_git_root(target_path=None):
    """
        Returns None if target_path is not in a git repo, or the root of the repo if it is
    """

    if target_path is None:
        target_path = os.getcwd()

    if call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, "w"), cwd=target_path) != 0:
        return None
    else:
        root = check_output(["git", "rev-parse", "--show-toplevel"], cwd=target_path)
        root = root.decode('utf-8').strip()
        return root


def run_cmd(cmd, return_as_list=False):
    """
        Run a command using interactive_bash 
        In case interactive_bash doesn't exists, it's automatically create a new one
        By using interactive_bash it guarantees that ~/.bashrc is loaded
    """
    ibash_exe = "/usr/local/bin/interactive_bash"

    import pathlib

    # Create ibash_exe if doesnt exists
    if not os.path.exists(ibash_exe):
        try:
            local_ibash_path = pathlib.Path(__file__).parent.parent.joinpath("bin").joinpath("interactive_bash").resolve()
            shutil.copy(local_ibash_path, ibash_exe)
        except Exception as exception:
            print("Error while trying to create an interactive_bash script: ", exception)
    try:
        if os.path.exists(ibash_exe):
            output = subprocess.check_output(cmd, shell=True, executable=ibash_exe, stderr=DEVNULL)
        else:
            print('Warning: /usr/local/bin/interactive_bash doesn\'t exists. You may want to create it')
            output = subprocess.check_output(cmd, shell=True, stderr=DEVNULL)

        output = output.decode("utf-8").strip()

        if return_as_list and output and output.__class__ == str:
            return output.split("\n")
    except Exception as _:
        return None

    return output


def get_git_url():
    git_url_cmd = "git config --get remote.origin.url"

    return run_cmd(git_url_cmd)


class GilInstallController:
    installation_file = "install.gil"

    def __init__(self):
        self.config_file = os.environ["HOME"] + "/.bash_install"

    def finish(self):
        # We can also close the cursor if we are done with it
        pass

    def create(self, args, extra_args):
        install_info = {}

        if len(args) < 1:
            print("Error: you should provide at least the name of MACRO that will represent project path")
            return

        if len(args) >= 2:
            project_name = args[2]
        else:
            project_name = os.path.basename(get_git_root())

        print('Creating install file for project %s' % (project_name,))

        install_macro = args[0]

        print("Using MACRO installation: " + install_macro)
        install_info["DIR_MACRO"] = install_macro

        install_info["PROJECT_NAME"] = project_name

        if len(args) > 1:
            print("Using BASHRC script: " + args[1])
            install_info["BASHRC"] = args[1]
        else:
            find_bashrc_output = run_cmd("find . -name 'bashrc.sh' | head -1")

            if find_bashrc_output != "":
                print("Found BASHRC script: " + find_bashrc_output)

                if find_bashrc_output[0:2] == "./":
                    find_bashrc_output = find_bashrc_output[2:]

                install_info["BASHRC"] = find_bashrc_output
            else:
                print("No BASHRC script was found!")

        with open(self.installation_file, "w") as file_handle:
            json.dump(install_info, file_handle, indent=4)

    def verify_installation(self, args, extra_args):

        target_install_file = self.installation_file
        if len(args) > 0:
            target_install_file = args[0]
        if not os.path.exists(target_install_file):
            target_install_file = self.search_for_install_file()

        with open(target_install_file, "r") as f:
            install_info = json.load(f)

        if "DIR_MACRO" not in install_info:
            print("Wrong usage!")
            return

        install_macro = install_info["DIR_MACRO"]

        found = False
        try:
            verify_dir_install_cmd = (
                "cat '" + self.config_file + "' | grep '" + install_macro + "'"
            )
            verify_dir_install_output = subprocess.check_output(
                verify_dir_install_cmd, shell=True
            )
            verify_dir_install_output = verify_dir_install_output.strip()

            found = verify_dir_install_output != ""
        except Exception as _:
            # Maybe the export does not exist. So let's create it
            # print("It seems that export config file does not exist. Let's create it")
            found = False

        if found:
            print("The current repo is already installed!")
        else:
            print("The current repo is not installed!")

    def search_for_install_file(self):
        current_dir = os.getcwd()
        find_gilfile_output = run_cmd(
            "find . -name '%s' | head -1" % (self.installation_file,)
        )

        if find_gilfile_output == "":
            print("No '%s' file found!!!" % (self.installation_file,))
            exit()
        else:
            current_dir = find_gilfile_output

        return current_dir

    def get_project_name(self, installfile_path=None, install_data=None):
        if not install_data:
            with open(installfile_path, "r") as f:
                install_data = json.load(f)

        project_name = install_data.get("project_name", None)

        if not project_name:
            project_path = get_git_root(os.getcwd())
            project_name = os.path.basename(project_path)

        return project_name

    def uninstall(self, args, extra_args):
        installfile_path = run_cmd(
            "find . -name '%s' | head -1" % (self.installation_file,)
        )
        project_name = self.get_project_name(installfile_path)

        print('Uninstalling project %s' % (project_name,))

        if os.path.exists(self.config_file):
            new_install_lines = []
            install_lines = []
            with open(self.config_file, "r") as f:
                install_lines = f.readlines()

            search_string = "##### %s #####" % (project_name,)

            found_config = False

            new_install_lines = []

            line_index = 0
            while line_index < len(install_lines):
                if search_string in install_lines[line_index]:
                    found_config = True
                    line_index = line_index + 5
                else:
                    new_install_lines.append(install_lines[line_index])
                line_index += 1

            if found_config:
                with open(self.config_file, "w") as f:
                    for new_line in new_install_lines:
                        f.write(new_line)
                print('Project %s uninstalled' % (project_name,))
            else:
                print('Error: Project doesn\'t seem installed')
        else:
            print("Error: Project directory can't be found!")

    def install(self, args, extra_args):
        current_dir = os.getcwd()
        installfile_path = os.path.join(current_dir, self.installation_file)
        if not os.path.exists(installfile_path):
            installfile_path = self.search_for_install_file()

            if installfile_path == "":
                print("No 'install.gil' file found!!!")
                exit()

        installfile_dir = os.path.dirname(os.path.abspath(installfile_path))

        print('Loading configuration from %s' % (installfile_path,))
        with open(installfile_path, "r") as f:
            install_info = json.load(f)

        if "DIR_MACRO" in install_info:
            repo_name = self.get_project_name(install_data=install_info)
            print('Installing project %s' % (repo_name,))

            git_root_path = get_git_root(current_dir)
            git_url = get_git_url()

            install_macro = install_info["DIR_MACRO"]

            found = False

            try:
                verify_dir_install_cmd = (
                    "cat '" + self.config_file + "' | grep '" + install_macro + "'"
                )
                verify_dir_install_output = subprocess.check_output(
                    verify_dir_install_cmd, shell=True
                )
                verify_dir_install_output = verify_dir_install_output.strip()

                found = verify_dir_install_output != ""
            except Exception as _:
                # Maybe the export does not exist. So let's create it
                print("- It seems that export config file does not exist. Let's create it")
                found = False

            if found:
                print(" - Project already installed!")
                exit()
            else:
                if os.path.exists(self.config_file):
                    f = open(self.config_file, "a+")
                else:
                    f = open(self.config_file, "w+")
                f.write("\n")
                f.write("##### %s #####\n" % (repo_name,))
                f.write("# GitRepo: %s\n" % (git_url,))
                f.write("# InstallDir: %s\n" % (git_root_path,))
                f.write("export %s=%s\n" % (install_macro, installfile_dir))

                if "BASHRC" in install_info:
                    f.write("source $%s/%s\n" % (install_macro, install_info["BASHRC"]))
                    f.write("\n")
                f.close()

            print(" - Verify if there aren't any python requirements files")
            requeriments_files = run_cmd("find %s -name 'requirements.txt'" % (os.getcwd(),), return_as_list=True)
            if requeriments_files:
                for requirement in requeriments_files:
                    if requirement:
                        requirement = requirement.strip()
                        run_cmd("pip install -r %s" % (requirement,))
            print(" - Save repo in mydirs")
            run_cmd("mydirs -s")
            print(" - Save repo in GitRepoWatcher database")
            run_cmd("rw -s")

    def load_install_file(self, path='install.gil'):
        if not os.path.exists(path):
            return None

        install_info = None

        with open(path, "r") as f:
            install_info = json.load(f)

        return install_info


    def verify_install_dir(self, args, extra_args):
        """
            Returns the directory it should be installed
        """
        default_dir = args[0]

        install_data = self.load_install_file()

        if not install_data:
            print(default_dir)
            return

        install_dir = default_dir

        if 'default_path' in install_data:
            install_dir = run_cmd('echo ' + install_data["default_path"])

        print(install_dir)

    def list_installs(self, args, extra_args):
        if not os.path.exists(self.config_file):
            print("No projects installed")
            return

        search_string = ""
        if len(args) > 0:
            search_string = args[0]

        new_install_lines = []
        install_lines = []
        with open(self.config_file, "r") as f:
            install_lines = f.readlines()

        project_name_list = []

        print("Installed projects")
        for line in install_lines:
            if line.startswith("##### "):
                end = line.index(" #####")
                repo_name = line[6:end]
                if not search_string or search_string in repo_name:
                    project_name_list.append(repo_name)

        project_name_list = sorted(project_name_list)

        for project_name in project_name_list:
            print("- %s" % (project_name,))

    def show_help(self, args, extra_args):
        help_text = "gil-install: generation and installation of projects based on bashrc.sh\n\n"
        help_text = help_text + "\tCreate a installation file:\n\t$ gil-install -c\n\n"
        help_text = help_text + "\tInstall a project:\n\t$ gil-install -i\n\n"
        help_text = help_text + "\tUninstall a project:\n\t$ gil-install -u\n\n"
        help_text = help_text + "\tVerify installation:\n\t$ gil-install -v\n\n"

        print(help_text)

    def get_commands(self):
        commands_parse = {
            "-c": self.create,
            "-i": self.install,
            "-u": self.uninstall,
            "-h": self.show_help,
            "-v": self.verify_installation,
            "-l": self.list_installs,
            "--help": self.show_help,
            "--create": self.create,
            "--install": self.install,
            "--uninstall": self.uninstall,
            "--verify": self.verify_installation,
            "--verify-dir": self.verify_install_dir,
            # '--list-args'  : self.list_args,
            # '--auto-list'  : self.auto_list,
            # 'no-args'      : self.handle_no_args,
        }
        return commands_parse

def parse_arguments(controller):

    args = {}

    last_key = ""

    if len(sys.argv) == 1:
        controller.handle_no_args()
        return None

    for i in range(1, len(sys.argv)):
        a = sys.argv[i]
        if a[0] == "-" and not is_float(a):
            last_key = a
            args[a] = []
        elif last_key != "":
            arg_values = args[last_key]
            arg_values.append(a)
            args[last_key] = arg_values

    return args


def parse_commands(commands_parse, args):
    if args is None:
        return

    # print('DEBUG: Parsing args: ' + str(args))
    for a in args:
        if a in commands_parse:
            commands_parse[a](args[a], args)


if __name__ == '__main__':
    controller = GilInstallController()
    commands_parse = controller.get_commands()

    args = parse_arguments(controller)
    parse_commands(commands_parse, args)

    controller.finish()
