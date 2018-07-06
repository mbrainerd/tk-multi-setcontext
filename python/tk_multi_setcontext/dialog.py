# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

# import the context_selector module from the qtwidgets framework
context_selector = sgtk.platform.import_framework(
    "tk-framework-qtwidgets", "context_selector")

# import the task_manager module from shotgunutils framework
task_manager = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "task_manager")

# import the shotgun_globals module from shotgunutils framework
shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals")

logger = sgtk.platform.get_logger(__name__)

def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    display_name = sgtk.platform.current_bundle().get_setting("display_name")

    # start ui
    app_instance.engine.show_dialog(display_name, app_instance, SetContextWidget)
    

class SetContextWidget(QtGui.QWidget):
    """
    A thin wrapper around the ContextSelector class available in the
    tk-frameworks-qtwidgets framework.
    """

    def __init__(self, parent=None):
        """
        Initialize the widget instance.
        """
        # call the base class init
        super(SetContextWidget, self).__init__(parent)

        # Resize this widget
        self.setObjectName("SetContextWidget")
        self.resize(350, 150)
        
        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()

        # create a background task manager for each of our components to use
        self._task_manager = task_manager.BackgroundTaskManager(self)

        self._context_widget = context_selector.ContextWidget(self)
        self._context_widget.set_up(self._task_manager)

        # If specified, restrict what entries should show up in the list of links when using
        # the auto completer.
        link_entity_types = self._app.get_setting("link_entity_types")
        if link_entity_types:
            self._context_widget.restrict_entity_types(link_entity_types)
        else:
            # Else, we only show entity types that are allowed for the Task.entity field.
            self._context_widget.restrict_entity_types_by_link("Task", "entity")

        # connect the signal emitted by the selector widget when a context is
        # selected. The connected callable should accept a context object.
        self._context_widget.context_changed.connect(
            self._on_item_context_change)

        # a button to toggle editing. the widget's editing capabilities can be
        # turned on/off. you can set the text to display in either state by
        # supplying it as an argument to the `enable_editing` method on the
        # widget. See the connected callable (self._select_context) for an
        # example.
        self._cancel_btn = QtGui.QPushButton("Cancel")
        self._cancel_btn.setObjectName("_cancel_btn")
        _sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        _sizePolicy.setHorizontalStretch(0)
        _sizePolicy.setVerticalStretch(0)
        _sizePolicy.setHeightForWidth(self._cancel_btn.sizePolicy().hasHeightForWidth())
        self._cancel_btn.setSizePolicy(_sizePolicy)
        self._cancel_btn.clicked.connect(self.close)

        self._select_btn = QtGui.QPushButton("Select")
        self._select_btn.setObjectName("_select_btn")
        _sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        _sizePolicy.setHorizontalStretch(0)
        _sizePolicy.setVerticalStretch(0)
        _sizePolicy.setHeightForWidth(self._select_btn.sizePolicy().hasHeightForWidth())
        self._select_btn.setSizePolicy(_sizePolicy)
        self._select_btn.clicked.connect(self._on_select)

        # Disable the Select button if no task is selected and we require that
        if self._app.get_setting("require_task_selection") and \
           self._app.context.task is None:
            self._select_btn.setEnabled(False)

        # lay out the widgets
        main_layout = QtGui.QVBoxLayout(self)
        main_layout.setObjectName("main_layout")
        main_layout.setAlignment(QtCore.Qt.AlignHCenter)
        main_layout.addWidget(self._context_widget)
        main_layout.addStretch()
        main_layout.addSpacing(17)

        horiz_layout = QtGui.QHBoxLayout()
        horiz_layout.setObjectName("horiz_layout")
        horiz_layout.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignRight)
        horiz_layout.addWidget(self._cancel_btn)
        horiz_layout.addWidget(self._select_btn)
        main_layout.addLayout(horiz_layout)

        # you can set a context using the `set_context()` method. Here we set it
        # to the current bundle's context
        self._context_widget.set_context(self._app.context)

    def closeEvent(self, event):
        """
        Executed when the main dialog is closed.
        All worker threads and other things which need a proper shutdown
        need to be called here.
        """

        logger.debug("CloseEvent Received. Begin shutting down UI.")

        # register the data fetcher with the global schema manager
        shotgun_globals.unregister_bg_task_manager(self._task_manager)

        try:
            # shut down main threadpool
            self._task_manager.shut_down()
        except Exception:
            logger.exception("Error running closeEvent()")

        # ensure the context widget's recent contexts are saved
        self._context_widget.save_recent_contexts()

    def _on_item_context_change(self, context):
        """
        This method is connected above to the `context_changed` signal emitted
        by the context selector widget.

        For demo purposes, we simply display the context in a label.
        """
        # typically the context would be set by some external process. for now,
        # we'll just re-set the context based on what was selected. this will
        # have the added effect of populating the "recent" items in the drop
        # down list
        self._context_widget.set_context(context)

        # Disable the Select button if no task is selected and we require that
        if self._app.get_setting("require_task_selection") and \
           context.task is None:
            self._select_btn.setEnabled(False)
        else:
            self._select_btn.setEnabled(True)

    def _on_select(self):
        """
        This method is connected above to the select button to show switching
        between enabling and disabling editing of the context.
        """
        selected_context = self._context_widget._context
        if selected_context != self._app.context:
            sgtk.platform.change_context(selected_context)

        self.close()
