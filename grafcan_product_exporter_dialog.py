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
import errno
import shutil
from datetime import datetime

from PyQt4 import QtGui, uic

from qgis.core import QgsMapLayerRegistry

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

        basedirectory = os.path.dirname(__file__)
        fillpath = lambda x: os.path.join(basedirectory, x)
        setting, filenamelog = map(fillpath, ['metadata.txt', 'debug.log'])

        # log file
        self.DEBUG = True
        self.filenamelog = filenamelog
        self.log("init appp")

        # events
        self.btnBox.accepted.connect(self.onClick_btnBoxAccepted)
        self.btnBox.rejected.connect(self.onClick_btnBoxRejected)

    def onClick_btnBoxAccepted(self):
        """
        :param layerid:
        :return:
        """
        # directory = '/tmp'
        self.log('init copy')

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
                self, u'',
                u'Va a copiar {0} que ocupan {1:.3f} MB. Desea continuar?'.format( # noqa
                    len(features),
                    (peso / 1024.0 / 1000.0)
                ),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            )
            if reply == QtGui.QMessageBox.Yes:
                directory = QtGui.QFileDialog.getExistingDirectory(
                    self, u'Selecciona carpeta de destino'
                )
                if directory:
                    progressDialog = QtGui.QProgressDialog(self)
                    progressDialog.setCancelButtonText("&Cancelar")
                    progressDialog.setRange(0, len(features))
                    progressDialog.setWindowTitle("Copiado")
                    i = 0
                    for f in features:
                        i += 1
                        progressDialog.setValue(i)
                        progressDialog.setLabelText(
                            u"Copiando fichero %d de %d..." % (
                                i, len(features)
                            )
                        )
                        QtGui.qApp.processEvents()
                        if progressDialog.wasCanceled():
                            break
                        # self.log("-- {} {}".format(i, len(features)))
                        src = dest = f['ruta']
                        src = src.replace('home', 'mnt')
                        dest = dest.replace('/home/datos', directory)
                        self.copyLargeFile(src, dest)

                    progressDialog.close()
                    QtGui.QMessageBox.information(
                        self,
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

    def copyLargeFile(self, src, dest, buffer_size=16000):
        """"""
        if not os.path.exists(os.path.dirname(dest)):
            try:
                os.makedirs(os.path.dirname(dest))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        with open(src, 'rb') as fsrc:
            with open(dest, 'wb') as fdest:
                shutil.copyfileobj(fsrc, fdest, buffer_size)

    def onClick_btnBoxRejected(self):
        pass

    def isLoadLayer(self, layername):
        """"""
        aux = QgsMapLayerRegistry.instance().mapLayersByName(layername)
        self.log("%s %s" % (aux, layername))
        return True if len(aux) > 0 else False

    def log(self, msg):
        """"""
        if self.DEBUG:
            f = open(self.filenamelog, "a")
            f.write(
                "%s: %s\n" % (datetime.now(), msg.encode('utf-8'))
            )
            f.close()
