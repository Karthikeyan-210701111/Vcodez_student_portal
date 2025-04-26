# generate_requirements.py
import subprocess

# Run pip freeze and write output to requirements.txt
with open('requirements.txt', 'w') as f:
    subprocess.run(['pip', 'freeze'], stdout=f, check=True)

print('requirements.txt has been generated.')
