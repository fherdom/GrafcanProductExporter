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
 * https://nyalldawson.net/2016/10/speeding-up-your-pyqgis-scripts/
"""
import os.path

from PyQt4.QtCore import (
    QSettings, QTranslator, qVersion, QCoreApplication
)
from PyQt4 import QtGui

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from grafcan_product_exporter_dialog import GrafcanProductExporterDialog
from utils import Utils


class GrafcanProductExporter:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """"""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
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

        self.actions = []
        self.menu = self.tr(u'&Exportador Distribuidor de productos')
        self.toolbar = self.iface.addToolBar(u'GrafcanProductExporter')
        self.toolbar.setObjectName(u'GrafcanProductExporter')

        # Custom
        self.utils = Utils()
        self.layer = None
        self.numSelectedFeatures = 0
        self.DEBUG = True
        self.sleepTime = 100
        self.setting = os.path.join(self.plugin_dir, 'metadata.txt')
        self.utils.filenamelog = os.path.join(self.plugin_dir, 'debug.log')
        self.utils.log("init app")

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
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
        """Add a toolbar icon to the toolbar."""
        # Create the dialog (after translation) and keep reference
        self.dlg = GrafcanProductExporterDialog()
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
        del self.toolbar

    def run(self):
        """"""
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass

    def process(self):
        """"""
        self.utils.log('init copy process')
        # self.utils.showMessageBar(self.iface, u'init copy proccess')

        # check layer, fields
        self.layer = self.utils.isValidLayer('productos', [u'ruta', u'peso'])
        if not self.layer:
            # self.utils.showMessageBar(self.iface, u'Capa no válida')
            self.utils.showMessage(self.iface, u'Capa no válida')
            return False

        # check num selected
        self.numSelectedFeatures = self.layer.selectedFeatureCount()
        if self.numSelectedFeatures == 0 or \
                self.numSelectedFeatures > 1000:
                self.utils.showMessage(
                    self.iface,
                    u'Debe seleccionar entre 1 y 1000 elementos',
                )
                return False

        # calculate size
        peso = self.utils.calPesoRequest(self.iface, self.layer)
        # peso = self.utils.calPeso(self.iface, self.layer)
        # self.utils.showMessageBar(self.iface, u'{}'.format(peso))

        # ask for confirmation
        reply = QtGui.QMessageBox.question(
            self.iface.mainWindow(),
            u'',
            u'Va a copiar {0} que ocupan {1:.3f} MB. Desea continuar?'.format( # noqa
                self.numSelectedFeatures,
                (peso / 1024.0 / 1000.0)
            ),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        )
        if reply == QtGui.QMessageBox.Yes:
            directory = QtGui.QFileDialog.getExistingDirectory(
                self.iface.mainWindow(),
                u'Selecciona carpeta de destino'
            )

            # copy files
            self.utils.copyRutaRequest(
                self.iface,
                self.layer,
                self.numSelectedFeatures,
                peso,
                directory
            )
        else:
            return False
        return True
