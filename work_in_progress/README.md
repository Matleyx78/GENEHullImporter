# GENEHullImporter
A Freecad WorkBench for import data from results of a file GeneHull Sailboat 3.4
# Develop 
I'm developing in a Freecad 1.2dev
# Install
Download Zip and unzip in your Mod directory.

Restart Freecad
# Usage
Create a new document and save it with name 'GH_Import_Doc'.

VERY IMPORTANT:

Now running 'Save As...' and re-save the document. This because is the only way to update the 'internal' document's name.

From GeneHull ods file, copy all the sheet 'Offset x,y,z' and paste (only value) in a new xlsx file named 'GH_Offset_Sheet'

In Freecad doc 'GH_Import_Doc' from menu 'File', import the file 'GH_Offset_Sheet'

If all is correct, you have in freecad a new spreadsheet with the same mapping in the genehull ods file.

Now you are ready from import.
