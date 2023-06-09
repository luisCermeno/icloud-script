
# import OS
import os
import csv
from datetime import datetime, timedelta
import subprocess
from zipfile import ZipFile
import shutil

"""
iCloud Photo Library Extraction Tool
Author: Luis Cermeno
Date of release: 04/12/2023
"""
shared = [0]

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
  # Add Photos subfolder (this is the way Apple delivers data as of April 2023)
  folder = folder + '/Photos'
  print(f'Injecting metadata to {folder}.')

  # Get all csv databases ignoring hidden files
  print(f'Reading csv files from {folder}...')
  csvs = []
  for x in os.listdir(folder):
    if x.endswith('.csv'):
          csvs.append(folder + '/' + x)
  print('Csvs files read successfully')

  # Read the data from each database
  metadata = {} #{FILENAME: {metadata for file}}
  for database in csvs:
    print(f'Reading data from {database}')
    # Open database
    data = open(database)
    csvreader = csv.reader(data)
    # Extract field names
    headers = []
    headers = next(csvreader) # reads row and advances to next row
    # Extract records
    for row in csvreader:
      # Create entry
      mp = {}
      for i in range(1, len(row)):
        mp[headers[i]] = row[i]
      metadata[row[0]] = mp
    # Close database
    data.close()
  print('Data read successfully')

  # Make the list of commands to run
  folder = folder.replace(' ', '\\ ') # Reset back to terminal format (with back slashes to construct commands)
  commands = []
  for f in metadata.keys():
    time = convert_time(metadata[f]['originalCreationDate'])
    commands.append(f"SetFile -d '{time}' {folder}/{f}")

  # Run each command
  print('Rewriting metadata...')
  for command in commands:
      # Execute process
      process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
      # Capture output and possible error
      output, error = process.communicate()
      if process.returncode != 0:
          print(f"Error running command '{command}': {error}")
  print('Metadata injected sucessfully!')

def move_shared(source, destination):
  """
  Moves all shared albums (zips) from source to destination.
  """
  for f in os.listdir(source):
    if f.endswith('.zip'):
      print(f'Found shared album. Moving from {source} to {destination}')
      shared[0] += 1
      # Construct source and destination paths
      this_source = source + '/' + f
      this_destination = destination + '/' + f.replace('.zip',f'{str(shared[0])}.zip')
      # Move the file
      shutil.move(this_source, this_destination)

def move_photos(source, destination):
  """
  Moves all photos from source to destination.
  """ 
  source = source + '/Photos'
  print(f'Moving photos from {source} to {destination}')
  # Read files
  for f in os.listdir(source):
    if not f.startswith('.') and not f.endswith('.csv'):
      # Construct source and destination paths
      this_source = source + '/' + f
      this_destination = destination + '/' + f
      # Move the file
      shutil.move(this_source, this_destination)

def move_folder(folder, destination):
  """
    Moves folder to destination
  """
  shutil.move(folder, destination, copy_function = shutil.copytree)

def main():
  intro = 'Thank you for using the iCloud Photo Library Extraction Tool\nAuthor: Luis Cermeno\nDate of release: 04/12/2023\n'
  print(intro)
  root = ''
  while len(root) == 0:
    print('Please enter the folder path that contain your zip files.')
    print('(You can also drag and drop the folder below, and then hit Enter)')
    root = input('> ')
    print('\n')
  root = root.strip() # Get rid of trailing whitespaces
  root = root.replace('\\ ', ' ') # Get rid of backslash characters to avoid issues with listdir

  destination = ''
  while len(destination) == 0:
    print('Please enter the destination path where you want your photos to be collected.')
    print('(You can also drag and drop the folder below, and then hit Enter)')
    destination = input('> ')
    print('\n')
  destination = destination.strip() # Get rid of trailing whitespaces
  destination = destination.replace('\\ ', ' ') # Get rid of backslash characters to avoid issues with listdir
  # Make subfolders for metadata and shared albums
  shared = destination + '/' + 'shared'
  extracts = destination + '/' + 'extract'
  os.mkdir(shared)
  os.mkdir(extracts)


  # Get all zip files ignoring hidden files
  print(f'Reading zip files from {root}...')
  zips = []
  for x in os.listdir(root):
    if x.endswith('.zip'):
      zips.append(root + '/' + x)
  print('Zip files read successfully')

  # For each zip file:
  for z in sorted(zips):
    print('\n')
    print(f'Extracting from {z}...')
    # Extract zip
    with ZipFile(z) as zObject:
      zObject.extractall(path = root)
    extracted = z.replace('.zip','')
    # Inject metadata to photos in extracted folder
    inject_meta(extracted)
    # Move photos to root
    move_photos(extracted,destination)
    move_shared(extracted, shared)
    # Clean up: move leftover to extracts
    move_folder(extracted, extracts)

main()