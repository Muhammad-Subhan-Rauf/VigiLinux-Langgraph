ubuntu_commands = [
    # File and Directory Management
    "ls",            # List directory contents
    "cd",            # Change directory
    "pwd",           # Print working directory
    "mkdir",         # Make a directory
    "rmdir",         # Remove an empty directory
    "rm",            # Remove files or directories
    "cp",            # Copy files and directories
    "mv",            # Move/rename files
    "find",          # Search for files
    "locate",        # Find files by name
    "touch",         # Create an empty file
    "tree",          # Display directory structure in a tree format

    # File Viewing and Editing
    "cat",           # View file contents
    "less",          # View file contents one page at a time
    "more",          # View file contents one screen at a time
    "nano",          # Command-line text editor
    "vim",           # Advanced text editor
    "gedit",         # GUI text editor
    "head",          # View the beginning of a file
    "tail",          # View the end of a file

    # File Permissions and Ownership
    "chmod",         # Change file permissions
    "chown",         # Change file ownership
    "ls -l",         # Detailed list with permissions

    # Package Management (APT)
    "sudo apt update",        # Update the package list
    "sudo apt upgrade",       # Upgrade installed packages
    "sudo apt install",       # Install a package
    "sudo apt remove",        # Remove a package
    "sudo apt autoremove",    # Remove unused packages
    "sudo apt search",        # Search for a package
    "dpkg",                   # Debian package management

    # Process and System Monitoring
    "ps",            # Display active processes
    "top",           # Display real-time system processes
    "htop",          # Interactive process viewer
    "kill",          # Kill a process by PID
    "killall",       # Kill processes by name
    "free -h",       # Show memory usage
    "df -h",         # Show disk usage
    "du",            # Estimate file/directory sizes

    # Networking
    "ping",          # Check connectivity to a server
    "curl",          # Make HTTP requests
    "wget",          # Download files
    "ifconfig",      # Display network configuration (deprecated, use `ip`)
    "ip addr",       # Show IP addresses and interfaces
    "netstat",       # Display network connections (use `ss` instead)
    "ssh",           # Connect to a remote server
    "scp",           # Copy files to/from a remote server
    "ftp",           # Connect to an FTP server

    # System Management
    "sudo",          # Run a command as a superuser
    "whoami",        # Display current user
    "id",            # Display user ID and group ID
    "uptime",        # Show system uptime
    "uname -a",      # Display system information
    "hostname",      # Display or set the hostname
    "history",       # Show command history
    "reboot",        # Restart the system
    "shutdown",      # Shutdown the system
    "date",          # Display or set the system date/time

    # Disk and Partition Management
    "fdisk",         # Partition management
    "mount",         # Mount a filesystem
    "umount",        # Unmount a filesystem
    "lsblk",         # List information about block devices
    "blkid",         # Display block device attributes

    # User Management
    "adduser",       # Add a new user
    "deluser",       # Delete a user
    "passwd",        # Change a user's password
    "who",           # Show who is logged in
    "w",             # Show who is logged in and what they are doing

    # Archiving and Compression
    "tar",           # Archive files
    "gzip",          # Compress files
    "gunzip",        # Decompress files
    "zip",           # Compress files into a zip archive
    "unzip",         # Extract a zip archive

    # System Logs
    "dmesg",         # View kernel messages
    "journalctl",    # Query and display system logs
    "tail -f /var/log/syslog", # View live system logs

    # Miscellaneous
    "echo",          # Print a message
    "clear",         # Clear the terminal screen
    "alias",         # Create command shortcuts
    "time",          # Measure the execution time of a command
    "man",           # Display the manual for a command
    "help",          # Get help for built-in commands

    # Development Tools
    "gcc",           # GNU C Compiler
    "make",          # Build automation tool
    "python3",       # Run Python 3 scripts
    "pip3",          # Install Python packages
    "git",           # Version control
]
