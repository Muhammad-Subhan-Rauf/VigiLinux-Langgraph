import subprocess
import google.generativeai as genai
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import MemorySaver
import ipAddress as ipComms
import os
from commands import ubuntu_commands 

present_path = "/"
command_template = """Convert the following user request into a shell command..."""  # Keep your original template

# Configure Gemini API Key
google_api = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api, verbose= False)
# Define state as dictionary instead of class
initial_state = {
    "user_input": None,
    "is_command": False,
    "shell_command": None,
    "response": None,
    "execution_result": None,
    "error": None
}

# TASK DEFINITIONS
@task
def classify_input(state: dict) -> dict:
    prompt_template = PromptTemplate(
        input_variables=["input"],
        template="""
        Is the user asking you to run a linux command line command if yes then return "command" else return "chat":
        Input: {input}
        Output (only 'command' or 'chat'):
        """
    ) # Keep your original template
    chain = prompt_template | llm
    result = chain.invoke({"input": state["user_input"]})
    classification = result.content.strip().lower()
    state["is_command"] = (classification != "chat")
    return state

@task
def handle_chat(state: dict) -> dict:
    # Handle date and time requests directly
    llm.temperature=0.7
    if "date" in state["user_input"].lower():
        state["response"] = f"Today's date is {datetime.now().strftime('%Y-%m-%d')}."
        print(state["response"])
        return state
    elif "time" in state["user_input"].lower():
        state["response"] = f"The current time is {datetime.now().strftime('%H:%M:%S')}."
        print(state["response"])
        return state

    # For other chats, ask Gemini
    prompt_template = PromptTemplate(
        input_variables=["input"],
        template="You are a helpful assistant. Respond to the following: {input}"
    )
    chain = prompt_template | llm
    result = chain.invoke({"input": state["user_input"]})
    state["response"] = result.content.strip()
    print(f"Chat Response: {state["response"]}")
    return state

@task
def interpret_command(state: dict) -> dict:
    #llm.temperature=0.1
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
    result = chain.invoke({"input": state["user_input"]})
    if result.content.strip().lower() != "unsupported command":

        state["shell_command"] = result.content.strip()
        print(f"Generated Shell Command: {state["shell_command"]}")
    return state

@task
def check_network_command(state: dict) -> dict:
    network_commands = ["ping", "traceroute", "nslookup", "dig", "curl", "wget", "ifconfig", "ip", "ssh", "scp", "netstat"]
    if state["shell_command"]:
        command = state["shell_command"].replace("Shell Command: ","")
        if any(cmd in command.lower().split() for cmd in network_commands):
        
            print("Network Command Detected")

            state["execution_result"] = ipComms.get_network_ip_addresses()[0]

    return state

@task
def execute_command(state: dict) -> dict:
    shell_command = state["shell_command"]
    
    # Remove the "Shell Command: " prefix
    shell_command = shell_command.replace("Shell Command: ", "")
    
    # Handle unsupported commands
    if "Unsupported Command" in shell_command:
        state["execution_result"] = "Command not supported or cannot be executed."
        return state

    # Check dependencies and install if missing
    # install_missing_packages(shell_command)

    try:
        print(f"Executing Command: {shell_command}")

        # Split by ';' and strip spaces around each command
        commands = [shell_command]
        if ";" in shell_command:
            commands = [cmd.strip() for cmd in shell_command.split(";") if cmd.strip()]
        if "&&" in shell_command:
            commands = [cmd.strip() for cmd in shell_command.split("&&") if cmd.strip()]

        all_results = []
        
        for cmd in commands:
            print(f"Executing Sub-Command: {cmd}")
            
            # Preprocess the shell command
            cmd = os.path.expanduser(cmd)
            cmd = os.path.expandvars(cmd)
            shell_bool = False
            # Split command if not using `shell=True`
            shell_command_list = cmd.split()
            shell_command_list[-1] = os.path.expanduser(shell_command_list[-1])
            symbols = ['|', '>', '<', '&&', '||', '$(', '`']
            if shell_command_list[0] == "echo" or any(symbol in shell_command_list for symbol in symbols):
                shell_bool = True
                shell_command_list = " ".join(shell_command_list)
                shell_command_list = shell_command_list.replace(">>",">")
            print(f"Processed Sub-Command: {shell_command_list}")

            # Execute the command
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
            state["execution_result"] = all_results
        # Combine all results into a single output
        # state["execution_result"] = "\n".join(all_results)
    except subprocess.CalledProcessError as e:
        state["error"] = e
        state["execution_result"] = f"Error executing command: {e.output}"
        print(state["execution_result"])
    except Exception as e:
        state["error"] = e
        state["execution_result"] = f"Execution failed: {str(e)}"
        print(state["execution_result"])

    return state

@task
def error_management(state: dict) -> dict:
    # Your existing error management logic
    # ...
    return state

@task
def generate_command_response(state: dict) -> dict:
    # Your existing response generation logic
    # ...
    return state

# ENTRYPOINT WORKFLOW
@entrypoint(checkpointer=MemorySaver())
def agent_workflow(user_input: str) -> dict:
    state = initial_state.copy()
    state["user_input"] = user_input
    
    # Classification step
    state = classify_input(state).result()
    
    if not state["is_command"]:
        state = handle_chat(state).result()
        print(state)
        return state
    else:
        print(state)
        state = interpret_command(state).result()
        state = check_network_command(state).result()
        
        # Execution loop with error handling
        max_retries = 3
        while max_retries > 0:
            state = execute_command(state).result()
            if not state.get("error"):
                break
            state = error_management(state).result()
            max_retries -= 1
        
        if not state.get("error"):
            state = generate_command_response(state).result()
        
        return state

# Updated CLI using streaming
def main():
    print("AI Command Line Agent (powered by Gemini) - Type 'exit' to quit.")
    
    while True:
        try:
            user_input = f"The current working directory is {present_path}. User asked: " + input("You: ")
            if user_input.lower().strip() == "exit":
                break

            for result in agent_workflow.stream(user_input, {"configurable": {"thread_id": "1"}}):
                if "response" in result:
                    print("AI Agent:", result["response"])
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        # except Exception as e:
        #     print(f"An unexpected error occurred: {e}. Check your internet and try again.")

if __name__ == "__main__":
    main()