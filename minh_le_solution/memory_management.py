import os
import json
from openai_api import OpenAIClient



class Memory:
    def __init__(self):
        self.code_files = {}



class ExecutionTrace:
    def __init__(self):
        self.memory = Memory()

        self.client = OpenAIClient()

        with open("examples/tool_execution_trace_1.json", "r") as f:
            self.trace_data = json.load(f)
    

    def process_all(self):
        for tool_call in self.trace_data:
            action_type = tool_call["action_type"]

            if action_type == "create_file":
                self.process_create_file(tool_call)

            if action_type == "modify_code":
                self.process_modify_code(tool_call)
            
            if action_type == "execute_command":
                self.process_execute_command(tool_call)
        
        print(self.memory.code_files)


    def process_create_file(self, tool_call):
        file = tool_call["action"]["file_path"]
        content = tool_call["action"]["content"]

        code_summary = self.summarize_code(content)

        status = tool_call["result"]["status"]
        status_explain = None
        if status == "success":
            output = tool_call["result"]["output"]
            status_explain = f"The result is: {output}."
        else:
            error = tool_call["result"]["error"]
            status_explain = f"The error is: {error}."

        context_description = tool_call["context"]["description"]
        context_reasoning = tool_call["context"]["reasoning"]

        prompt = (
            "Create a summary of no more than 1000 characters of the state of a file, "
            "given information on its creation as follows:\n"

            f"- Summary of code for creation: {code_summary}\n"
            f"- Status: {status}\n"
            f"- {status_explain}"
            f"- Context: {context_description}\n"
            f"- Context reasoning: {context_reasoning}\n"
        )

        result = self.client.get_response(prompt)
        self.memory.code_files[file] = {"data": result}


    def process_modify_code(self, tool_call):
        files = tool_call["action"]["files"]
        instructions = tool_call["action"]["instructions"]
        code = tool_call["action"]["code"]

        code_summary = self.summarize_code(code)

        status = tool_call["result"]["status"]
        status_explain = None
        if status == "success":
            output = tool_call["result"]["output"]
            status_explain = f"The result is: {output}."
        else:
            error = tool_call["result"]["error"]
            status_explain = f"The error is: {error}."

        context_description = tool_call["context"]["description"]
        context_reasoning = tool_call["context"]["reasoning"]

        for file in files:
            file_current_data = self.memory.code_files[file]["data"]

            prompt = (
                "Create a summary of no more than 1000 characters of the state of a file, "
                "given its current state and its update.\n"

                "The file's current state is:\n"
                f"{file_current_data}\n"

                "The file's update is:\n"
                f"- Instructions: {instructions}\n"
                f"- Summary of code to achieve instructions: {code_summary}\n"
                f"- Status: {status}\n"
                f"- {status_explain}"
                f"- Context: {context_description}\n"
                f"- Context reasoning: {context_reasoning}\n"
            )

            result = self.client.get_response(prompt)
            self.memory.code_files[file]["data"] = result


    def summarize_code(self, code):
        prompt = (
            "Summarize this code in English in at most 200 characters:\n"
            f"{code}"
        )

        summary = self.client.get_response(prompt)
        return summary



if __name__ == "__main__":
    execution_trace = ExecutionTrace()
    execution_trace.process_all()