import subprocess
import google.generativeai as genai
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import Graph, END, START
import ipAddress as ipComms
import os
from commands import ubuntu_commands

from langchain_groq import ChatGroq

commands_with_paths = ["echo", "cd", "ls", "cp", "mv", "rm", "rmdir", "mkdir", "touch", "find", "locate", "pwd", "basename", "dirname", "tar", "zip", "unzip", "gzip", "gunzip", "ln", "stat", "file", "chmod", "chown", "chgrp", "cat", "tac", "more", "less", "head", "tail", "diff", "cmp", "grep", "sed", "awk", "tee", "scp", "rsync", "df", "du", "mount", "umount", "export", "source"]

present_path = "/"
command_template = """Convert the following user request into a shell command, or reply 'Unsupported Command' if it cannot be executed. Split the command into multiple
        sub commands, when writing multiple commands separate each command with a && meaning command1 && command2 && command3. Do not return any cd commands
        instead use absolute paths from the home directory to the directory where the work needs to be done. Write the commands in order of execution:
        if a file or folder does not exist, make that file/folder
        User Request: {input}
        Shell Command:"""
# Configure Gemini API Key
google_api = os.getenv("GOOGLE_API_KEY")
groq_api = os.getenv("GROQ_API_KEY")




def change_dir(new_path):
    global present_path
    if os.path.isabs(new_path):
        present_path = new_path

    else:
        present_path = present_path +"/" + new_path

    print("\n\n\nUPDATED PATH: ",present_path)
# llm =ChatGroq(
#     model_name="llama-3.3-70B-versatile",
#     temperature=1,
#     groq_api_key=groq_api
# )

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api, verbose= False, temperature=0)

# Define State
class AgentState:
    def __init__(self, user_input=None, is_command=False,  shell_command=None, response=None, execution_result=None):
        self.user_input = user_input
        self.is_command = is_command

        self.shell_command = shell_command
        self.response = response
        self.execution_result = execution_result
        self.error = None

# Step 1: Determine if Input is a Command
def classify_input(state: AgentState) -> AgentState:
    # print(f"Input received: {state.user_input}")
    prompt_template = PromptTemplate(
        input_variables=["input"],
template="""
Classify whether the user's request can be accomplished through Linux command line operations.
Consider these as 'command' (even if implicit):
- File/directory operations
- System administration/configuration
- Package management
- Process/network management
- Text manipulation
- Hardware operations
- Automation/scripting tasks
- Permission/account management
- Any action requiring terminal execution

For general knowledge, conversations, or non-Linux topics, classify as 'chat'.

Input: {input}
Output (only 'command' or 'chat'):
"""
    )
    chain = prompt_template | llm
    result = chain.invoke({"input": state.user_input})
    classification = result.content.strip().lower()
    print("CLASSS: ",classification)
    state.is_command = (classification != "chat")

    print(f"Classification: {'Command' if state.is_command else  'Chat'}")
    return state

# Step 2: Process Chat Input
def handle_chat(state: AgentState) -> AgentState:
    # Handle date and time requests directly
    llm.temperature=0.7
    if "date" in state.user_input.lower():
        state.response = f"Today's date is {datetime.now().strftime('%Y-%m-%d')}."
        print(state.response)
        return state
    elif "time" in state.user_input.lower():
        state.response = f"The current time is {datetime.now().strftime('%H:%M:%S')}."
        print(state.response)
        return state

    # For other chats, ask Gemini
    prompt_template = PromptTemplate(
        input_variables=["input"],
        template="You are a helpful assistant. Respond to the following: {input}"
    )
    chain = prompt_template | llm
    result = chain.invoke({"input": state.user_input})
    state.response = result.content.strip()
    print(f"Chat Response: {state.response}")
    return state

# Step 3: Interpret Command Input
def interpret_command(state: AgentState) -> AgentState:
    llm.temperature=0
    prompt_template = PromptTemplate(
        input_variables=["input"],
        template="""
        Convert the following user request into a shell command, or reply 'Unsupported Command' if it cannot be executed. Split the command into multiple
        sub commands, when writing multiple commands separate each command with a && meaning command1 && command2 && command3. Do not return any cd commands
        instead use absolute paths from the home directory to the directory where the work needs to be done:
        User Request: {input}
        Shell Command:
        """
    )
    chain = prompt_template | llm

    max_retries = 2  # Set a maximum number of retries
    attempts = 0

    while attempts <= max_retries:
        result = chain.invoke({"input": state.user_input})
        print(result)
        command_output = result.content.strip()

        if command_output:  # Check if the command is not empty
            if command_output.lower() != "unsupported command":
                state.shell_command = command_output
                print(f"Generated Shell Command: {state.shell_command}")
                return state # Command found, return state
            else:
                state.shell_command = "Unsupported Command"
                print(f"Generated Shell Command: {state.shell_command}")
                return state # Unsupported command, return state
        else:
            attempts += 1
            print(f"Empty command received from LLM. Regenerating... (Attempt {attempts}/{max_retries + 1})")

    state.shell_command = None  # Set shell_command to None if no command after retries
    state.response = "Sorry, I couldn't generate a valid command after multiple attempts." # Inform user about failure
    print(state.response)
    return state # Return state with no command


