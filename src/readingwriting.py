with open('log.txt', 'w') as outfile:
    outfile.write("Some line")
    outfile.write("Some new line\n")
    outfile.write("Some more new line\n")

with open('log.txt', 'r') as infile:
    readdate = infile.read()

print(readdate)