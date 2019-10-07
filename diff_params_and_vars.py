import re
import sys

input = raw_input("input the two paths separated by a comma: ")
input = input.split(",")
for i in range(len(input)):
    input[i] = input[i].strip()
file1 = open(input[0]) # bells.tacobell.com/src/templates/directory/citylist.soy
file2 = open(input[1]) # locations.tacobell.com/src/templates/directory/citylist.soy
file1_params = []
file1_let_vars = []
file2_params = []
file2_let_vars = []


#scrape params from first file
postTemplate = False
for line in file1:
    if 'template' in line:
        postTemplate = True
        continue
    if not postTemplate:
        line.strip()
        try:
            found = re.search('@param?\?? ([^\s]+)', line).group(1)
        except AttributeError:
            found='none'
        if found != 'none':
            file1_params.append(found)
    else:
        try:
            found = re.findall('\$([^\s]+)', line)
        except AttributeError:
            found='none'
        if len(found) > 0 and found[0] != 'none':
            file1_let_vars += found

#scrape params from second file
postTemplate = False
for line in file2:
    if 'template' in line:
        postTemplate = True
        continue
    if not postTemplate:
        line.strip()
        try:
            found = re.search('@param?\?? ([^\s]+)', line).group(1)
        except AttributeError:
            found='none'
        if found != 'none':
            file2_params.append(found)
    else:
        try:
            found = re.findall('\$([^\s]+)', line)
        except AttributeError:
            found='none'
        if len(found) > 0 and found[0] != 'none':
            file2_let_vars += found


file1_params.sort()
file2_params.sort()
file1_exclusive_params = list(set(file1_params) - set(file2_params))
file2_exclusive_params = list(set(file2_params) - set(file1_params))

print('')
print("params exlusive to " + str(input[0]) + ": \n")
for i in file1_exclusive_params:
    print(i)
print('')
print("params exlusive to " + str(input[1]) + ": \n")
for i in file2_exclusive_params:
    print(i)

print('\n')
print('variables used in ' + str(input[0]) + ": \n")
for i in file1_let_vars:
    print(i.strip("}").strip(":").strip(","))
print('')
print('variables used in ' + str(input[0]) + ": \n")
for i in file2_let_vars:
    print(i.strip("}").strip(":").strip(","))
#tot_diff = list(set(file1_params) - set(file2_params)) + list(set(file2_params) - set(file1_params))
#any_special_char [!@#$%^&*(),.?":{}|<>]