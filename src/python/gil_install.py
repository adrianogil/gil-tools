#!/usr/bin/env python2
import sys, json, os, subprocess

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

from subprocess import *

def get_git_root(p):
    """Return None if p is not in a git repo, or the root of the repo if it is"""
    if call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, 'w'), cwd=p) != 0:
        return None
    else:
        root = check_output(["git", "rev-parse", "--show-toplevel"], cwd=p)
        root = root.strip()
        return root

def get_git_url():
    git_url_cmd = "git config --get remote.origin.url"
    git_url_output = subprocess.check_output(git_url_cmd, shell=True)
    git_url_output = git_url_output.strip()

    return git_url_output

class GilInstallController:
    def __init__(self):
        self.installation_file = "install.gil"
        self.config_file = os.environ["HOME"] + "/.bash_install"

    def finish(self):
        # We can also close the cursor if we are done with it
        pass

    def create(self, args, extra_args):
        install_info = {}

        install_macro = args[0]

        print("Using MACRO installation: " + install_macro)
        install_info['DIR_MACRO'] = install_macro

        if len(args) > 1:
            print("Using BASHRC script: " + args[1])
            install_info['BASHRC'] = args[1]
        else:
            find_bashrc_cmd = "find . -name 'bashrc.sh' | head -1"
            find_bashrc_output = subprocess.check_output(find_bashrc_cmd, shell=True)
            find_bashrc_output = find_bashrc_output.strip()

            if find_bashrc_output != "":
                print("Found BASHRC script: " + find_bashrc_output)

                if find_bashrc_output[0:2] == './':
                    find_bashrc_output = find_bashrc_output[2:]

                install_info['BASHRC'] = find_bashrc_output
            else:
                print("No BASHRC script was found!")

        with open(self.installation_file, 'w') as f:
            json.dump(install_info, f)

    def install(self, args, extra_args):
        with open(self.installation_file, 'r') as f:
            install_info = json.load(f)

        if 'DIR_MACRO' in install_info:
            current_dir = os.getcwd()

            git_root_path = get_git_root(current_dir)
            git_url = get_git_url()

            repo_name = os.path.basename(git_root_path)

            install_macro = install_info['DIR_MACRO']

            found = False

            try:
                verify_dir_install_cmd = "cat '" + self.config_file + "' | grep '" + \
                        install_macro + "'"
                verify_dir_install_output = subprocess.check_output(verify_dir_install_cmd, shell=True)
                verify_dir_install_output = verify_dir_install_output.strip()

                found = verify_dir_install_output != ""
            except:
                # Maybe the export does not exist. So let's create it
                print("It seems that export config file does not exist. Let's create it")
                found = False

            if not found:
                if os.path.exists(self.config_file):
                    f = open(self.config_file, 'a+')
                else:
                    f = open(self.config_file, 'w+')
                f.write("##### %s #####\n" % (repo_name,))
                f.write("# GitRepo: %s\n" % (git_url,))
                f.write("# InstallDir: %s\n" % (git_root_path,))
                f.write("export %s=%s\n" % (install_macro,current_dir))

                if 'BASHRC' in install_info:
                    f.write("source $%s/%s\n" % (install_macro, install_info['BASHRC']))
                    f.write("\n")
                f.close()

    def get_commands(self):
        commands_parse = {
            '-c'           : self.create,
            '-i'           : self.install,
            '--create'     : self.create,
            '--install'    : self.install,
            # '--list-args'  : self.list_args,
            # '--auto-list'  : self.auto_list,
            # 'no-args'      : self.handle_no_args,
        }
        return commands_parse

controller = GilInstallController()
commands_parse = controller.get_commands()

def parse_arguments():

    args = {}

    last_key = ''

    if len(sys.argv) == 1:
        controller.handle_no_args()
        return None

    for i in range(1, len(sys.argv)):
        a = sys.argv[i]
        if a[0] == '-' and not is_float(a):
            last_key = a
            args[a] = []
        elif last_key != '':
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
