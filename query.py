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
            model = "gpt-4o",
            temperature = self.temperature,
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
    model = GPT4("Given the description of HTTP3 functionality, implement the relevant behaviour outlined in RFCs in the following C function.")
    output = model.get_chat_result("""
                          #include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/*
 * HTTP Priority as defined in RFC 9218.
 *   - urgency: an integer (lower values indicate higher priority)
 *   - incremental: if true, indicates the response can be sent incrementally
 */
typedef struct {
    int urgency;
    bool incremental;
} http_priority_t;

/*
 * Parse a Priority header string.
 * Expected formats include:
 *    "u=1"        (urgency = 1, incremental = false)
 *    "u=2,i"      (urgency = 2, incremental = true)
 *
 * Returns true on success; false if the header cannot be parsed.
 */
bool parse_priority_header(const char *header, http_priority_t *priority)
                                   {
                                   //implement me
                                   }
                          """)
    # print(output)
    with open("output.c", "w") as f:
        f.write(output)


if __name__ == "__main__":
    main()