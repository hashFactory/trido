#!/usr/local/bin/python3
import datetime

import os
import json
import sys
import argparse
import shutil
import subprocess
from pathlib import Path

settings = {
}

posts = []
html_post_filenames = []
htmls = {}
files = {}

# verbosity flag
V = False
DRYRUN = False

# defines all the metadata a page needs
class FuturePage():
    def __init__(self):
        self.name = ""
        self.type = ""
        self.filename = ""
        self.title = ""
        self.nav = ""
        self.header = ""
        self.article = ""
        self.template = ""

    def __str__(self):
        return self.name + " " + self.filename

# contains all info relevant to a post
class Post:
    # all our useful fields
    def __init__(self):
        self.userid = ""
        self.postid = 0
        self.title = ""
        self.content = ""
        self.creationdate = datetime.datetime(2021, 1, 1).timestamp()
        self.modifieddate = datetime.datetime(2021, 1, 1).timestamp()
        self.collection = ""
        self.tags = []
        self.files = []
        self.links = []
        self.post_map_filename = ""
        self.html_filename = ""

    # populate post from post map file
    def from_post_map(self, filename):
        self.post_map_filename = filename

        # check if json file exists
        if not os.path.exists(self.post_map_filename):
            print("WARNING: Could not find post map file '" + str(self.post_map_filename) + "', ignoring")
            return None
        else:
            # deserialize json
            with open(self.post_map_filename, 'r', encoding='UTF-8') as j:
                post_map = json.load(j, strict=False)

            # TODO: properly convert markdown to html
            # read in fields
            self.userid = post_map.get("userid")
            self.postid = int(post_map.get("postid"))
            self.title = post_map.get("title")
            self.content = post_map.get("content")
            self.creationdate = post_map.get("creationdate")

            # if verbose
            if V:
                print("Successfully read in " + str(self))
            return self

    # check if post is still empty
    def is_empty(self):
        if self.userid == "" and self.postid == "":
            return True
        return False

    # writes post to html and returns it
    def to_html(self):
        filename = settings["output_dir"] + settings["content_dir"] + "posts/" + str(self.creationdate) + ".html"

        # generate html
        new_post = get_primitive("post.html")
        new_post = new_post.replace("|TITLE|", self.title)
        new_post = new_post.replace("|POSTCONTENTS|", self.content)

        # write to html file
        if not DRYRUN:
            with open(filename, 'w') as html:
                html.write(new_post)

        # add new file location to global list
        self.html_filename = filename
        htmls[self.postid] = filename

    # writes post to post map file
    def to_post_map(self):
        filename = _outdir() + settings["content_dir"] + "posts/" + datetime.datetime.now().timestamp() + ".map"

        with open(filename, 'w', encoding='utf-8') as pm:
            if V:
                print("Wrote \'" + self.title + "\' to " + filename)
            json.dump(self, pm, encoding='utf-8')

    # returns string info
    def __str__(self):
        return self.userid + " (" + self.post_map_filename + "): " + self.title

# defines what macros are available to a page
class Macro():
    def __init__(self, name, tag, filename):
        self.name = name
        self.tag = tag
        self.filename = filename

    def __str__(self):
        return self.name + " " + self.tag + " " + self.filename

# return output dir as string
def _outdir():
    global settings
    return settings['output_dir']

# fetch the default template page
def get_page(template):
    with open("primitives/home.html", 'r') as page_template:
        #return [l.rstrip() for l in page_template.readlines()]
        contents = page_template.read()
        page_template.close()
        return contents

# fetch primitive
def get_primitive(primitive):
    global settings
    with open(settings['template_dir'] + primitive, 'r') as primitive_template:
        contents = primitive_template.read()
        primitive_template.close()
        return contents

# generate html posts
def post_map_to_html(future, macros):
    global html_post_filenames, htmls

    # fetch locations
    post_map_files = [fi for fi in os.listdir(settings['postmaps_dir']) if fi.endswith(".map")]
    if V:
        print("Found " + str(len(post_map_files)) + " post map files in " + settings['postmaps_dir'])
    primitive_post = open(settings['template_dir'] + 'post.html')

    # generate individual htmls
    for pmf in post_map_files:
        new_post = Post()
        new_post.from_post_map(settings['postmaps_dir'] + pmf)
        new_post.to_html()
        posts.append(new_post)

    # sort posts in chronological order
    #html_post_filenames = dict(sorted(html_post_filenames.items()))
    posts.sort(key=lambda a: a.postid)

    for p in posts:
        html_post_filenames.append(p.html_filename)
    #html_post_filenames = htmls.
    #html_post_filenames = [value.html_filename for value in temp]

