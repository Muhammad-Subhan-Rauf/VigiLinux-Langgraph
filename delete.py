import subprocess
import os


shell_command = ["echo", "'RAsubdiouasbdoliujbadzsliohkuyfjbsxdcfkluijh' > /home/subhan-rauf/Desktop/subhan/rauf/sohail/texting.txt"]
result = subprocess.run("echo 'RAsubdiouasbdoliujbadzsliohkuyfjbsxdcfkluijh' > /home/subhan-rauf/Desktop/subhan/rauf/sohail/texting.txt", capture_output=True, text=True, shell=True)
print(result)



