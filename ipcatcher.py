import os
stream = os.popen('hostname -I')
output = stream.read().strip()
print(output)
print(type(output))