# generates the new pages
def generate_pages(future, macros):
    global settings

    for fu in future:
        template = get_page("home.html")
        with open(settings['template_dir'] + fu.filename, 'r') as content:
            # modify template
            """for m in range(1, 3):
                template = template.replace(macros[m].name, open("templates/" + macros[m].filename, 'r').read())
            template = template.replace("<|ARTICLE|>", content.read())
            template = template.replace("<|TITLE|>", fu.title)"""

            # TODO: generalise with macros
            html_buffer = ""

            for p in posts:
                with open(p.html_filename, 'r', encoding='utf-8') as f:
                    html_buffer = html_buffer + f.read() + "\n"

            template = template.replace("|PROJECTS|", html_buffer)

            # write to output file
            if not DRYRUN:
                with open(settings['output_dir'] + fu.filename, 'w', encoding='utf-8') as future_page:
                    future_page.write(template)
                    future_page.close()
            
            # output html contents if the user wants
            if V:
                print("Populated home.html")
            content.close()
"""
def process(r1):
    with open(r1, 'r', encoding='utf-8') as f:
        input = f.read()
        with open(str(datetime.datetime.now().timestamp()) + ".map", 'w', encoding='utf-8') as f2:
            json.dump(input, f2)
"""
# read the pages json into an object
def read_site_map(filename):
    global settings
    # read in json file
    with open(filename, 'r', encoding='utf-8') as f:
        pages = json.load(f)

    # read in settings (there's got to be a better way of doing this)
    fields = ['macros_file', 'publish_file', 'content_dir', 'template_dir', 'output_dir', 'postmaps_dir']
    for f in fields:
        if pages.get(f):
            settings[f] = pages.get(f)
    
    # get what must be included
    if pages.get('include'):
        settings['include'] = pages.get('include')

    future = []

    # read in json into smarter objects
    for page in pages['pages']:
        fu = FuturePage()
        if page.get('name'):
            fu.name = page['name']
        if page.get('filename'):
            fu.filename = page['filename']
        if page.get('type'):
            fu.type = page['type']
            if fu.type == 'content':
                fu.article = fu.filename
        if page.get('title'):
            fu.title = page['title']
        if V:
            print(fu)
        future.append(fu)

    # fill the blanks
    for fu in future:
        if fu.title == "":
            fu.title = "title.html"
        if fu.nav == "":
            fu.nav = "nav.html"
        if fu.header == "":
            fu.header = "header.html"
        if fu.article == "":
            fu.article = "article.html"
    return future

# builds scp command in a list so subprocess.run can use it
def generate_scp(pub_settings):
    global settings

    scp_command = ['scp', '-r']

    # read in optional settings if they're there
    if pub_settings['-i']:
        scp_command.append('-i')
        scp_command.append(pub_settings['-i'])
    if pub_settings['-P']:
        scp_command.append('-P')
        scp_command.append(pub_settings['-P'])

    # read in source and destination
    if pub_settings.get('src'):
        scp_command.append(pub_settings['src'])
    if pub_settings.get('dst'):
        scp_command.append(pub_settings['dst'])

    return scp_command

# read macros.map to find substitutions
def read_macros_map(filename):
    macros = []
    with open(filename, 'r') as f:
        contents = [l.rstrip() for l in f.readlines()]
    for c in contents:
        if len(c) > 2:
            line = c.split(" ")
            macros.append(Macro(line[0], line[1], line[2]))
    return macros

# read publish.map file
def read_publish_map(filename):
    global settings

    # start loading in our publish.map
    pub_settings = {}
    with open(filename, 'r', encoding='utf-8') as f:
        pub_json = json.load(f)

    # read in settings one by one
    fields = ['-i', '-P']
    for f in fields:
        if pub_json.get(f):
            pub_settings[f] = pub_json.get(f)

    # if src and dst don't exist, make guesses
    if pub_json.get('src'):
        pub_settings['src'] = pub_json.get('src')
    else:
        pub_settings['src'] = settings['output_dir']
    if pub_json.get('dst'):
        pub_settings['dst'] = pub_json.get('dst')
    else:
        print("ERROR: need to specify a destination")
        sys.exit(12)

    return pub_settings

# cleans compiled files
def clean(future):
    for fu in future:
        if V:
            print("Not removing " + fu.filename)
        if os.path.exists(fu.filename):
            if V:
                print("Removing " + fu.filename)
            os.remove(fu.filename)

# main compiling function
def compile(future):
    global settings
    macros = read_macros_map(settings['macros_file'])
    settings['output_dir'] = ''
    generate_pages(future, macros)

