# gil-tools
Personal tools

## Command line options

Install gil-projects, i.e., projects that have install.gil file
```
cd <gil-project-path>
gil-install -i
```


Clone a repo, enter it and add it to mydirs and to GitRepoWatcher tools
```
gil-clone <url>
```

## Installation - Manually add configuration to bashrc

Add the following lines to your bashrc:
```
export AGIL_SCRIPTS_DIR=/<path-to>/gil-tools/
source ${AGIL_SCRIPTS_DIR}/bashrc.sh
```

## Installation - using gil-install

Requirements:
* you should be have a .bash_install file loaded by .bashrc
* or you can use my dotfiles project


```
cd <gil-tools-path>/src
python3 python/gil_install.py -i
```


## Planned features
- Add directory to mydirs and GitRepoWatcher
- Automated way to install all my default tools
- Setup termux and install all my default tools
- Automated installation of projects based on bashrc.sh pattern
- Clone, and go inside directory and create project files based on templates