# **NEW STEP: Check if Command is Network Related**
def check_network_command(state: AgentState) -> AgentState:
    network_commands = ["ping", "traceroute", "nslookup", "dig", "curl", "wget", "ifconfig", "ip", "ssh", "scp", "netstat"]
    if state.shell_command:
        command = state.shell_command.replace("Shell Command: ","")
        if any(cmd in command.lower().split() for cmd in network_commands):

            print("Network Command Detected")

            state.execution_result = ipComms.get_network_ip_addresses()[0]

    return state

# Step 4: Check and Install Missing Packages
def install_missing_packages(command):

    command = command.replace("Shell Command: ","")
    # print(f'\n\n\n\n\nCommand: {command}')
    # print(f'\n\n\n\n\nCommand: {command.split()[0]}')
    try:
        command = command.replace("Shell Command: ","")
        # print(f'\n\n\n\n\nCommand: {command}')
        # print(f'\n\n\n\n\nCommand first: {command.split()[0]}')
        command_lst = command.split()
        # print(f"\n\n\ncommand list: {command_lst}")
        # Check if command exists
        if command_lst[0] == "cd" or command_lst[0] in ubuntu_commands:
            return True

        out = subprocess.run(command_lst, capture_output=True, text=True)

        # print("\n\n\nOutput:", out.stdout)  # Standard output
        # print("Error:", out.stderr)  # Standard error (if any)
        # print("Return Code:", out.returncode, "\n\n\n")  # Return code of the command

        # subprocess.check_output(f"which {command.split()[0]}", shell=True, text=True)
    except subprocess.CalledProcessError:
        # print(f"Dependency missing for: {command.split()[0]}")
        # print(f"Installing {command.split()[0]}...")
        subprocess.run(f"brew install {command.split()[0]}", shell=True, check=True)

    except Exception as e:
        print(f"unexpected error occured: {e}\n\n")

def remove_before_double_slash(path: str) -> str:
    # Find the position of the double slash
    double_slash_index = path.find("//")

    # If found, return everything after it, otherwise return the original path
    return path[double_slash_index + 2:] if double_slash_index != -1 else path


# Step 5: Execute Shell Command
def execute_command(state: AgentState) -> AgentState:
    shell_command = state.shell_command
    global present_path

    if shell_command is None: # Handle the case where interpret_command returns None
        state.execution_result = "Unable to generate a valid command."
        return state

    # Remove the "Shell Command: " prefix
    shell_command = shell_command.replace("Shell Command: ", "")

    # Handle unsupported commands
    if "Unsupported Command" in shell_command:
        state.execution_result = "Command not supported or cannot be executed."
        return state

    # Check dependencies and install if missing
    install_missing_packages(shell_command)

    try:
        print(f"Executing Command: {shell_command}")

        # Split by ';' and strip spaces around each command
        commands = [shell_command]
        # if ";" in shell_command:
        #     commands = [cmd.strip() for cmd in shell_command.split(";") if cmd.strip()]
        if "&&" in shell_command:
            commands = [cmd.strip() for cmd in shell_command.split("&&") if cmd.strip()]

        all_results = []

        for cmd in commands:
            print(f"Executing Sub-Command: {cmd}")
            # cmd = cmd.replace("/home","~")
            cmd = cmd.replace("~/user","~")
            # Preprocess the shell command
            cmd = os.path.expanduser(cmd)
            cmd = os.path.expandvars(cmd)
            shell_bool = False
            # Split command if not using `shell=True`
            shell_command_list = cmd.split()
            print("THIS LIST: ",shell_command_list)
            shell_command_list[-1] = os.path.expanduser(shell_command_list[-1])
            symbols = ['|', '>', '<', '&&', '||', '$(', '`']

            if shell_command_list[0] == "echo" or any(symbol in shell_command_list for symbol in symbols):
                shell_bool = True
                shell_command_list = " ".join(shell_command_list)
                shell_command_list = shell_command_list.replace(">>",">")
            print(f"Processed Sub-Command: {shell_command_list}")
            if shell_command_list[0] == "cd":
                change_dir(shell_command_list[1])
                print("PRESENT PATH: ",present_path)
                continue
            is_abs_path = os.path.isabs(shell_command_list[1])
            if shell_command_list[0] in commands_with_paths and not is_abs_path:
                if present_path.endswith("/") and len(present_path) > 1:
                    present_path = present_path.rstrip("/")

                new_path = shell_command_list[-1]

                # Extract the last directory of the present path
                last_dir_present = os.path.basename(present_path)
                first_dir_new = os.path.basename(new_path.split("/")[0]) if "/" in new_path else new_path

                # Avoid duplicating the directory name
                if last_dir_present == first_dir_new:
                    shell_command_list[-1] = present_path + new_path[len(first_dir_new):]
                else:
                    shell_command_list[-1] = present_path + "/" + new_path

            elif isinstance(shell_command_list, str) :
                print("\n\n\n\nis instance TRUE")
                print(f"||{shell_command_list.split()[0]}||")
                if shell_command_list.split()[0] in commands_with_paths:
                    print("\n\nSPLIT ALSO TRUE")
                    if shell_bool:
                        print("\n\nSHELL BOOL TRUE")

                        if present_path.endswith("/") and len(present_path) > 1:
                            present_path = present_path.rstrip("/")

                        parts = shell_command_list.split()
                        new_path = parts[-1]

                        last_dir_present = os.path.basename(present_path)
                        first_dir_new = os.path.basename(new_path.split("/")[0]) if "/" in new_path else new_path

                        if last_dir_present == first_dir_new:
                            parts[-1] = present_path + new_path[len(first_dir_new):]
                        else:
                            parts[-1] = present_path + "/" + new_path
                        print(f"\n\n\n\n\n\n\nPARTS:   {parts}\n\n\n\n\n\n\n\n\n")
                        shell_command_list = " ".join(parts)
                        shell_command_list = remove_before_double_slash(shell_command_list)
                        print(f"\n\n\nREMMED PATH: {shell_command_list}\n\n\n")


                # shell_command_list[-1] = present_path + "/" +shell_command_list[-1]



            # Execute the
            print("CURRENT PATH IS: ",present_path)
            print("THE PATH IS ABSOLUTE T/F:",is_abs_path)
            print("WE ARE RUNNING: ",shell_command_list)
            result = subprocess.run(shell_command_list, capture_output=True, shell=shell_bool)
            print(result)

            # Handle errors and collect results
            if result.returncode != 0:
                error_msg = f"Error executing command '{cmd}': {result.stderr.strip()}"
                print(error_msg)
                all_results.append(error_msg)
            else:
                output = result.stdout
                print(f"Sub-Command Output:\n{output}")
                all_results.append(output)
            state.execution_result = all_results
        # Combine all results into a single output
        # state.execution_result = "\n".join(all_results)
    except subprocess.CalledProcessError as e:
        state.error = e
        state.execution_result = f"Error executing command: {e.output}"
        print(state.execution_result)
    except Exception as e:
        state.error = e
        state.execution_result = f"Execution failed: {str(e)}"
        print(state.execution_result)

    return state

