# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GrafcanProductExporterDialog
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


 # ProgressBar: https://fredrikaverpil.github.io/2015/05/12/file-copy-progress-window-with-pyqt-pyside-and-shutil/
 # http://nullege.com/codes/show/src@p@y@PyQt4-HEAD@examples@dialogs@findfiles.py/87/PyQt4.QtGui.QFileDialog.getExistingDirectory

"""

import os
from PyQt4 import QtGui, uic

from utils import Utils


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'grafcan_product_exporter_dialog_base.ui'))


class GrafcanProductExporterDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GrafcanProductExporterDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.chkCloud.setVisible(False)

        self.plugin_dir = os.path.dirname(__file__)

        # log file
        self.iface = self

        self.utils = Utils()
        self.layer = None
        self.numSelectedFeatures = 0
        self.DEBUG = True
        self.sleepTime = 100
        self.setting = os.path.join(self.plugin_dir, 'metadata.txt')
        self.utils.filenamelog = os.path.join(self.plugin_dir, 'debug.log')
        self.utils.log("init app")

        # events
        self.btnBox.accepted.connect(self.onClick_btnBoxAccepted)
        # self.btnBox.rejected.connect(self.onClick_btnBoxRejected)

    def onClick_btnBoxAccepted(self):
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
            self.iface,
            u'',
            u'Va a copiar {0} que ocupan {1:.3f} MB. Desea continuar?'.format( # noqa
                self.numSelectedFeatures,
                (peso / 1024.0 / 1000.0)
            ),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        )
        if reply == QtGui.QMessageBox.Yes:
            directory = QtGui.QFileDialog.getExistingDirectory(
                self.iface,
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
