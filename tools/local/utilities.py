import yaml
import os
import isodate
from datetime import datetime, timezone
import cv2
import numpy as np
import re
import json
import ast
from typing import Optional, Dict, Any, List, Set
import importlib
import inspect
from collections import defaultdict
from innovation.FeedbackerAi.tools.local.logger.logger import LoggerFactory
from innovation.FeedbackerAi.tools.models.entities.video import VideoAnswer, ClassifiedLabel
from innovation.FeedbackerAi.tools.models.entities.video import VideoQuestion
from innovation.FeedbackerAi.agents.entities.component import Answer, Question
from abc import ABC




class Utility:
    
    # Globals
    class GLOBALS(ABC):
        question = None
        video_filename = None
        genre = None
        focus = None
        platforms = None
        sources_types = None
    
    # MISC #
    
    @staticmethod
    def calculate_score(to_have_trends: List, not_to_have_trends: List, formula_config):
        
        max_score = 0
        min_score = 0
        score = 0
        
        # Add weights for positive features
        for trend in to_have_trends:
            weight = formula_config.get(trend.feature_type.value, 0)
            max_score += weight
        
        # Subtract weights for negative features
        for trend in not_to_have_trends:
            weight = formula_config.get(trend.feature_type.value, 0)
            min_score += weight
        
        # Handle case where max_score == min_score to avoid division by zero
        if max_score == min_score:
            return 0
        
        # Convert to percentage in range 0-100%
        score = max_score - min_score
        percentage = ((score - min_score) / (max_score - min_score)) * 100
        return percentage
            
        
    
    @staticmethod
    def answer_to_review(answer: Answer):
        from innovation.FeedbackerAi.tools.local.entities.review import Review
        review = Review(
            text=answer.text,
            source_type=answer.metadata["source_type"] if "source_type" in answer.metadata is not None else None,
            genre=Utility.GLOBALS.genre,
            platform=answer.metadata["platform"] if "platform" in answer.metadata is not None else None,
            focus=Utility.GLOBALS.focus
        )
        return review
    
    @staticmethod
    def answer_to_trend(answer: Answer):
        from innovation.FeedbackerAi.tools.local.entities.review import Trend
        trend = Trend(
            name=answer.text,
            # feature_type=FEATURE_TYPE[answer.metadata["feature_type"]] if "feature_type" in answer.metadata is not None else None
        )
        return trend
    
    @staticmethod
    def get_globals():
        return Utility.GLOBALS
    
    @staticmethod
    def log(message, is_debug = True):
        if is_debug:
            LoggerFactory.logger.debug(message)
        else:
            LoggerFactory.logger.info(message)
    
    @staticmethod
    def call_lambda(method_to_call, method_args=None):
        content = None
        if method_args is None:
            # Call method without arguments
            content = method_to_call()
        elif isinstance(method_args, (list, tuple)):
            # Unpack multiple arguments
            content = method_to_call(*method_args)
        else:
            # Single argument
            content = method_to_call(method_args)
        return content            
            
    @staticmethod
    def show_image(video_frame, model_results: List[dict]):
       # Step 1: Convert to NumPy array
        np_image = video_frame.detach().cpu().numpy()

        # Step 2: Rearrange axes from (C, H, W) to (H, W, C)
        np_image = np.transpose(np_image, (1, 2, 0))

        # Step 3: Normalize or scale pixel values if necessary
        # If tensor values are in range [0,1], scale to [0,255]
        # np_image = np.clip(np_image * 255, 0, 255).astype(np.uint8)

        # # Step 4: Convert RGB to BGR for OpenCV
        # np_image_bgr = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        np_bgr = cv2.cvtColor(np_image.astype(np.uint8), cv2.COLOR_RGB2BGR)

        # Iterate over detections
        if model_results:
            for idx, model_result in enumerate(model_results):
                label_name = model_result["label"]
                confidence = model_result["score"]
                image_text = f"{label_name}: {confidence:.2f}"
                if "debug_box" in model_result and model_result["debug_box"]:
                    # Draw bounding box
                    xmin, ymin, xmax, ymax = map(int, model_result["debug_box"])

                    # Draw rectangle
                    cv2.rectangle(np_bgr, (xmin, ymin),
                                (xmax, ymax), (0, 255, 0), 2)
                    cv2.putText(np_bgr, image_text, (xmin, ymin - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                else:
                    # Get image dimensions
                    height, width = np_bgr.shape[:2]

                    # Calculate center position
                    x = 10
                    y = height - 10
                    cv2.putText(np_bgr, image_text, (x,y-(10*idx)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
        else:
            # Get image dimensions
            height, width = np_bgr.shape[:2]

            # Calculate center position
            x = width // 2
            y = height // 2
            cv2.putText(np_bgr, "No detections!", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Show the image
        cv2.imshow('Detections', np_bgr)
        key_pressed = cv2.waitKey(5000)

        return key_pressed

    @staticmethod
    def is_object_instance_of(obj, class_name, namespace=None):
        # Get class object from the string
        cls = namespace.get(class_name) if namespace is not None else globals().get(class_name)

        if cls:
            if isinstance(obj, cls):
                return True
            else:
                return False
        else:
            raise Exception("No class found!")

    @staticmethod
    def get_list_by_column(matrix, column_idx):
        return [row[column_idx] for row in matrix]
    
    @staticmethod
    def get_list_tuples_with_max_value(list1, list2, param_match_index, param_max_index):
        # # Create a set of field values from list1
        # set1 = {t[param_match_index] for t in list1}
        # # Create a set of field values from list2
        # set2 = {t[param_match_index] for t in list2}
        # # Find common field values
        # common_values = set1.intersection(set2)
        
        # # Filter tuples in list1 that match the common values
        # intersected_list1 = [t for t in list1 if t[param_match_index] in common_values]
        # # Filter tuples in list2 that match the common values
        # intersected_list2 = [t for t in list2 if t[param_match_index] in common_values]
        
        max_elements = {}
        combined_list = list1 + list2
        for item in combined_list:
            key = item[param_match_index]
            if key not in max_elements or item[param_max_index] > max_elements[key][param_max_index]:
                max_elements[key] = item

        # Extract the results as a list
        return list(max_elements.values())
    
    # STRING #
    
    @staticmethod
    def substring_from_char(s, char, is_last=False):
        if not is_last:
            pos = s.find(char)
        else:
            pos = s.rfind(char)

        if pos != -1:
            # Get substring after the character
            substring = s[pos+1:]
            return substring
        else:
            return s
    
    @staticmethod
    def substring_until_char(s, char):
        pos = s.find(char)
        
        if pos != -1:
            return s[:pos]
        else:
            return s

    @staticmethod
    def substring_between_strings(s, before, after, is_last_string = False):
        return Utility.substring_until_char(Utility.substring_from_char(s, before, is_last_string), after)
    
    @staticmethod
    def find_json_from_text(text):
        match = re.search(r'\{.*\}', text)
        if match:
            json_str = match.group()
            try:
                data = json.loads(json_str)
                return data
            except json.JSONDecodeError:
                return None
        else:
            return None
        
    @staticmethod
    def to_camel_case(s):
        """
        Examples:
        print(to_camel_case("hello_world"))        # helloWorld
        print(to_camel_case("convert to Camel Case"))  # convertToCamelCase
        print(to_camel_case("this-is-a-test"))     # thisIsATest
        """
        
        words = re.split(r'[\s_\-]+', s)
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    @staticmethod
    def to_pascal_case(s):
        """
        Examples:
        print(to_pascal_case("hello world"))          # HelloWorld
        print(to_pascal_case("convert_to-pascal case"))  # ConvertToPascalCase
        print(to_pascal_case("this-is-a-test"))      # ThisIsATest
        """
        words = re.split(r'[\s_\-]+', s)
        return ''.join(word.capitalize() for word in words)
    
    @staticmethod
    def intersect_lists_by_strings(list1, list2):
        """
        Returns a set of strings that are present in both lists.
        
        Args:
            list1 (list): The first list of strings.
            list2 (list): The second list of strings.
        
        Returns:
            set: A set of strings that are present in both lists.
        """
        return set(list1) & set(list2)
    
    @staticmethod
    def get_unique_answers_by_field(answers: List[Answer], field: str):
        seen_values = set()
        unique_objects = []

        for obj in answers:
            if field != "text":
                value = obj.metadata[field]
            else:
                value = obj.text
            if value not in seen_values:
                seen_values.add(value)
                obj.metadata["count"] = 1
                unique_objects.append(obj)
            else:
                unique_obj = next((obj for obj in unique_objects if obj.metadata[field] == value or
                                   obj.text == value), None)
                unique_obj.metadata["count"] += 1
        return unique_objects

    # DATE/TIME #
    
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
    
    # CONVERTERS #
    
    @staticmethod
    def merge_dict_values_to_list(dict: Dict[Any, Any]):
        merged = []
        for d in dict.values():
            merged.extend(d)
        return merged
    
    @staticmethod
    def merge_list_of_dicts(dicts: List[Dict[Any, Any]]) -> Dict[Any, List[Any]]:
        merged = defaultdict(list)
        for d in dicts:
            for key, value in d.items():
                merged[key].append(value)
        return dict(merged)
    
    @staticmethod
    def dict_values_to_string(input_dict):
        values = input_dict.values()
        string_values = [str(value) if value is not None else "" for value in values]
        result = ','.join(string_values)
        return result
    
    @staticmethod
    def composite_to_dict(obj):
        if isinstance(obj, dict):
            return {k: Utility.composite_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Utility.composite_to_dict(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return Utility.composite_to_dict(vars(obj))
        else:
            return obj
        
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
    def class_attrs_to_dict(obj):
        return {k: v for k, v in obj.__dict__.items() if v not in [None, [], {}, ()]}
    
    @staticmethod
    def class_attrs_to_str(obj):
        """
        Returns
        {
            'attr1': '[1, 2, 3]',
            'attr2': '42',
            'attr3': '{\"child_attr1\": \"child_val1\"}',
            'attr4': 'true'
        }
        """
        return {
            k: json.dumps(v) for k, v in obj.__dict__.items()
            if v not in [None, [], {}, ()]
        }
    
    @staticmethod
    def list_of_dict_to_str(list_of_dicts):
        """
        Returns 
                dict1.param1, dict1.param2
                dict2.param1, dict2.param2
                dict3.param1, dict3.param2
        """
        return "\n".join([Utility.dict_to_str(d) for d in list_of_dicts])
                             
    @staticmethod
    def dict_to_str(d):
        """
        Returns dict1.param1, dict1.param2
        """
        return ', '.join(f"{key}: {value}" for key, value in d.items() if key)
    
    @staticmethod
    def str_to_dict(s):
        # Use regex to extract key and value
        match = re.match(r"(\w+):\s*(\[.*\])", s)

        if match:
            key = match.group(1)
            list_str = match.group(2)
            # Convert string to list
            value_list = ast.literal_eval(list_str)
            # Create dictionary
            return {key: value_list}
        else:
            raise Exception("String format is not as expected.")
                    
    @staticmethod
    def files_to_dict(folder_path):
        files_dict = {}
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                topic = Utility.substring_until_char(filename, ".")
                files_dict[topic] = None
        return files_dict
    
    # FILE #
    
    @staticmethod
    def get_filename_from_path(file_path):
        return Utility.substring_between_strings(file_path, "/", ".", is_last_string=True)

    @staticmethod
    def get_project_directory(file_path=""):
        return os.path.join(os.getcwd(), file_path)
    
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
    def find_maps_with_key(data, target_key):
        """
        Recursively search for all dictionaries containing target_key.
        Returns a list of all matching dictionaries.
        """
        results = []

        if isinstance(data, dict):
            if target_key in data:
                results.append(data)
            for v in data.values():
                results.extend(Utility.find_maps_with_key(v, target_key))
        elif isinstance(data, list):
            for item in data:
                results.extend(Utility.find_maps_with_key(item, target_key))
        return results        

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
            Utility.log(f"Removed file {file_path}")
        except FileNotFoundError as e:
            print(f"The file '{file_path}' does not exist.")
            raise e
        except PermissionError as e:
            print(
                f"You do not have permission to delete this file '{file_path}'.")
            raise e

    @staticmethod
    def create_file_from_path(file_path, content=""):
        """
        Creates a file at the specified path, creating any necessary directories.

        Args:
            file_path (str): The full path to the file to be created.
            content (str, optional): The content to write to the file. Defaults to empty string.

        Returns:
            str: The path of the created file, or None if an error occurred.
        """
        try:
            # Extract directory from the file path
            directory = os.path.dirname(file_path)
            # Create directories if they don't exist
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            # Create and write to the file
            with open(file_path, "w") as f:
                f.write(content)
            Utility.log(f"Created file {file_path}")
            return file_path
        except Exception as e:
            print(f"Error creating file: {e}")
            return None
        
    @staticmethod    
    def append_to_file(file_path, new_content):
        """
        Append new content to an existing file.

        Args:
            file_path (str): The path to the file.
            new_content (str): The content to append to the file.
        """
        try:
            with open(file_path, "a") as f:
                f.write("\n"+new_content)  # Adds a new line after the content
            Utility.log(f"Content appended to {file_path}")
        except Exception as e:
            raise Exception(f"Error appending to file: {e}")
    
    @staticmethod
    def read_data_from_file(file_path, ignore_timetamps=True):
        """
        Reads data from a file.

        Args:
            file_path (str): Path to the file containing the data.

        Returns:
            The contents of the file as a string.
        """
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        filtered_lines = []
        try:
            with open(file_path, 'r') as f:
                if not ignore_timetamps:
                    return [line.rstrip('\n') for line in f]
                for line in f:
                    if re.search(timestamp_pattern, line):
                        continue  # Skip lines with timestamp
                    filtered_lines.append(line.rstrip('\n'))
                return filtered_lines
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        
    @staticmethod
    def read_json_from_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    @staticmethod
    def write_json_to_file(file_path, data):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file)
        return file_path
            
    @staticmethod
    def does_file_exist(file_path, has_content=False):
        if not isinstance(file_path, str):
            raise TypeError(f"file_path '{file_path}' must be a string")
        file_exists = os.path.exists(file_path)
        if has_content and file_exists:
            with open(file_path, 'r') as f:
                content = f.read()
                if not content:
                    return False
        return file_exists

    @staticmethod
    def get_list_files(main_dir, name="", root_dir=os.getcwd(), is_dir=False):
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
    
    # REFLECTION #        
    @staticmethod
    def create_class(module_name: str, class_name: str) -> object:
        # Import the module
        module = importlib.import_module(module_name)

        # Get the class from the module
        cls = getattr(module, class_name, None)
        
        if cls is not None:
            return cls
        else:
            raise Exception(f"Reflection failed - Module '{module_name}' Class '{class_name}' not found.")
        
    @staticmethod
    def create_instance(module_name: str, class_name: str) -> object:
        # Import the module
        module = importlib.import_module(module_name)

        # Get the class from the module
        cls = getattr(module, class_name, None)
        
        if cls is not None:
            return cls()
        else:
            raise Exception(f"Reflection failed - Module '{module_name}' Class '{class_name}' not found.")
        