# Step error: Respond to errors occuring
def error_management(state: AgentState) -> AgentState:
    print("FIXING ERRORS HERE PEOPLE")
    llm.temperature=0
    prompt_template = PromptTemplate(
        input_variables=["input"],
        template=f"""
        This error occured {state.error} when trying to run the command {state.shell_command}. Return an updated code
        that will run properly after fixing the errors. The return response should follow the following command template:

        {command_template}
        """
    )
    chain = prompt_template | llm
    result = chain.invoke({"input": state.user_input})
    if result.content.strip().lower() != "unsupported command":

        state.shell_command = result.content.strip()
        print(f"Generated Shell Command: {state.shell_command}")
    state.shell_command = result
    state.error = None
    return state


# Step 6: Respond to Command Execution
def generate_command_response(state: AgentState) -> AgentState:
    prompt_template = PromptTemplate(
        input_variables=["command", "result"],
        template="Explain the output in complete layman terms, and be straight to the point. : Output: {result}"
    )
    chain = prompt_template | llm
    result = chain.invoke({"result": state.execution_result})
    state.response = result.content.strip()
    # print(f"Explanation: {state.response}")
    return state

# Create LangGraph Workflow
def create_agent_graph():
    graph = Graph()
    graph.add_node("classify_input", classify_input)
    graph.add_node("handle_chat", handle_chat)
    graph.add_node("interpret_command", interpret_command)
    # NEW NODE ADDED
    graph.add_node("check_network_command",check_network_command)
    graph.add_node("execute_command", execute_command)
    graph.add_node("error_management", error_management)
    graph.add_node("generate_command_response", generate_command_response)
    graph.set_entry_point("classify_input")
    graph.add_conditional_edges(
        "classify_input",
        lambda state: "handle_chat" if not state.is_command else "interpret_command"
    )
    graph.add_edge("handle_chat", END)
    # graph.add_edge("interpret_command", "check_network_command") #connect interpret to check_network_command
    graph.add_edge("interpret_command", "execute_command") #connect interpret to check_network_command
    # graph.add_edge("check_network_command", "generate_command_response") #connect check_network to execute
    # graph.add_edge("execute_command", "generate_command_response")
    graph.add_conditional_edges(
        "execute_command",
        lambda state: "generate_command_response" if not state.error else "error_management"
    )
    graph.add_edge("error_management", "execute_command")
    graph.add_edge("generate_command_response", END)
    return graph

# Command Line Interface
def main():
    print("AI Command Line Agent (powered by Gemini) - Type 'exit' to quit.")
    graph = create_agent_graph()
    app = graph.compile()

    while True:
        try:
            print("CURRENT DIRECTORY:", present_path)
            user_input = f"The current working directory is {present_path}. user asked: " + input("You: ")
            state = AgentState(user_input=user_input)
            print("THIS STATE", state.execution_result)
            result = app.invoke(state)
            print("AI Agent:", result.response)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Check your internet and try again.")

if __name__ == "__main__":
    main()