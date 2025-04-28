import openai
import sys
import os
from dotenv import load_dotenv

load_dotenv()
class GPT4:
    def __init__(self, system_prompt, temperatrue=0.0):
        openai.api_key = os.getenv("API_KEY")
        self.messages = list()
        self.temperature = temperatrue
        self.system_prompt = system_prompt
        system_message = {
            'role': 'system',
            'content': system_prompt
        }    
        self.messages.append(system_message)
    
    def print_system_message(self):
        print("System message:", self.system_prompt)
        
    def get_chat_result(self, user_prompt):
        user_message = {
            'role': 'user',
            'content': user_prompt
        }
        self.messages.append(user_message)
        
        completion_text = openai.chat.completions.create(
            model = "o1",
            # temperature = self.temperature,
            messages = self.messages
        )
        
        response = completion_text.choices[0]
        
        if response.finish_reason != 'stop':
            sys.exit(
                f'Model did not finish properly: {response.finish_reason}')
        
        gpt_message = {
            'role': 'assistant',
            'content': response.message.content
        }
        self.messages.append(gpt_message)
        
        return gpt_message['content']   
    
def main():
    model = GPT4("You are a developer testing URI resolution in HTTP server implementations. " \
    "Consider the general conditions on the structure of a valid URI based on RFC 3986 and RFC 8820." \
    "Write code that generates an exhaustive and systematic set of test URIs that violate each constraint." \
    "Keep the authority and other components of the uri separate, like {'authority': 'example.com', 'path': '/this/is/valid?q=test#section-1'}." \
    "Write all generated test cases to a file called llm_tests_3.json")
    output = model.get_chat_result(
        """
        import string 
        import json

        //Implement the following function generate_uri_test_cases(), 
        //which returns a list of malformed URIs. Include helper functions to generate invalid components.
        //Start with a valid URI and systematically generate invalid cases for each component.

        def generate_uri_test_cases():
            # Get valid and invalid components 
            //write code here

            # Helper to construct bad URIs 
            def build_test_case(component_name, bad_value, **kwargs):
                //write code here
        }
        """
    )
    # print(output)
    with open("test_generation.py", "w") as f:
        f.write(output)


if __name__ == "__main__":
    main()