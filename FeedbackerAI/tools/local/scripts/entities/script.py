import subprocess
import os
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import Optional, Dict, Any

class Script:
    
    code = None
    error = None
    output = None
    
    config = Utility.load_yaml()["local"]["scripts"]
    
    def __init__(self, parent_folder, name):
        self.parent_folder = parent_folder
        self.name = name
    
    def execute(self, command="", inputs=[], args=[]):
        exeutable_files = Utility.get_list_files(
            self.parent_folder, self.name, root_dir=os.path.join(os.getcwd(), self.config["path"]))
        if exeutable_files is not None and len(exeutable_files) == 1:
            # Build the command list
            # inputs_str = " ".join([str(input) for input in inputs])
            if not command:
                script_executable = ['python3', exeutable_files[0][0], *inputs] + args
            else:
                script_executable = ['python3', exeutable_files[0][0], command] + inputs + args
            # Run the subprocess
            try:
                result = subprocess.run(
                    script_executable, capture_output=True, text=True)
                self.output = result.stdout
                self.error = result.stderr
                self.code = result.returncode
            except subprocess.CalledProcessError as e:
                raise Exception(
                    f"Failed to run script '{exeutable_files[0]} {inputs}': {e}")
        else:
            raise Exception(
                f"No tool was found with the name '{self.name}'! Exiting...")

        Utility.log(self.output if self.code == 0 else self.error)
        if self.code == 2:
            Utility.log(f"Skipping '{self.name} {inputs}:{self.error}'...")
        if self.code == 1:
            print(f"Exiting '{self.name} {inputs}:{self.error}'...")
            raise Exception
        
        return self.output