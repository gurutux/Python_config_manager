import paramiko
import json
import validators
import os
import asyncio

def ssh_to_host(ip_address, user, passwd, key_file):
	ssh_connection = paramiko.SSHClient()
	ssh_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_connection.connect(hostname=ip_address,username=user,password=passwd, key_filename=key_file)
	return ssh_connection


def read_configs():
	script_dir = os.path.dirname(__file__) 
	config_dir = "config.d/"
	abs_config_dir = os.path.join(script_dir, config_dir)
	configs_list = os.listdir(abs_config_dir)
	configs = {}
	for config in configs_list:
		if config != 'example.json':
			file = "{}{}".format(abs_config_dir,config)
			with open(file) as opened_file:
				configs[file] = json.load(opened_file)

	return configs


def setup_ssh_connections(configs):
	ssh_connections = {}
	for path, config in configs.items():
		for host, host_config in config['Hosts'].items():
			if host not in ssh_connections.keys():
				ssh_connections[host] = ssh_to_host(
					host_config['fqdn_ip'],
					host_config['login_user'],
					host_config['login_pass'],
					host_config['login_key_file']
					)

	return ssh_connections


def manage_files(command, ssh_connections):
	for host, ssh_connection in ssh_connections.items():
		if command["Command"] == "Create":
			#ssh_connection.exec_command("echo '{}' > {}".format(command.key()))
			print("echo '{}' > {}".format(command["attributes"], command["Path"]))
		elif command["Command"] == "Modify":
			#ssh_connection.exec_command("echo '{}' > {}".format(command["attributes"], command["Path"]))
			print("echo '{}' > {}".format(command["attributes"], command["Path"]))
		elif command["Command"] == "update_permissions":
			#ssh_connection.exec_command("chmode {} {}".format(command["attributes"], command["Path"]))
			print("chmode {} {}".format(command["attributes"], command["Path"]))
		elif command["Command"] == "update_owner":
			#ssh_connection.exec_command("chown {} {}".format(command["attributes"], command["Path"]))
			print("chown {} {}".format(command["attributes"], command["Path"]))
		elif command["Command"] == "Delete":
			#ssh_connection.exec_command("rm -rf {}".format(command["Path"]))
			print("rm -rf {}".format(command["Path"]))


def manage_packages(command, ssh_connections):
	pass


def manage_services(command, ssh_connections):
	pass


def switch_config_commands(config, ssh_connections):
	for unit in ["Files", "Packages", "Services"]:
		if unit == "Files":
			for file in config[unit].keys():
				for command in config[unit][file].keys():
					if command == "related_services":
						for serivce in config[unit][file][command]:
							manage_services({serivce: "Restart"}, ssh_connections)
					else:
						manage_files({"Path": file, "Command": command, "attributes": config[unit][file][command]}, ssh_connections)
		elif unit == "Packages":
			for Package, command in config[unit].items():
				if Package == "related_services":
					for serivce in config[unit][Package]:
						manage_services({serivce: "Restart"}, ssh_connections)
				else:
					manage_packages({Package: command}, ssh_connections)
		elif unit == "Services":
			for service, command in config[unit].items():
				manage_services({serivce: command}, ssh_connections)


async def config_executer(config, ssh_connections):
	uniq_ssh_connections = {}
	for host in ssh_connections.keys():
		if host in config["Hosts"].keys():
			uniq_ssh_connections[host] = ssh_connections[host]

	switch_config_commands(config, uniq_ssh_connections)


async def run_tasks(configs, ssh_connections):
	for file, config  in configs.items():
		coro = config_executer(config, ssh_connections)
		task = asyncio.create_task(coro)
		await task

configs = read_configs()
ssh_connections = setup_ssh_connections(configs)
asyncio.run(run_tasks(configs, ssh_connections))


#print(ssh_connections)
#print(configs)