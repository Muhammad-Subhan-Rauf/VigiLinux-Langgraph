import subprocess

def get_network_ip_addresses():
    """
    Executes the `ip addr` command and extracts IP addresses, excluding localhost.

    Returns:
        list: A list of IP addresses.
        None: if command failed.
    """
    try:
        # Run the `ip addr` command
        result = subprocess.run(
            ["ip", "addr"],
            capture_output=True,
            text=True,
            check=True
        )
        # Extract IP addresses from the output
        lines = result.stdout.splitlines()
        ip_addresses = []
        for line in lines:
            line = line.strip()
            if line.startswith("inet "):  # Match lines with IP addresses
                ip = line.split()[1].split('/')[0]  # Extract the IP part
                if ip != "127.0.0.1":  # Exclude localhost
                    ip_addresses.append(ip)
        return ip_addresses
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None


def get_network_ip_addresses_with_pipes():
  """
    Executes the ip addr command pipeline using pipes
    and returns the IP addresses.

    Returns:
        str: The output of the pipeline, containing the IP address lines.
        None: if command failed
  """

  try:
      ifconfig_process = subprocess.Popen(['ip', 'addr'], stdout=subprocess.PIPE)
      grep_inet_process = subprocess.Popen(['grep', 'inet '], stdin=ifconfig_process.stdout, stdout=subprocess.PIPE)
      grep_v_process = subprocess.Popen(['grep', '-v', '127.0.0.1'], stdin=grep_inet_process.stdout, stdout=subprocess.PIPE)
      ifconfig_process.stdout.close()
      grep_inet_process.stdout.close()
      output, error = grep_v_process.communicate()
      if error:
          raise subprocess.CalledProcessError(returncode=1, cmd="ip addr|grep...", stderr=error)
      return output.decode()
  except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None
# Example usage
if __name__ == "__main__":
    ip_output = get_network_ip_addresses()
    if ip_output:
        print("IP Addresses:")
        print(ip_output)
    ip_output_with_pipes = get_network_ip_addresses_with_pipes()
    if ip_output_with_pipes:
        print("IP Addresses (with pipes):")
        print(ip_output_with_pipes)