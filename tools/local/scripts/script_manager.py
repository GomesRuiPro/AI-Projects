from abc import ABC
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.local.scripts.entities.cached_script import CachedScript
from innovation.FeedbackerAi.tools.local.scripts.entities.script import Script
from typing import Optional, Dict, Any, List

class ScriptManager(ABC):
    
    cache_enabled=True
    memento_enabled=False          

    @staticmethod
    def change_video_codec(video_path):
        
        video_converted_path = Utility.rename_file(video_path, "converted")

        script = Script("internal", "video_codec_converter")
        
        inputs = [video_path]
        args = ["--output_path=" + video_converted_path]
        script.execute("", inputs, args)

        if script.code != 0:
            video_converted_path = video_path
        return video_converted_path
    
    @staticmethod
    def scrappe_url(webpage, max_results=1):
        from innovation.FeedbackerAi.tools.sources.source import Webpage
        
        args = ["--max_results=" + str(max_results)]
            
        ui_component_parent = None
        ui_component: Webpage.Component = webpage.ui_component
        if ui_component.is_composite():
            ui_component_parent: Webpage.Branch = webpage.ui_component
            ui_component: Webpage.Leaf = ui_component_parent.child
        else:
            ui_component: Webpage.Leaf = webpage.ui_component
            
        ui_component_args = Utility.dict_values_to_string(ui_component.tags)      
        
        args.extend([
                "--type_to_fetch=" + ui_component.type_to_fetch,
                "--attr_to_fetch=" + ui_component.attr_to_fetch,
                "--filter=" + ui_component_args             
                ])
        
        if ui_component_parent:
            ui_component_parent_args = Utility.dict_values_to_string(ui_component_parent.tags)    
            args.append("--parent_filter=" + ui_component_parent_args)
            
        script = Script("internal", "web_scrapper")      
        if ScriptManager.cache_enabled:
            main_topic = Utility.substring_until_char(webpage.domain, ".")
            sub_topic = webpage.resource.replace("/", "_")
            topic = f"{main_topic}_{sub_topic}"
            script = CachedScript("internal", "web_scrapper", topic, ScriptManager.memento_enabled)
        inputs = [webpage.domain, webpage.resource]
        script.execute("", inputs, args)
        
        # if not script.output:
        #     raise Exception("No results were found from the url scrapping!")
        
        
        return script.output
    
    @staticmethod
    def download_video(searchText, clip_resolution, clip_duration_seconds, games_per_genre_length, clip_uploaded_days_ago, output_path):
        script = Script("apis", "youtube_api")
        command = "download"  
        inputs = [searchText]
        args =  ["--resolution=" + clip_resolution,
                    f"--max_results=" +
                    str(games_per_genre_length),
                        "--max_duration=" +
                    str(clip_duration_seconds),
                        "--uploaded_days_ago=" +
                    str(clip_uploaded_days_ago),
                        "--output_path=" + output_path]
        return script.execute(command, inputs, args)
        
    @staticmethod
    def get_video_comments(searchText, clip_resolution, clip_duration_seconds, games_per_genre_length, clip_uploaded_days_ago, output_path):
        pass
    
    @staticmethod
    def translate_text(list_text: List[str], trg_lang='en'):
        LIST_SEPARATOR = '[;]'
        is_batching = False
        text = list_text
        
        args =  ["--trg_lang=" + trg_lang]
        if isinstance(list_text, List) and len(text) > 1:
            is_batching = True
            args.append("--list_separator=" + LIST_SEPARATOR)
            text = LIST_SEPARATOR.join(list_text)
        
        script = Script("apis", "google_translator_api")
        command = "translate"  
        inputs = [text]
        translated_text = script.execute(command, inputs, args)
        
        if is_batching:
            translated_text = translated_text.split(LIST_SEPARATOR)
            
            if len(translated_text) != len(list_text):
               raise Exception("The comments are not the same size after translation!")
           
        return translated_text
        