#!/usr/bin/python3
import datetime

import os
import json
import sys
import argparse
import shutil
import subprocess
import random
from string import hexdigits
from pathlib import Path
from urllib import parse

import time

# verbosity flag
V = False
DRYRUN = False

# defines all the metadata a page needs
class FuturePage:
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
    def __init__(self, userid="", title="", content=""):
        self.userid: str = userid
        self.title: str = str(title)
        self.content: str = content
        self.creationdate = datetime.datetime.now().timestamp()
        self.modifieddate = self.creationdate
        self.postid = self.creationdate
        self.collection = ""
        self.tags = []
        self.files = []
        self.links = []
        self.post_map_filename = str(self.creationdate) + ".map"
        self.html_filename = str(self.creationdate) + ".html"

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
            # TODO: convert links
            # read in fields
            self.userid = str(post_map.get("userid"))
            self.postid = str(post_map.get("postid"))
            self.title = str(post_map.get("title"))
            self.content = post_map.get("content")
            self.creationdate = str(post_map.get("creationdate"))
            self.modifieddate = str(post_map.get("modifieddate"))

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
    def to_html(self, output_dir="content/posts/", template_dir="primitives/"):
        self.html_filename = str(self.postid) + ".html"
        filename = output_dir + self.html_filename

        # generate html
        new_post = get_primitive(template_dir, "post.html")
        new_post = new_post.replace("|TITLE|", self.title)
        new_post = new_post.replace("|POSTCONTENTS|", self.content)

        # TODO: img lazy loading (remove later)
        new_post = new_post.replace("<img ", "<img loading=\"lazy\" ")

        # write to html file
        if not DRYRUN:
            with open(filename, 'w') as html:
                html.write(new_post)

        # add new file location to global list
        return self.html_filename

    # writes post to post map file
    def to_post_map(self, users_dir="users/"):
        self.post_map_filename = str(self.creationdate) + ".map"
        filename = users_dir + self.userid + "/postmaps/" + self.post_map_filename

        with open(filename, 'w', encoding='utf-8') as pm:
            if V:
                print("Wrote \'" + self.title + "\' to " + filename)
            json.dump(self.__dict__(), pm, skipkeys=True)
        shutil.copy2(filename, filename.replace("/postmaps/", "/backup_posts/"))

    # returns string info
    def __str__(self):
        return self.userid + " (" + self.post_map_filename + "): " + self.title

    # returns dict version of object
    def __dict__(self):
        return {
            'userid': str(self.userid),
            'postid': str(self.postid),
            'title': str(self.title),
            'content': str(self.content),
            'creationdate': self.creationdate,
            'modifieddate': self.modifieddate,
            'collection': self.collection
        }

# defines a user
class User:
    def __init__(self, userid="", username=""):
        self.userid: str = userid
        self.username: str = username
        self.creationdate = datetime.datetime.now().timestamp()
        self.postlist: [str] = []
        self.user_map_filename: str = ""
        self.homepage: str = ""
        self.colors = {}
        self.backgroundimage = ""

    # populate info from .map file
    def from_user_map(self, filename):
        self.user_map_filename = filename

        # deserialize json
        with open(self.user_map_filename, 'r', encoding='UTF-8') as j:
            user_map = json.load(j, strict=False)

        # read in relevant fields
        self.userid = user_map.get("userid")
        self.username = user_map.get("username")
        self.creationdate = user_map.get("creationdate")
        self.postlist = [str(u) for u in user_map.get("postlist")]
        self.homepage = self.userid + ".html"
        self.backgroundimage = user_map.get("backgroundimage")

        return self

    def to_html(self, output_dir="content/users/", template_dir="primitives/"):
        pass

    # write user map
    def to_user_map(self, users_dir="users/"):
        self.user_map_filename = str(self.username) + ".map"
        filename = users_dir + self.userid + "/" + self.user_map_filename

        with open(filename, 'w', encoding='utf-8') as um:
            if V:
                print("Wrote user \'" + self.username + "\' to " + filename)
            json.dump(self.__dict__(), um, skipkeys=True)
        #shutil.copy2(filename, filename.replace("postmaps", "backup_posts"))

    # add post to user list
    def add_post(self, postid):
        self.postlist.append(postid)

    # reset posts
    def reset_posts(self):
        self.postlist: [str] = []

    def __dict__(self):
        return {
            'userid': self.userid,
            'username': self.username,
            'creationdate': self.creationdate,
            'postlist': self.postlist,
            'backgroundimage': self.backgroundimage
        }

