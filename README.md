# ssh-manager
Simple CLI tool for creating and tracking SSH keys and creation/expiration dates. 

## Description
This is an automation and tracking tool that uses the subprocess module from python to create and track SSH keys and their creation/expiration dates. Currently there is no database integration, the program will generate a file "expiration_dates.json" that will track all expiration dates and creation dates, as well as the names of each key on the system. If there are existing keys, the program will automatically add those keys to the expiration_dates.json and begin tracking the date of creation as the most current date.
By default, all keys are set to expire 12 months from creation date, however, work is being done to add custom expiration dates for each key based on user input. A timestamp is also added to the file for easier organization and visualization of each key pair.
The manager will also update the SSH config file as well. There is a prompt after creating a new key that will guide the user in adding the proper information, or if you wish to manage this manually, it is optional. 
The manager will also display the all of the keys on the system (see the usage/visuals block below) and display the contents of the config file.
Currently there is no automatic syncing (there is work to add this feature), so the --sync or -s option will have to be run to sync the contents of the expiration_dates.json with the current contents of the .ssh directory. So if keys are removed, the --sync option will need to be called in order for the program to sync with the system.

## Visuals

## Installation

## Usage
```
ssh_manager -n gitlab -kt ed25519 (will output: id_ed25519_gitlab_<timestamp>)
ssh_manager -l (lists current keys on system including creation and expiration dates)
ssh_manager -lc (lists the current contents of .ssh/config)
ssh_manager --sync (syncs the current contents of the .ssh file to the expiration_dates.json, this function also prunes the json file if keys have been removed)

```
## Support

## Contributing

## Authors and acknowledgment
+ Aaron Newman
+ aaron.newman@landotec.io

## License

## Project status
