dunder = chr(95) + chr(95)
correct = 'logging.getLogger(' + dunder + 'name' + dunder + ')'
wrong = 'logging.getLogger(name)'

with open('documents/death_verification.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(wrong, correct)

with open('documents/death_verification.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('documents/death_verification.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(repr(lines[15]))