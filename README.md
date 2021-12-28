# Backdropper
Backup files to Dropbox

## Installation
* >git clone https://github.com/ctrl-escp/backdropper.git 

cd into the directory and  
* > python3 -m pip install -r requirements.txt
* Get your API by [creating an APP on Dropbox](https://www.dropbox.com/developers/apps/create).
* Place the api key in a file named `.token` or pass it when running the script using the `-t` option.
## Usage
You can always do `python3 backdropper.py -h` to get the following usage text:
```
usage: backdropper.py [-h] [-n NAME] [--do-not-overwrite] [-t TOKEN_FILE] target

Backdropper - Backup to Dropbox.

positional arguments:
  target                The file or directory to upload

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Alternative path/name to save the target under
  --do-not-overwrite    Do not overwrite name if this flag is set
  -t TOKEN_FILE, --token-file TOKEN_FILE
                        Read token from file. By default look for .token in current directory
```
### Examples
Upload a file to the backdropper folder
>python3 backdroppper.py /path/to/target_file

Save file under a different name
> python3 backdroppper.py /path/to/target_file -n new_name

Save file under a different name in a different folder
> python3 backdroppper.py /path/to/target_file -n folder_name/file_name

Save all files in a folder into a zip file and upload it to a zip file with the folder's name
>python3 backdropper.py /path/to/folder
