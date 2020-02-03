# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qweb
                                 A QGIS plugin
 This plugin is for web
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-02-08
        git sha              : $Format:%H$
        copyright            : (C) 2019 by KIOS Research Center
        email                : mariosmsk@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QSettings, QTranslator, qVersion, QCoreApplication, Qt, QUrl
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QAction, QShortcut
# Initialize Qt resources from file resources.py
from .resources import *
from PyQt5.QtNetwork import QNetworkProxyFactory

from PyQt5.QtWebKit import QWebSettings

# Import the code for the DockWidget
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Qweb_dockwidget_base.ui'))


class QwebDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(QwebDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


class Qweb:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Qweb_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Qweb')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Qweb')
        self.toolbar.setObjectName(u'Qweb')

        #print "** INITIALIZING Qweb"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Qweb', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Qweb/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Qweb'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.dockwidget = QwebDockWidget()

        self.dockwidget.back.setText('')
        self.dockwidget.back.setIcon(QIcon(':/plugins/Qweb/icons/back.png'))
        self.dockwidget.back.clicked.connect(self.on_backButton_clicked)

        self.dockwidget.forward.setText('')
        self.dockwidget.forward.clicked.connect(self.on_forwardButton_clicked)
        self.dockwidget.forward.setIcon(QIcon(':/plugins/Qweb/icons/forward.png'))

        self.dockwidget.refresh.setText('')
        self.dockwidget.refresh.clicked.connect(self.on_refreshButton_clicked)
        self.dockwidget.refresh.setIcon(QIcon(':/plugins/Qweb/icons/refresh.png'))

        self.dockwidget.home.setText('')
        self.dockwidget.home.clicked.connect(self.on_homeButton_clicked)
        self.dockwidget.home.setIcon(QIcon(':/plugins/Qweb/icons/home.png'))

        self.dockwidget.home.setText('')
        self.dockwidget.home.clicked.connect(self.on_homeButton_clicked)
        self.dockwidget.home.setIcon(QIcon(':/plugins/Qweb/icons/home.png'))

        self.dockwidget.zoom_in.setText('')
        self.dockwidget.zoom_in.clicked.connect(self.on_actionZoomIn_triggered)
        self.dockwidget.zoom_in.setIcon(QIcon(':/plugins/Qweb/icons/mActionZoomIn.svg'))

        self.dockwidget.zoom_out.setText('')
        self.dockwidget.zoom_out.clicked.connect(self.on_actionZoomOut_triggered)
        self.dockwidget.zoom_out.setIcon(QIcon(':/plugins/Qweb/icons/mActionZoomOut.svg'))

        self.dockwidget.webView.loadFinished.connect(self.on_load_finished)


    #--------------------------------------------------------------------------
    def on_load_finished(self):
        self.dockwidget.lineEdit.setText(self.dockwidget.webView.url().toString())

    def on_actionZoomIn_triggered(self):
        current = self.dockwidget.webView.zoomFactor()
        self.dockwidget.webView.setZoomFactor(current + 0.1)

    def on_actionZoomOut_triggered(self):
        current = self.dockwidget.webView.zoomFactor()
        self.dockwidget.webView.setZoomFactor(current - 0.1)

    def on_homeButton_clicked(self):
        url = "https://www.google.com"
        self.dockwidget.webView.load(QUrl(url))
        self.dockwidget.lineEdit.setText(url)

    def on_refreshButton_clicked(self):
        self.dockwidget.webView.reload()

    def on_backButton_clicked(self):
        self.dockwidget.webView.back()

    def on_forwardButton_clicked(self):
        self.dockwidget.webView.forward()

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING Qweb"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

    def open_url(self, url):
        self.run()
        self.url_corr(url)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD Qweb"

        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Qweb'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def load_url(self):

        url = self.dockwidget.lineEdit.text()
        self.url_corr(url)

    def url_corr(self, url):

        if 'file://' in url or "https://" in url:
            url = url

        else:

            if "www." not in url and ".com" not in url:
                url = "https://www.google.com/search?q=" + url

            if "https://" not in url:
                url = "https://" + url

        self.dockwidget.webView.load(QUrl(url))
        self.dockwidget.lineEdit.setText(url)

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True
            if self.dockwidget == None:
                return

            self.dockwidget.lineEdit.returnPressed.connect(self.load_url)
            QNetworkProxyFactory.setUseSystemConfiguration(True)
            QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
            self.dockwidget.webView.settings().setAttribute(QWebSettings.PluginsEnabled, True)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()