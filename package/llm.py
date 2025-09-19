from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from tools.utilities import Utility


config = Utility.load_yaml()["llm"]

class LLMGaming:
    def __init__(self, model_name=config["model"]):
        self.__model = OllamaLLM(model=model_name)

    def generate_search_queries(self, query, number_of_results=1):
        question_llm_template = (
            "Hi! Generate a list of {number_of_results} search queries for videos about {query}  splitted by ','. Don't send me any extra details or comments."
            "Thank you!"
        )

        prompt = ChatPromptTemplate.from_template(question_llm_template)
        chain = prompt | self.__model
        result = chain.invoke({"number_of_results": number_of_results, "query": query})

        queries = result.split(',')[:number_of_results]
        if not queries or len(queries) != number_of_results:
            raise Exception(f"LLM provided unexpected response: {result}")
        return queries
    
    def get_list_games(self, genre, number_of_results):
        question_llm_template = (
            "Hi! Give me a list of size {number_of_results} with the most popular and recent {genre} games this year splitted by ','. Don't send me any extra details or comments."
            "Thank you!"
        )

        prompt = ChatPromptTemplate.from_template(question_llm_template)
        chain = prompt | self.__model
        result = chain.invoke({"number_of_results": number_of_results, "genre": genre})
        
        queries = result.split(',')[:number_of_results]
        quoted_words = [f"\"{word}\"" for word in queries]
        if not quoted_words or len(quoted_words) != number_of_results:
            raise Exception(f"LLM provided unexpected response: {result}")
        return quoted_words

    def get_trends(self, focus, genre, sources):
        question_llm_template = (
            "Hi! I need to figure out what gaming players are looking for in the future. "
            "Can you give me a list of the most desired and the most hated {focus} features the {genre} games should have? "
            "The answer should be a simple list sorted from the most mentioned to the least with keywords and without descriptions. "
            "Also insert the total number of mentions per feature and its percentage. "
            "Your sources should be {sources}. "
            "Thank you!"
        )

        prompt = ChatPromptTemplate.from_template(question_llm_template)
        chain = prompt | self.__model
        result = chain.invoke({"focus": focus, "genre": genre, "sources": sources})

        return result