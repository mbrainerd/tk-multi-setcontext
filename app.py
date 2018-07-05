# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.


from sgtk.platform import Application

class SetContextApp(Application):
    """
    The app entry point. This class is responsible for intializing and tearing down
    the application, handle menu registration etc.
    """
    
    def init_app(self):
        """
        Called as the application is being initialized
        """
        tk_multi_setcontext = self.import_module("tk_multi_setcontext")

        display_name = self.get_setting("display_name")

        command_name = display_name.lower()
        command_name = re.sub('[^0-9a-zA-Z]+', '_', command_name)

        # register command
        cb = lambda: tk_multi_setcontext.dialog.show_dialog(self)
        menu_caption = "%s..." % display_name
        menu_options = {
            "short_name": command_name,
            "description": "Set the current SGTK Context",
        }
        self.engine.register_command(menu_caption, cb, menu_options)

    @property
    def context_change_allowed(self):
        """
        Specifies that context changes are allowed.
        """
        return True

    def destroy_app(self):
        """
        Tear down the app
        """
        self.log_debug("Destroying tk-multi-setcontext")
