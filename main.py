#!/usr/bin/python3

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
			ssh_connection.exec_command("sudo echo '{}' > {}".format(command["attributes"], command["Path"]))
			print("sudo echo '{}' > {}".format(command["attributes"], command["Path"]))
		elif command["Command"] == "Modify":
			ssh_connection.exec_command("sudo echo '{}' > {}".format(command["attributes"], command["Path"]))
			print("sudo echo '{}' > {}".format(command["attributes"], command["Path"]))
		elif command["Command"] == "update_permissions":
			ssh_connection.exec_command("sudo chmod {} {}".format(command["attributes"], command["Path"]))
			print("sudo chmod {} {}".format(command["attributes"], command["Path"]))
		elif command["Command"] == "update_owner":
			ssh_connection.exec_command("sudo chown {} {}".format(command["attributes"], command["Path"]))
			print("sudo chown {} {}".format(command["attributes"], command["Path"]))
		elif command["Command"] == "Delete":
			ssh_connection.exec_command("sudo rm -rf {}".format(command["Path"]))
			print("sudo rm -rf {}".format(command["Path"]))


def manage_packages(command, ssh_connections):
	for host, ssh_connection in ssh_connections.items():
		ssh_connection.exec_command("sudo apt update -y")
		print("sudo apt update -y")
		if command["Command"] == "Install":
			ssh_connection.exec_command("sudo apt install -y {}".format(command['Package']))
			print("sudo apt install -y {}".format(command['Package']))
		elif command["Command"] == "Remove":
			ssh_connection.exec_command("sudo apt remove -y {}".format(command['Package']))
			print("sudo apt remove -y {}".format(command['Package']))
		elif command["Command"] == "Update":
			ssh_connection.exec_command("sudo apt update -y {}".format(command['Package']))
			print("sudo apt --only-upgrade install -y {}".format(command['Package']))


def manage_services(command, ssh_connections):
	for host, ssh_connection in ssh_connections.items():
		if command["Command"] == "Restart":
			ssh_connection.exec_command("sudo systemctl restart {}".format(command['Service']))
			print("sudo systemctl restart {}".format(command['Service']))
		elif command["Command"] == "Reload":
			ssh_connection.exec_command("sudo systemctl reload {}".format(command['Service']))
			print("sudo systemctl reload {}".format(command['Service']))
		elif command["Command"] == "Start":
			ssh_connection.exec_command("sudo systemctl start {}".format(command['Service']))
			print("sudo systemctl start {}".format(command['Service']))
		elif command["Command"] == "Stop":
			ssh_connection.exec_command("sudo systemctl stop {}".format(command['Service']))
			print("sudo systemctl stop {}".format(command['Service']))


def switch_config_commands(config, ssh_connections):
	for unit in ["Files", "Packages", "Services"]:
		if unit == "Files":
			for file in config[unit].keys():
				for command in config[unit][file].keys():
					if command == "related_services":
						for serivce in config[unit][file][command]:
							manage_services({"Service": serivce, "Command": "Restart"}, ssh_connections)
					else:
						manage_files({"Path": file, "Command": command, "attributes": config[unit][file][command]}, ssh_connections)
		elif unit == "Packages":
			for Package, command in config[unit].items():
				if Package == "related_services":
					for serivce in config[unit][Package]:
						manage_services({"Service": serivce, "Command": "Restart"}, ssh_connections)
				else:
					manage_packages({"Package": Package, "Command": command}, ssh_connections)
		elif unit == "Services":
			for service, command in config[unit].items():
				manage_services({"Service": serivce, "Command": command}, ssh_connections)


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
