# Python_config_manager

## Read this in Edit mode for better visual

## How to install:
run bootstrap.sh
in case it didn't work: 
- install python3
- pip3 install -r requirements.txt

## how to run
- add a config file to config.d
- run main.py using python3
- This is not a deamonized tool

## Quick Archeticture
- the tool will read the config files first. 
- then will prepare the SSH connections.
- then will start interpret file by file.
- each config file should be sequential, as I started changing the files first, then the packages then the services.
- one config file can be implemented on multible hosts by adding more hosts to the Hosts section the config will be applyed to them too.
- I didn't really play around a lot with the AsyncIO, hoowever there is huge pussibility to play with it in this situation, as we can paralize configs implementations and also implementing one config to multible hosts at the same time.
- I havn't add a section for bash commands to be executed on the hosts, however this is also possible.
- ofcourse python won't be the Fastest programming language to take such project to the next level, a coumpiled language would be the best.

  
## Quick Notes

This config manager was created as a test, it is less than one day job. 
The main idea here is that config are written in Json, and each config is applied on its own.


The below is an example for the config. 
you can ssh using both keys or passwords

if you are installing a package or removing a package, and you would like to restart the service relater please mention the service name in the list "related_services" and don't change the list name. 
for the files, each file should be a full path.
when writing data to a file you should respect that you can't add normal text, however you can woek around this by adding regix to express /n and /t and so on. 

while setting the hosts if you are using passwd only please set the login_key_file to null, and if you are using a key provide full key path and set login_pass to null.

you can add multible hosts and the tool will execute the same changes to both of them.



{
	"Services": {
		"Service1.name": "Stop",
		"Service2.name": "Start",
		"Service3.name": "Reload",
		"Service4.name": "Restart"
	},
	"Packages":{
		"package1.name": "install",
		"package2.name": "remove",
		"package3.name": "update",
		"related_services": ["service1.name", "service2.name"]
	},
	"Files":{
		"/var/www/html/index.html":{
			"Create":"text in the file",
			"update_permissions": "442",
			"update_owner": "user",
			"modify": "text in the file",
			"related_services": ["service1", "service2"]
		},
		"/var/www/html/index.php":{
			"Delete": null,
			"Create":"text in the file",
			"update_permissions": "442",
			"update_owner": "user",
			"modify": "text in the file",
			"related_services": ["service1", "service2"]
		}
	},
	"Hosts":{
		"Uniq_hostname1":{
			"fqdn_ip": "x.com",
			"login_user": "username",
			"login_pass": null, 
			"login_key_file": "file_path"
		},
    "Uniq_hostname2":{
			"fqdn_ip": "196.45.34.5",
			"login_user": "username",
			"login_pass": "Password", 
			"login_key_file": null
		}
	}
}
