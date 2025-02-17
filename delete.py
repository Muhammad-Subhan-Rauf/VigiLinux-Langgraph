stri = "echo /home/rauf > index.js"

parts = stri.split()  # Split into list
parts[-1] = "home/" + parts[-1]  # Modify the last element

stri = " ".join(parts)  # Join back into a string

print(stri)
