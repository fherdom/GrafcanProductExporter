# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GrafcanProductExporter
                                 A QGIS plugin
 Exportador Distribuidor de productos
                              -------------------
        begin                : 2017-12-26
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Félix
        email                : fhernandeze@grafcan.com
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
import os.path
import errno
import shutil
from datetime import datetime

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4 import QtGui
from qgis.core import QgsMapLayerRegistry
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
# from grafcan_product_exporter_dialog import GrafcanProductExporterDialog


class GrafcanProductExporter:
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
            'GrafcanProductExporter_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Exportador Distribuidor de productos')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GrafcanProductExporter')
        self.toolbar.setObjectName(u'GrafcanProductExporter')

        basedirectory = os.path.dirname(__file__)
        fillpath = lambda x: os.path.join(basedirectory, x)
        setting, filenamelog = map(fillpath, ['metadata.txt', 'debug.log'])

        self.DEBUG = True

        self.filenamelog = filenamelog

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
        return QCoreApplication.translate('GrafcanProductExporter', message)

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
        parent=None
    ):
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

        # Create the dialog (after translation) and keep reference
        # self.dlg = GrafcanProductExporterDialog()

        icon = QtGui.QIcon(icon_path)
        action = QtGui.QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GrafcanProductExporter/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Exportador Distribuidor de productos'),
            # callback=self.run,
            callback=self.process,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Exportador Distribuidor de productos'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass


    def process(self):
        """"""
        self.log('init copy process')

        if self.isLoadLayer('productos'):
            layerList = QgsMapLayerRegistry.instance(
            ).mapLayersByName('productos')
            if layerList:
                layer = layerList[0]
            features = layer.selectedFeatures()
            peso = 0
            for f in features:
                peso += int(f['peso'])

            reply = QtGui.QMessageBox.question(
                self.iface.mainWindow(),
                u'',
                u'Va a copiar {0} que ocupan {1:.3f} MB. Desea continuar?'.format( # noqa
                    len(features),
                    (peso / 1024.0 / 1000.0)
                ),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            )
            if reply == QtGui.QMessageBox.Yes:
                directory = QtGui.QFileDialog.getExistingDirectory(
                    self.iface.mainWindow(),
                    'Selecciona carpeta de destino'
                )
                if directory:
                    progressDialog = QtGui.QProgressDialog(self.iface.mainWindow())
                    progressDialog.setCancelButtonText("&Cancelar")
                    progressDialog.setRange(0, len(features))
                    progressDialog.setWindowTitle("Copiado")
                    i = 0
                    for f in features:
                        i += 1
                        progressDialog.setValue(i)
                        progressDialog.setLabelText(
                            "Copiando fichero %d de %d..." % (i, len(features))
                        )
                        QtGui.qApp.processEvents()
                        if progressDialog.wasCanceled():
                            break
                        # self.log("-- {} {}".format(i, len(features)))
                        src = dest = f['ruta']
                        src = src.replace('home', 'mnt')
                        self.copyLargeFile(src, dest)
                        dest = dest.replace('/home/datos', directory)

                    progressDialog.close()
                    QtGui.QMessageBox.information(
                        self.iface.mainWindow(),
                        u'Mensaje',
                        u'Proceso completado {0:.3f}MB'.format(
                            peso / 1024.0 / 1000.0
                        ),
                        QtGui.QMessageBox.Ok
                    )
                    self.log(
                        'Copiados {0} {1:.3f}'.format(
                            len(features), (peso / 1024.0 / 1000)
                        )
                    )
            else:
                self.log('Copia cancelada')

        self.log('end copy process')


    def copyLargeFile(self, src, dest, buffer_size=16000):
        """
        :param layerid:
        :return:
        """
        if not os.path.exists(os.path.dirname(dest)):
            try:
                os.makedirs(os.path.dirname(dest))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        with open(src, 'rb') as fsrc:
            with open(dest, 'wb') as fdest:
                shutil.copyfileobj(fsrc, fdest, buffer_size)


    def isLoadLayer(self, layername):
        """
        :param layerid:
        :return:
        """
        aux = QgsMapLayerRegistry.instance().mapLayersByName(layername)
        self.log("%s %s" % (aux, layername))
        return True if len(aux) > 0 else False


    def log(self, msg):
        """
        :param layerid:
        :return:
        """
        if self.DEBUG:
            f = open(self.filenamelog, "a")
            f.write(
                "%s: %s\n" % (datetime.now(), msg.encode('utf-8'))
            )
            f.close()
