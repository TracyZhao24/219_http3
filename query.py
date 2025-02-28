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
    model = GPT4("You are a C developer working on a simple implementation of HTTP3. Code up all relevant sections related to RFCs in the following C function.")
    output = model.get_chat_result(
        """
        #import <stdio>
        #import <stdlib>
        #import <string>

        //Do not use any external libraries. 
        //Implement the following function resolve_uri(), 
        //which returns a uri as a string given a base uri a relative uri as parameters. 

        char * resolve_uri(char * base_uri, char * query_uri){
            //write code here
        }
        """
    )
    # print(output)
    with open("output.c", "w") as f:
        f.write(output)


if __name__ == "__main__":
    main()