class Posts:
    def __init__(self):
        self.posts = {}

    def add(self, post: Post):
        if post:
            self.posts[post.postid] = post

    def get(self, postid=""):
        """for p in self.posts:
            if p.postid == postid:
                return p"""
        if postid in self.posts.keys():
            return self.posts.get(postid)
        else:
            print("Could not find post with id=" + postid)

        return None

class Users:
    def __init__(self, users_dir="users/"):
        self.users: [User] = []

    # creates relevant directories but doesn't add it to main list
    def create_user(self, s: dict, userid):
        #os.mkdir(s["output_dir"] + s["postmaps_dir"] + userid)
        os.makedirs(s["output_dir"] + s["content_dir"] + "posts/" + userid, exist_ok=True)

        os.makedirs(s["output_dir"] + s["users_dir"] + userid, exist_ok=True)
        os.makedirs(s["output_dir"] + s["users_dir"] + userid + "/postmaps/", exist_ok=True)
        os.makedirs(s["output_dir"] + s["users_dir"] + userid + "/backup_posts/", exist_ok=True)
        os.makedirs(s["output_dir"] + "assets/" + userid + "/", exist_ok=True)

        if not os.path.exists(s["output_dir"] + s["users_dir"] + userid + "/colors.map"):
            shutil.copy2(s["template_dir"] + "colors.map", s["output_dir"] + s["users_dir"] + userid + "/colors.map")

        user = User(userid=userid, username=userid)
        if V:
            print("Created user!")
        return user

    # repopulates user with default posts
    def reset_user_posts(self, s: dict, userid=""):
        pass
        # delete posts and replace with originals
        #shutil.rmtree('content/' + userid + '/postmaps/')
        #shutil.rmtree('content/' + userid + '/posts/')
        #shutil.copytree('content/defaultposts/', 'content/postmaps')

        #shutil.copytree('content/defaultposts/', 'content/postmaps')

    # check if username is already taken
    def check_if_user_exists(self, userid=""):
        for u in self.users:
            if u.userid == userid:
                return True
        return False

    # fetch user by id
    def get_user_by_id(self, userid="") -> User :
        for u in self.users:
            if u.userid == userid:
                return u


# defines what macros are available to a page
class Macro:
    def __init__(self, name, tag, filename):
        self.name = name
        self.tag = tag
        self.filename = filename

    def __str__(self):
        return self.name + " " + self.tag + " " + self.filename

