import fabric
import json
import validators
import os

script_dir = os.path.dirname(__file__) 
config_dir = "config.d/"
abs_config_dir = os.path.join(script_dir, config_dir)

configs = os.listdir(abs_config_dir)
print(configs)