# include files and directories
def export_include():
    global settings
    output = settings['output_dir']
    for i in settings['include']:
        if i[-1] == '/':
            if V:
                print("Copying contents of " + i + " to " + output + i)
            # TODO: clean up how ugly this is
            files = list(Path(i).rglob('*.*'))
            
            for f in files:
                f_parent, f_name = os.path.split(Path(f))
                # make new directory in output if it doesn't exist yet
                if not os.path.isdir(output + f_parent):
                    if V:
                        print("makedirs(" + str(output + f_parent) + ")")
                    os.makedirs(output + f_parent, exist_ok=True)

                # if it doesn't exist yet, copy
                if not os.path.exists(output + str(f)):
                    if V:
                        print("Copying " + str(f) + " to " + (output + str(f)) + " since it doesn't exist")
                    shutil.copy2(f, output + str(f))
                # if source file is newer, copy
                elif os.path.getmtime(f) > os.path.getmtime(output + str(f)):
                    if V:
                        print("Copying " + str(f) + " to " + (output + str(f)) + " since source is newer")
                    shutil.copy2(f, output + str(f))
                # if we don't need to copy
                else:
                    if V:
                        print("Skipping " + str(f) + " since it already exists " + (output + str(f)))
        else:
            if V:
                print("Copying " + i + " to " + output + i)
            shutil.copy2(i, output)

# export compiled site to specified directory
def export(future):
    global settings
    macros = read_macros_map(settings['macros_file'])
    #if os.path.exists(settings['output_dir']):
    #    shutil.rmtree(settings['output_dir'])
    if not os.path.exists(settings['output_dir']):
        os.mkdir(settings['output_dir'])
    if not os.path.exists(settings['output_dir'] + "content"):
        os.mkdir(settings['output_dir'] + "content")
    if not os.path.exists(settings['output_dir'] + "content/posts"):
        os.mkdir(settings['output_dir'] + "content/posts")
    
    post_map_to_html(future, macros)
    generate_pages(future, macros)
    export_include()

# uses export to publish website using publish_file directive
def publish(future):
    global settings

    # generate command from settings
    pub_settings = read_publish_map(settings['publish_file'])
    scp_command = generate_scp(pub_settings)
    if V:
        print(scp_command)

    # compile website
    if V:
        print("Compiling according to " + settings['site_map'] + " ...")
    export(future)
    if V:
        print("Done compiling")

    # execute
    print("Using '" + ' '.join(scp_command) + "' to publish")
    if 'y' not in input("Is this correct? [y/n] ").lower():
        print("ERROR: you cancelled the operation")
        sys.exit(14)

    print("Publishing to " + pub_settings['dst'] + " ...")
    scp_run = subprocess.run(scp_command)
    if scp_run.returncode != 0:
        print("ERROR: scp failed with error " + str(scp_run.returncode))
        sys.exit(13)
    else:
        print("Success!")

# check if user really wants to populate 
def check_if_user_compile():
    print("""It is generally preferred to use the export functionality. 
This will compile the project into the current directory. 
Are you sure this is what you want? [y/n]  """)
    choice = input().lower()
    return "y" in choice

# handles main functions
def main(args):
    global V, DRYRUN
    # set defaults
    macros_file = "macros.map"
    site_file = "site.map"
    content_dir = "content/"

    if args.map:
        site_file = args.map

    future = read_site_map(site_file)
    settings['site_map'] = site_file

    if args.output:
        if args.output[-1] != '/':
            args.output += '/'
        settings['output_dir'] = args.output

    # main argument loop
    if args.verbose:
        V = True
    if args.command == 'clean':
        clean(future)
    elif args.command == 'compile':
        if check_if_user_compile():
            compile(future)
        else:
            print("Exiting...")
    elif args.command == 'dryrun':
        DRYRUN = True
        compile(future)
    elif args.command == 'export':
        export(future)
    elif args.command == 'publish':
        publish(future)

# main entry
# just parses and sends everything to main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Project processor") 

    # add keyword commands to commands parser
    commands = parser.add_subparsers(title='possible commands', dest='command', metavar='COMMAND')
    commands.add_parser("clean", help="deletes compiled files")
    commands.add_parser("dryrun", help="compiles without writing files")
    commands.add_parser("compile", help="compiles in current dir project (deprecated, use export)")
    commands.add_parser("export", help="compiles & exports according to site.map")
    commands.add_parser("publish", help="exports via scp according to publish.map")

    # add flag arguments here
    parser.add_argument("-v", "--verbose", help="print changes", action="store_true")
    parser.add_argument("-o", "--output", help="set the output directory for export", action="store", dest='output')
    parser.add_argument("-m", "--map", help="specify site.map generator", action="store", dest='map')

    # print help if no commands specified
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # send all to main
    args = parser.parse_args()
    main(args)