class Trido:
    def __init__(self, site_map='site.map'):
        self.s = {}
        self.posts = Posts()
        self.users = Users()
        self.home_filenames = []
        self.htmls = {}
        self.files = {}
        self.read_site_map(site_map)
        self.init_users()

    # parse api url
    def parse_api(self, url: str):
        split = url.split('/')

        if len(split) > 3:
            if split[1] == 'api':
                return split[2], split[3]

    # handles cgi post requests
    def handle_post_request(self, rt: (str, str), form: dict) -> str:
        redirect = "user/" + rt[0]
        if rt[0] == 'home':
            redirect = ""

        # resetcolors.py
        if rt[1] == 'resetcolors.py':
            # read in from default colors map
            with open("primitives/defaultcolors.map", 'r') as defaultcolors:
                with open("users/" + rt[0] + "/colors.map", 'w') as data:
                    json.dump(json.load(defaultcolors), data)
            self.generate_user_homepage(rt[0])
            return redirect

        # colors.py
        elif rt[1] == 'colors.py':
            colors = {"|BGCOLOR|": form["bgcolor"][0], "|TITLECOLOR|": form["titlecolor"][0],
                      "|TEXTCOLOR|": form["textcolor"][0], "|BOXCOLOR|": form["boxcolor"][0]}

            with open("users/" + rt[0] + "/colors.map", 'w') as data:
                json.dump(dict(colors), data)

            self.generate_user_homepage(rt[0])
            return redirect

        # randomcolors.py
        elif rt[1] == 'randomcolors.py':
            fields = ['|BGCOLOR|', '|TITLECOLOR|', '|TEXTCOLOR|', '|BOXCOLOR|']
            # only python 3.9+ :\
            #colors = [(f, '#' + random.randbytes(3).hex()) for f in fields]
            # python 3.7 fix
            colors = [(f, '#' + ''.join([random.choice(hexdigits) for n in range(6)])) for f in fields]

            with open("users/" + rt[0] + "/colors.map", 'w') as data:
                json.dump(dict(colors), data)

            self.generate_user_homepage(rt[0])
            return redirect

        elif rt[1] == 'uploadfile.py':
            return redirect

        # setbackground.py
        elif rt[1] == 'setbackground.py' or rt[1] == 'uploadbackground.py':
            bgurl: str = form.get("bgurl")[0]
            user = self.users.get_user_by_id(rt[0])
            if not bgurl.startswith("http"):
                #bgurl = user.userid + "/" +
                pass
                #bgurl = bgurl.replace("|USER|", str(user.userid))
                # TODO: fix bgurl prefix discrepency

            if len(bgurl) > 0:
                if user:
                    user.backgroundimage = bgurl
                    user.to_user_map(self.s["output_dir"] + self.s["users_dir"])
                    self.generate_user_homepage(user.userid)

            return redirect

        # resetposts.py
        elif rt[1] == 'resetposts.py':
            self.users.reset_user_posts(self.s, rt[0])

            # regenerate html pages
            self.post_maps_to_html(postmaps_dir="content/postmaps/")
            return redirect

        # createprofile.py
        elif rt[1] == 'createprofile.py':
            userid = form.get("userid", ["anonymous"])[0]

            user = self.users.get_user_by_id(userid)

            if user is None:
                user = self.users.create_user(self.s, userid=userid)
                self.users.users.append(user)
                user.to_user_map(self.s["output_dir"] + self.s["users_dir"])
                self.generate_user_homepages()
                return "user/" + userid
            else:
                return "/"

        # submitpost.py
        elif rt[1] == 'submitpost.py':
            title = form.get("title", ["Default title"])[0]
            userid = form.get("userid", ["anonymous"])[0]
            content = form.get("content", ["Whoops! this post seems to be empty!"])[0]

            user = self.users.get_user_by_id(userid)

            # check if user doesn't exist
            if user is None:
                user = self.users.create_user(self.s, userid=userid)
                self.users.users.append(user)

            # create and save new post
            np = Post(userid, title, content)
            np.to_post_map()
            np.to_html()
            self.posts.add(np)
            user.postlist.append(np.postid)

            # save user map
            user.to_user_map(self.s["output_dir"] + self.s["users_dir"])

            self.post_maps_to_html(self.s["users_dir"] + userid + "/postmaps/")
            self.generate_user_homepages()
            return "user/" + user.userid

        self.generate_home_page()

    # TODO: split trido into api and ssg
    # TODO: decide on source of truth .map or postmaps folder
    # TODO: edit post portal
    # TODO: make post links clickable
    # TODO: file upload action
    # TODO: fix reset posts
    # TODO: fix compile arg
    # TODO: look into macro replacement engine
    # TODO: user export and backup
    # TODO: add prefix for links
    # TODO: support different deployment configurations
    # TODO: page to manage user's files
    # TODO: fix filename on save
    # TODO: POST reply multi part data with filename

    # generate html posts
    def post_maps_to_html(self, postmaps_dir="users/home/postmaps/"):
        # sort posts in chronological order
        post_map_files = [fi for fi in os.listdir(postmaps_dir) if fi.endswith(".map")]
        post_map_files.sort()
        if V:
            print("Found " + str(len(post_map_files)) + " post map files in " + postmaps_dir)
        #primitive_post = open(self.s['template_dir'] + 'post.html')

        # generate individual htmls
        for pmf in post_map_files:
            new_post = Post()
            new_post.from_post_map(postmaps_dir + pmf)
            new_post.to_html(self.s['output_dir'] + self.s['content_dir'] + "posts/" + new_post.userid + "/")
            self.posts.add(new_post)

    # regenerate main.css

    # generates all user's homepages
    def generate_user_homepages(self):
        for u in self.users.users:
            self.post_maps_to_html(self.s["users_dir"] + "/" + u.userid + "/postmaps/")
            self.generate_user_homepage(u.userid)

    # generate user home pages
    def generate_user_homepage(self, user: str):
        template = self.get_page("user.html")
        html_buffer = ""
        location = self.s['output_dir'] + self.s['content_dir'] + 'posts/' + user + "/"

        user_posts = [fi for fi in os.listdir(location) if fi.endswith(".html")]
        user_posts.sort()
        user_posts.reverse()

        for u in user_posts:
            #with open(location + post.html_filename, 'r') as f:
            with open(location + u, 'r') as f:
                html_buffer += f.read() + "\n"

        # fetch colors
        with open(self.s["output_dir"] + self.s["users_dir"] + user + "/" + "colors.map", 'r') as data:
            colors = json.load(data)

        users_buffer = ""
        for u in self.users.users:
            users_buffer = "<li><a class=\"basic-link\" href=\"|SERVER|user/" + str(u.userid) + "\" >user/" + u.userid + "</a></li>" + users_buffer

        template = template.replace("|OTHERUSERS|", users_buffer)

        template = template.replace("|BGURL|", self.users.get_user_by_id(user).backgroundimage)
        bgurl = ""
        bgimage = self.users.get_user_by_id(user).backgroundimage
        if not bgimage.startswith("http"):
            bgimage = self.s["server"] + "assets/" + bgimage
        if bgimage != "":
            bgurl = "background-image: url('" + bgimage + "');\n"


        template = template.replace("|POSTS|", html_buffer)
        template = template.replace("|ASSETS|", self.s['assets_location'])
        template = template.replace("|SERVER|", self.s['server'])
        template = template.replace("|USER|", str(user))
        template = template.replace("|RANDOM|", str(datetime.datetime.now()))

        # replace colors in css and home.html
        with open("primitives/maintemplate.css", "r") as csstemplate:
            with open(self.s["output_dir"] + self.s["content_dir"] + user + ".css", "w") as maincss:
                css = csstemplate.read()
                for k, v in colors.items():
                    if V:
                        print(str(k) + ", " + str(v))
                    css = css.replace('\"' + k + '\"', v)
                    template = template.replace(k, v)

                css = css.replace("\"|BGURL|\"", bgurl)
                maincss.write(css)
                template = template.replace("|MAINCSS|", css, 1)

        if not DRYRUN:
            with open(self.s['output_dir'] + self.s['content_dir'] + user + ".html", 'w') as f:
                f.write(template)

        if V:
            print("Wrote " + user + "'s homepage")

    # generates the home page
    def generate_home_page(self):
        template = self.get_page("home.html")
        # modify template
        """for m in range(1, 3):
            template = template.replace(macros[m].name, open("templates/" + macros[m].filename, 'r').read())"""

        # TODO: generalise with macros
        html_buffer = ""

        self.home_filenames = [self.posts.get(i).html_filename for i in self.users.get_user_by_id("home").postlist]
        for h in self.home_filenames:
            with open(self.s['output_dir'] + self.s['content_dir'] + "posts/home/" + h, 'r', encoding='utf-8') as f:
                html_buffer = html_buffer + f.read() + "\n"

        # fetch colors
        with open("primitives/colors.map", 'r') as data:
            colors = json.load(data)

        # replace colors in css and home.html
        with open("primitives/maintemplate.css", "r") as csstemplate:
            with open("primitives/main.css", "w") as maincss:
                css = csstemplate.read()
                for k, v in colors.items():
                    if V:
                        print(str(k) + ", " + str(v))
                    css = css.replace('\"' + k + '\"', v)
                    html_buffer = html_buffer.replace(k, v)
                maincss.write(css)
                # TODO: temp speedup css
                template = template.replace("|MAINCSS|", css, 1)

        template = template.replace("|PROJECTS|", html_buffer)
        #template = template.replace("|SUBMIT|", open('submitpost.html').read())
        template = template.replace("|SUBMIT|", "")
        template = template.replace("|ASSETS|", self.s['assets_location'])
        template = template.replace("|SERVER|", self.s['server'])
        template = template.replace("|RANDOM|", str(datetime.datetime.now()))

        # write to output file
        if not DRYRUN:
            with open(self.s['output_dir'] + 'home.html', 'w', encoding='utf-8') as future_page:
                future_page.write(template)
                future_page.close()

        # output html contents if the user wants
        if V:
            print("Populated home.html")

    # find all users
    def init_users(self):
        self.users.users = []

        # grab all non hidden directories
        _users = [u for u in (list(os.listdir(self.s["users_dir"])))]
        for u in _users:
            if "DS_Store" not in u:
                new_user = self.users.create_user(self.s, userid=u)
                new_user.from_user_map(self.s["users_dir"] + u + "/" + u + ".map")
                self.users.users.append(new_user)

    # read the pages json into an object
    def read_site_map(self, filename):
        # read in json file
        with open(filename, 'r', encoding='utf-8') as f:
            self.pages = json.load(f)

        # read in settings (there's got to be a better way of doing this)
        fields = ['macros_file', 'publish_file', 'content_dir', 'template_dir', 'output_dir', 'postmaps_dir', 'assets_location', 'server', 'usermaps_dir', 'users_dir']
        for f in fields:
            if self.pages.get(f):
                self.s[f] = self.pages.get(f)

        # get what must be included
        if self.pages.get('include'):
            self.s['include'] = self.pages.get('include')

        # get server info
        server_info = parse.urlparse(self.s['server'])

        self.s["port"] = server_info.port
        self.s["hostname"] = server_info.hostname

        future = []

        # read in json into smarter objects
        # TODO: replace with json.load
        for page in self.pages['pages']:
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

    # read publish.map file
    def read_publish_map(self, filename):
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
            pub_settings['src'] = self.s['output_dir']
        if pub_json.get('dst'):
            pub_settings['dst'] = pub_json.get('dst')
        else:
            print("ERROR: need to specify a destination")
            sys.exit(12)

        return pub_settings

    # read macros.map to find substitutions
    def read_macros_map(self, filename):
        macros = []
        with open(filename, 'r') as f:
            contents = [l.rstrip() for l in f.readlines()]
        for c in contents:
            if len(c) > 2:
                line = c.split(" ")
                macros.append(Macro(line[0], line[1], line[2]))
        return macros

    # cleans compiled files
    def clean(self, future):
        for fu in future:
            if V:
                print("Not removing " + fu.filename)
            if os.path.exists(fu.filename):
                if V:
                    print("Removing " + fu.filename)
                os.remove(fu.filename)

    # main compiling function
    def compile(self, future):
        macros = self.read_macros_map(self.s['macros_file'])
        self.s['output_dir'] = ''
        self.generate_home_page()

    # include files and directories
    def export_include(self):
        output = self.s['output_dir']
        for i in self.s['include']:
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
        # copy a backup of default post maps
        #shutil.copytree(self.s['postmaps_dir'], self.s['output_dir'] + 'content/defaultposts/')
        os.makedirs(self.s['output_dir'] + 'content/posts/', exist_ok=True)

    # export compiled site to specified directory
    def export(self, future):
        self.macros = self.read_macros_map(self.s['macros_file'])

        os.makedirs(self.s['output_dir'] + self.s['content_dir'] + "/posts", exist_ok=True)

        self.init_users()

        post_map_dirs = [self.s['users_dir'] + d + "/postmaps/" for d in os.listdir(self.s['users_dir'])]
        for d in post_map_dirs:
            self.post_maps_to_html(d)

        self.generate_user_homepages()
        #self.generate_home_page()
        self.export_include()

    # uses export to publish website using publish_file directive
    def publish(self, future):
        # generate command from settings
        pub_settings = self.read_publish_map(self.s['publish_file'])
        scp_command = generate_scp(pub_settings)
        if V:
            print(scp_command)

        # compile website
        if V:
            print("Compiling according to " + 'site.map' + " ...")
        self.export(future)
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

    # return output dir as string
    def _outdir(self):
        return self.s['output_dir']

    # fetch the default template page
    def get_page(self, template="home.html"):
        with open("primitives/" + template, 'r') as page_template:
            #return [l.rstrip() for l in page_template.readlines()]
            contents = page_template.read()
            page_template.close()
            return contents

    # fetch posts
    def get_num_posts(self):
        return len([fi for fi in os.listdir(self._outdir()) if fi.endswith(".map")])

