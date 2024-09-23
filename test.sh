#!/bin/bash

# Function to execute a command in the background
execute_command() {
    command_to_execute=$1
    port=$2
    $command_to_execute $port &
}

# Define the port variable
port=$1
python="python3"
# List of commands to execute
commands=(
    "$python client.py $port example.com. A 5"
    "$python client.py $port example.com. A 1"
    "$python client.py $port bar.example.com. CNAME 5"
    "$python client.py $port . NS 5"
    "$python client.py $port bar.example.com. A 5"
    "$python client.py $port foo.example.com. A 5"
    "$python client.py $port example.org. A 5"
    "$python client.py $port example.org. CNAME 5"
    "$python client.py $port example.org. NS 5"
    "$python client.py $port www.metalhead.com. A 5"
    # Add more commands here
)

# Loop through the commands and execute them in parallel
for command in "${commands[@]}"; do
    execute_command "$command"
    echo "Command $command"
done

# Wait for all background processes to finish
wait
