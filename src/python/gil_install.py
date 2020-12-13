#!/usr/bin/env python3
"""
    Script that automatically install Gil projects by:
    - creating a link to project shellscript from main .bashrc.sh

"""
from subprocess import *

import subprocess
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


def get_git_root(p):
    """
    Returns None if p is not in a git repo, or the root of the repo if it is
    """
    if call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, "w"), cwd=p) != 0:
        return None
    else:
        root = check_output(["git", "rev-parse", "--show-toplevel"], cwd=p)
        root = root.strip()
        return root


def run_cmd(cmd, return_as_list=False):
    output = subprocess.check_output(cmd, shell=True)
    output = output.decode("utf-8").strip()
    if return_as_list:
        return output.split("\n")

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
            print(
                "Error: you should provide at least the name of MACRO that will represent project path"
            )
            return

        install_macro = args[0]

        print("Using MACRO installation: " + install_macro)
        install_info["DIR_MACRO"] = install_macro

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

        with open(self.installation_file, "w") as f:
            json.dump(install_info, f)

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
        find_gilfile_cmd = "find . -name '%s' | head -1" % (self.installation_file,)
        find_gilfile_output = subprocess.check_output(find_gilfile_cmd, shell=True)
        find_gilfile_output = find_gilfile_output.decode("utf-8").strip()

        if find_gilfile_output == "":
            print("No '%s' file found!!!" % (self.installation_file,))
            exit()
        else:
            current_dir = find_gilfile_output

        return current_dir

    def install(self, args, extra_args):
        current_dir = os.getcwd()
        if not os.path.exists(self.installation_file):
            find_gilfile_cmd = "find . -name 'install.gil' | xargs -I {} dirname {}"
            find_gilfile_output = subprocess.check_output(find_gilfile_cmd, shell=True)
            find_gilfile_output = find_gilfile_output.decode("utf-8").strip()

            if find_gilfile_output == "":
                print("No 'install.gil' file found!!!")
                exit()
            else:
                current_dir = os.path.join(current_dir, find_gilfile_output)

        with open(os.path.join(current_dir, self.installation_file), "r") as f:
            install_info = json.load(f)

        if "DIR_MACRO" in install_info:

            git_root_path = get_git_root(current_dir)
            git_url = get_git_url()

            repo_name = os.path.basename(git_root_path)

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
                print(
                    "It seems that export config file does not exist. Let's create it"
                )
                found = False

            if found:
                print(" - Project already installed!")
            else:
                if os.path.exists(self.config_file):
                    f = open(self.config_file, "a+")
                else:
                    f = open(self.config_file, "w+")
                f.write("##### %s #####\n" % (repo_name,))
                f.write("# GitRepo: %s\n" % (git_url,))
                f.write("# InstallDir: %s\n" % (git_root_path,))
                f.write("export %s=%s\n" % (install_macro, current_dir))

                if "BASHRC" in install_info:
                    f.write("source $%s/%s\n" % (install_macro, install_info["BASHRC"]))
                    f.write("\n")
                f.close()

            print(" - Verify if there aren't any python requirements files")
            find_requeriments_cmd = ()
            subprocess.check_output(find_requeriments_cmd, shell=True)
            requeriments_files = run_cmd(
                "find . -name 'requirements.txt'", return_as_list=True
            )
            if requeriments_files:
                for requirement in requeriments_files:
                    run_cmd("pip install -r %s" % (requirement,))
            print(" - Save repo in GitRepoWatcher database")
            run_cmd("source ~/.bashrc && rw -s")

    def show_help(self, args, extra_args):
        help_text = "gil-install: generation and installation of projects based on bashrc.sh\n\n"
        help_text = help_text + "\tCreate a installation file:\n\t$ gil-install -c\n\n"
        help_text = help_text + "\tInstall a project:\n\t$ gil-install -i\n\n"
        help_text = help_text + "\tVerify installation:\n\t$ gil-install -v\n\n"

        print(help_text)

    def get_commands(self):
        commands_parse = {
            "-c": self.create,
            "-i": self.install,
            "-h": self.show_help,
            "-v": self.verify_installation,
            "--help": self.show_help,
            "--create": self.create,
            "--install": self.install,
            "--verify": self.verify_installation,
            # '--list-args'  : self.list_args,
            # '--auto-list'  : self.auto_list,
            # 'no-args'      : self.handle_no_args,
        }
        return commands_parse


controller = GilInstallController()
commands_parse = controller.get_commands()


def parse_arguments():

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


def parse_commands(args):
    if args is None:
        return

    # print('DEBUG: Parsing args: ' + str(args))
    for a in args:
        if a in commands_parse:
            commands_parse[a](args[a], args)


args = parse_arguments()
parse_commands(args)

controller.finish()