# fetch primitive
def get_primitive(template_dir="primitives/", primitive="post.html"):
    with open(template_dir + primitive, 'r') as primitive_template:
        contents = primitive_template.read()
    return contents

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

    t = time.process_time()

    if args.map:
        site_file = args.map

    trido = Trido(site_map=site_file)

    if args.output:
        if args.output[-1] != '/':
            args.output += '/'
        trido.s['output_dir'] = args.output

    # main argument loop
    if args.verbose:
        V = True
    if args.command == 'clean':
        trido.clean(trido.s)
    elif args.command == 'compile':
        if check_if_user_compile():
            trido.s['output_dir'] = './'
            trido.export(trido.s)
        else:
            print("Exiting...")
    elif args.command == 'dryrun':
        DRYRUN = True
        trido.export(trido.s)
    elif args.command == 'export':
        trido.export(trido.s)
        if V:
            print("Run with: cd " + trido.s['output_dir'] + "; python3 -m http.server --cgi " + ''.join(filter(str.isdigit, trido.s['server'].split(':')[-1])))
    elif args.command == 'publish':
        trido.publish(trido.s)

    t2 = time.process_time() - t
    if V:
        print("Took " + str(t2) + " seconds")

# builds scp command in a list so subprocess.run can use it
def generate_scp(pub_settings):
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

"""
def process(r1):
    with open(r1, 'r', encoding='utf-8') as f:
        input = f.read()
        with open(str(datetime.datetime.now().timestamp()) + ".map", 'w', encoding='utf-8') as f2:
            json.dump(input, f2)
"""