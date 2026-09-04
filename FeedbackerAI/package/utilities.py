import yaml
import os
import subprocess
import isodate
from datetime import datetime, timezone

class Utility:

    @staticmethod
    def format_list_tuples_to_string(list, columns_names, columns_metrics):
        result = ""
        for list_idx in range(len(list)):
            result += "\n"
            for column_idx in range(len(columns_names)):
                result += f" {columns_names[column_idx]}: {list[list_idx][column_idx]}{columns_metrics[column_idx]}, "
            result = result[:-2]
        return result


    @staticmethod
    def get_list_by_column(matrix, column_idx):
        return [row[column_idx] for row in matrix]

    @staticmethod
    def str_to_datetime(date_str, format_str="%Y-%m-%dT%H:%M:%SZ"):
        dt = datetime.strptime(date_str, format_str)
        return dt.replace(tzinfo=timezone.utc)
    
    @staticmethod
    def datetime_to_str(dt, format_str="%Y-%m-%d %H:%M:%S"):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime(format_str)

    @staticmethod
    def iso_duration_to_seconds(duration):
        # Parse ISO 8601 duration to timedelta
        td = isodate.parse_duration(duration)
        return int(td.total_seconds())

    @staticmethod
    def load_yaml():
        yaml_file = os.path.join(os.getcwd(), "config.yaml")
        try:
            with open(yaml_file, 'r') as file:
                data = yaml.safe_load(file)
            return data
        except FileNotFoundError:
            print(f"Error: YAML file '{yaml_file}' not found.")
            return None
        except yaml.YAMLError as e:
            print(f"Error loading YAML file '{yaml_file}': {e}")
            return None
    
    @staticmethod
    def rename_file(file_path, extra, is_to_rename=False):
        # Separate the filename and extension
        base_name, ext = os.path.splitext(file_path)

        # Create the new filename with extra string before the extension
        new_path = f"{base_name}_{extra}{ext}"

        # Rename the file
        if is_to_rename:
            os.rename(file_path, new_path)
        return new_path
    
    @staticmethod
    def remove_file(file_path):
        try:
            os.remove(file_path)
        except FileNotFoundError as e:
            print(f"The file '{file_path}' does not exist.")
            raise e
        except PermissionError as e:
            print(f"You do not have permission to delete this file '{file_path}'.")
            raise e
        
    @staticmethod
    def does_file_exist(file_path):
        if not isinstance(file_path, str):
            raise TypeError(f"file_path '{file_path}' must be a string")
        return os.path.exists(file_path)

    @staticmethod
    def get_list_files(main_dir, name = "", root_dir=os.getcwd(), is_dir=False):
        files = []
        for class_idx, class_dir in enumerate(os.listdir(root_dir)):
            if class_dir in main_dir:
                class_path = os.path.join(root_dir, main_dir)
                if (is_dir):
                    for file_idx, filename in enumerate(os.listdir(class_path)):
                        filename_path = os.path.join(class_path, filename)
                        if os.path.isfile(filename_path):
                            files.append((filename_path, file_idx))
                else:
                        for filename in os.listdir(class_path):
                            filename_path = os.path.join(class_path, filename)
                            if name in filename and os.path.isfile(filename_path):
                                files.append((filename_path, class_idx))
                                break
                break
        return files
    
    @staticmethod
    def change_video_codec(video_path):
        video_converted_path = Utility.rename_file(video_path, "converted")
        code, output, error = Utility.__call_executable_tool(
            "local", 'video_codec_converter', video_path, ["--output_path=" + video_converted_path]
         )

        if code != 0:
            video_converted_path = video_path
        return video_converted_path
    
    @staticmethod
    def download_video(searchText, clip_resolution, clip_duration_minutes, games_per_genre_length, clip_uploaded_days_ago, output_path):
        code, output, error = Utility.__call_executable_tool("apis",
                    'video_downloader', searchText,
                    ["--resolution=" + clip_resolution,
                     f"--max_results=" + str(games_per_genre_length),
                     "--max_duration=" + str(clip_duration_minutes),
                     "--uploaded_days_ago=" + str(clip_uploaded_days_ago),
                     "--output_path=" + output_path]
                )
        
    @staticmethod
    def __call_executable_tool(parent_folder, name, input="", args=[]):
        exeutable_files = Utility.get_list_files(parent_folder, name, root_dir=os.path.join(os.getcwd(), "tools"))
        if exeutable_files is not None and len(exeutable_files) == 1:
            # Build the command list
            command = ['python3', exeutable_files[0][0], input] + args
            # Run the subprocess
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                output = result.stdout
                error = result.stderr
                code = result.returncode
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to run script '{exeutable_files[0]} {input}': {e}")
        else:
            raise Exception(f"No tool was found with the name '{name}! Exiting...")
        
        print(output if code == 0 else error)
        if code == 2:
            print(f"Skipping '{name} {input}'...")
        if code == 1:
            print(f"Exiting '{name} {input}'...")
            raise Exception
        return code, output, error
        
        
