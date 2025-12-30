import subprocess

with open('requirements.txt', 'r') as f:
    lines = f.readlines()

new_content = []
for line in lines:
    if 'python-dotenv>=1.0.0' not in line:
        new_content.append(line)
    if not new_content:
        new_content.append('python-dotenv>=1.0.0')

with open('requirements.txt', 'w') as f:
    f.writelines(new_content)

print('Added python-dotenv>=1.0.0 to requirements.txt')
