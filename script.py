
# import OS
import os
import csv
from datetime import datetime, timedelta
import subprocess
from zipfile import ZipFile

def convert_time(time):
  """
  Input: 'DDDDD MMMMM DD,YYYY H:MM AM/PM GMT'
  Output: 'MM/DD/YYYY HH:MM:SS' (PDT)

  Example:
  Input: 'Saturday January 15,2022 7:31 PM GMT'
  Output: '01/15/2022 12:31:00'
  """
  # Parse the input time string using the datetime.strptime method
  dt = datetime.strptime(time, '%A %B %d,%Y %I:%M %p GMT')
  # Convert the GMT time to PDT by subtracting 7 hours
  dt = dt - timedelta(hours=7)
  # Format the output time string in the required format
  return dt.strftime('%m/%d/%Y %H:%M:%S')


def inject_meta(folder):
  """
  Input: An extracted zip folder path (no backslashes)
  Output: In place injects the metadata of the photos contained witin the folder

  Example:
  inject_meta('/Users/luiscermeno/Desktop/data/iCloud Photos Part 34 of 34')
  """

  print(f'Injecting metadata to {folder}')
  # Read the data from cvs database
  print('Reading data from Photo Library.csv...')
  data = open(folder + '/Photos/' + 'Photo Details.csv')
  csvreader = csv.reader(data)
  # Extract field names and create dictionary
  headers = []
  headers = next(csvreader) # reads row and advances to next row
  # Extract records
  metadata = {} #{FILENAME: {metadata for file}}
  for row in csvreader:
    mp = {}
    for i in range(1, len(row)):
      mp[headers[i]] = row[i]
    metadata[row[0]] = mp
  data.close()
  print('Data read successfully')

  # Make the list of commands to run
  folder = folder.replace(' ', '\\ ') # Reset back to terminal format (with back slashes to construct commands)
  commands = []
  for f in metadata.keys():
    time = convert_time(metadata[f]['originalCreationDate'])
    commands.append(f"SetFile -d '{time}' {folder}/Photos/{f}")

  # Run each command
  print('Rewriting metadata...')
  for command in commands:
      # Execute process
      process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
      # Capture output and possible error
      output, error = process.communicate()
      if process.returncode != 0:
          print(f"Error running command '{command}': {error}")
          break
  print('Metadata injected sucessfully!')

  
root = r''
while len(root) == 0:
  print('Please enter the address where your zip files are.')
  print('(You can also drag and drp the folder)')
  root = input('ADDRESS: ')
  print('\n')
root = root.strip()
root = root.replace('\\ ', ' ') # Get rid of backslashes characters to avoid issues with listdir

# Get all filenames ignoring hidden files
print(f'Reading zip files from {root}...')
zips = []
for x in os.listdir(root):
  if not x.startswith('.') and not x.endswith('.py') and not x.endswith('.csv'):
        zips.append(root + '/' + x)
print('Zip files read successfully')
print(zips)

# For each zip file:
for i,z in enumerate(zips):
  print(f'Extracting from {z}...')
  # Extract zip
  with ZipFile(z) as zObject:
    zObject.extractall(path = root)
  # Inject metadata to zip
    inject_meta(z.replace('.zip',''))
