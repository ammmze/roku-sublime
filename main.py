import sublime, sublime_plugin
import os

from .roku import Roku
roku = Roku()

class RokuPackageInstallCommand(sublime_plugin.WindowCommand):
    def run(self):
        roku.createPackage()
        roku.installPackage()

class RokuUninstallCommand(sublime_plugin.WindowCommand):
    def run(self):
        roku.uninstallPackage()

class RokuPackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        roku.createPackage()

class RokuInstallCommand(sublime_plugin.WindowCommand):
    def run(self):
        roku.installPackage()

class RokuReplaceCommand(sublime_plugin.ApplicationCommand):
    def run(args):
        roku.installPackage()

class RokuSettingsCommand(sublime_plugin.WindowCommand):
    def run(self, default=True):
        # Define path variables
        try:
            packagePath = os.path.dirname(os.path.realpath(__file__))
            packageFolder = os.path.basename(packagePath)
        except:
            pass

        # Show default settings in package when available
        if default and packageFolder is not None:
            package = packageFolder
        # Otherwise show User defined settings
        else:
            package = "User"
        # Strip .sublime-package of package name for syntax file
        package_extension = ".sublime-package"
        if package.endswith(package_extension):
            package = package[:-len(package_extension)]
        # Open settings file
        self.window.run_command('open_file', {'file': '${packages}/' + package + '/Roku.sublime-settings' });
