# StaticPageGenerator
My custom static page generator - not meant to be generic

There are currently two main functionalities:
Menu generation: takes two files
- Menu Entries
- Affected pages

Template: takes three arguments
- Detailed contents
- Template file
- Target file

Currently it processes one file at a time.

The static generator is very stringint on syntax, I didn't bother making it flexible because it is meant to fit with what I need to do and I've only had to set it up once so far, if I need to do any other custom jobs, I simply add a method in the class and run the script again.
