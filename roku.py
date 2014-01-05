import sublime, sublime_plugin
import os, sys
import zipfile
import threading

from .thread_progress import ThreadProgress

# request-dists is the folder in our plugin
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

try:
    import requests
except ImportError:
    pass

def get_root_directory():
    folders = sublime.active_window().folders()

    projDir = ""
    for folder in folders:

        folderLen = len(folder.split(os.sep))

        if projDir == "" or folderLen < len(projDir.split(os.sep)):
            projDir = folder

    return projDir


def get_project_name(projDir):
    dirList = projDir.split(os.sep)
    return dirList[len(dirList)-1]

class Roku():

    ACTION_INSTALL = 'Install'
    ACTION_REPLACE = 'Replace'
    ACTION_DELETE  = 'Delete'

    def getRokuBoxes(self):
        # sublime.active_window().project_data()['ip']
        return self.getSettings().get("boxes")

    def getSettings(self):
        return sublime.load_settings('Roku.sublime-settings')

    def installPackage(self):
        boxes = self.getRokuBoxes()

        if len(boxes) > 1:
            self.selectBoxToDeploy()
        elif len(boxes) == 1:
            self.deployToBoxByIndex(0)
        else:
            sublime.error_message('No roku boxes have been configured. Add roku boxes to Preferences > Package Settings > Roku > Settings - User.')

    def uninstallPackage(self):
        boxes = self.getRokuBoxes()

        if len(boxes) > 1:
            self.selectBoxToUninstall()
        elif len(boxes) == 1:
            self.uninstallFromBoxByIndex(0)
        else:
            sublime.error_message('No roku boxes have been configured. Add roku boxes to Preferences > Package Settings > Roku > Settings - User.')

    def createPackage(self):
        print('Packaging...')

        zf = zipfile.ZipFile(self.getArchivePath(), 'w')
        abs_src = os.path.abspath(get_root_directory())

        for dirname, subdirs, files in os.walk(get_root_directory()):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]

                # This is fairly messy need to fix this
                #   - maybe set up preferences for what to ignore in the project file or prefs file
                if(arcname.find('.buildpath') == -1 and
                    arcname.find('.gitignore') == -1 and
                    arcname.find('.project') == -1 and
                    arcname.find('.git') == -1 and
                    arcname.find('.sublime') == -1 and
                    arcname.find('build') == -1):
                        print('zipping %s as %s' % (os.path.join(dirname, filename), arcname))
                        zf.write(absname, arcname)
        zf.close()

        print('packaging complete.')

    def selectBoxToDeploy(self):
        boxes = self.getRokuBoxes()
        items = []

        for box in boxes:
            items.append([box['name'], box['ip']])

        sublime.active_window().show_quick_panel(items, self.deployToBoxByIndex)

    def selectBoxToUninstall(self):
        boxes = self.getRokuBoxes()
        items = []

        for box in boxes:
            items.append([box['name'], box['ip']])

        sublime.active_window().show_quick_panel(items, self.uninstallFromBoxByIndex)

    def deployToBoxByIndex(self, index):
        if index >= 0:
            box = self.getRokuBoxes()[index]
            self.post(box, self.ACTION_REPLACE, self.getArchivePath())

    def uninstallFromBoxByIndex(self, index):
        if index >= 0:
            box = self.getRokuBoxes()[index]
            self.post(box, self.ACTION_DELETE, self.getArchivePath())

    def getArchivePath(self):
        projectDir = get_root_directory()
        outputDirectory = projectDir + os.sep + 'build'
        projectName = get_project_name(projectDir)
        archive = outputDirectory + os.sep + projectName + '.zip'

        # check for and create build directory if necessary
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)

        return archive

    def post(self, box, action, archive = None):
        thread = RokuPluginInstall(box, action, archive, self.getSettings().get('timeout'))
        boxInfo = box['name'] + ' (' + box['ip'] + ')'
        if action == self.ACTION_INSTALL or action == self.ACTION_REPLACE:
            msg = 'Installing application to ' + boxInfo
        else:
            msg = 'Communicating with ' + boxInfo
        ThreadProgress(thread, msg, 'Done ' + msg)
        thread.start()

class RokuPluginInstall(threading.Thread):
    def __init__(self, box, action, archive = None, timeout = None):
        self.box = box
        self.action = action
        self.archive = archive
        self.timeout = timeout if timeout != None and timeout > 0 else None
        self.result = None
        threading.Thread.__init__(self)

    def run(self):
        url = 'http://' + self.box['ip'] + '/plugin_install/'
        # url = 'http://httpbin.org/post'
        payload = {'mysubmit': self.action}
        if not self.archive == None:
            files = {'archive': open(self.archive, 'rb')}
        else:
            files = {}

        try:
            s = requests.Session()
            s.auth = requests.auth.HTTPDigestAuth(self.box['user'], self.box['pass'])

            # Make a get request first to setup the authentication
            s.get(url, timeout=self.timeout)

            # Do the post
            r = s.post(url, timeout=self.timeout, files=files, data=payload)
            print(r.status_code)

            if r.status_code == 401:
                # Prompt for password
                sublime.active_window().show_input_panel('Unauthorized: Please provide your roku password:', self.box['pass'], self.promptPasswordDone, None, self.promptPasswordCancel)
                return

            if not r.status_code == 200:
                sublime.error_message(r.status_code)

            # TODO: Search response for text
            # Install Success.
            # Warning: Application size limits it to Roku 2 players, Roku XDS and Roku XR. It will not work with other Roku 1 players (2093212 > 768000).
            # Install Failure: Unzip failed. Invalid or corrupt zip archive.  Unloading.
            # Application Received: Identical to previous version -- not replacing.

            print(r.text)
            self.result = r
        except requests.exceptions.ConnectionError as e:
            print(e)
            sublime.error_message('Could not connect to ' + self.box['name'] + ' (' + self.box['ip'] + ')')
        except requests.exceptions.Timeout as e:
            print(e)
            sublime.error_message('Timeout while communicating with ' + self.box['name'] + ' (' + self.box['ip'] + ')')

    def promptPasswordDone(self, password):
        self.box['pass'] = password
        self.run()

    def promptPasswordCancel(self):
        self.result = False






