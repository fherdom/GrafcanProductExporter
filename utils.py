# -*- coding: utf-8 -*-
import os.path
import errno
import shutil
import timeit
from datetime import datetime

from PyQt4 import QtGui, QtCore
from qgis.core import QgsMapLayerRegistry, QgsFeatureRequest

RUTA = '/mnt'


class Utils:

    def __init__(self):
        """"""
        self.DEBUG = True
        self.filenamelog = None
        self.list = []

    def log(self, msg):
        """"""
        if self.DEBUG:
            f = open(self.filenamelog, "a")
            f.write(
                "%s: %s\n" % (datetime.now(), msg.encode('utf-8'))
            )
            f.close()

    def showMessageBar(self, iface, msg):
        """"""
        iface.messageBar().pushInfo(
            u"Exportador:", msg
        )

    def showMessage(self, iface, msg):
        """"""
        QtGui.QMessageBox.information(
            iface.mainWindow(),
            u'Información',
            u'{}'.format(msg),
            QtGui.QMessageBox.Ok
        )

    def isValidLayer(self, layername, fields):
        """"""
        layers = QgsMapLayerRegistry.instance().mapLayersByName(layername)
        if len(layers) == 0:
            return None
        layer = layers[0]
        field_names = set([field.name() for field in layer.pendingFields()])
        return layer if set(fields).issubset(field_names) else None

    def calPesoRequest(self, iface, layer):
        """"""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
            QtCore.Qt.WaitCursor))
        # request
        request = QgsFeatureRequest().setFlags(
            QgsFeatureRequest.NoGeometry
        ).setSubsetOfAttributes(
            ['pk', 'peso', 'ruta'], layer.fields()
        ).setFilterFids(
            layer.selectedFeaturesIds()
        )
        start = timeit.default_timer()
        peso = 0
        for idx, feature in enumerate(layer.getFeatures(request)): # TODO: 171227, problem with enumerate(layer.getFeatures(request)) is very slow!!!!
            peso += int(feature['peso'])
            self.list.append([feature['pk'], feature['peso'], feature['ruta']])

        stop = timeit.default_timer()
        total_time = stop - start
        if self.DEBUG:
            self.log('calPesoRequest {}, time: {}'.format(peso, total_time))
        QtGui.QApplication.restoreOverrideCursor()
        return peso

    def calPeso(self, iface, layer):
        """"""
        # request
        peso = 0
        for idx, feature in enumerate(layer.selectedFeatures()):
            peso += int(feature['peso'])
        return peso

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

    def copyRutaRequest(
        self, iface, layer, numSelectedFeatures, peso, directory
    ):
        """"""
        # progress
        # option #1
        progressDialog = QtGui.QProgressDialog(iface.mainWindow())
        progressDialog.setCancelButtonText("&Cancelar")
        progressDialog.setRange(0, numSelectedFeatures)
        progressDialog.setWindowTitle("Copiando")

        """
        # option #2
        progress = QtGui.QProgressBar()
        progress.setMaximum(self.numSelectedFeatures)
        progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        progressMessageBar.layout().addWidget(progress)
        iface.messageBar().pushWidget(
            progressMessageBar, iface.messageBar().INFO
        )
        """

        # request
        """
        request = QgsFeatureRequest()
        request.setFlags(QgsFeatureRequest.NoGeometry)
        request.setSubsetOfAttributes(['ruta'], layer.fields())
        request.setFilterFids(layer.selectedFeaturesIds())
        """
        # for idx, f in enumerate(layer.getFeatures(request)):
        for idx, f in enumerate(self.list):

            # option #1
            progressDialog.setValue(idx)
            progressDialog.setLabelText(
                u"Copiando fichero %d de %d..." % (idx, numSelectedFeatures)
            )
            QtGui.qApp.processEvents()
            if progressDialog.wasCanceled():
                return False

            # option #2
            """
            percent = idx / float(self.numSelectedFeatures) * 100
            iface.mainWindow().statusBar().showMessage(
                "Processed {} %".format(int(percent))
            )
            """

            # src = dest = f['ruta']
            src = dest = f[2]
            src = src.replace('home', RUTA)
            dest = dest.replace('/home/datos', directory)
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                QtCore.Qt.WaitCursor))
            self.copyLargeFile(src, dest)
            QtGui.QApplication.restoreOverrideCursor()

        progressDialog.close()

        # option #2
        """
        iface.messageBar().clearWidgets()
        iface.mainWindow().statusBar().clearMessage()
        """

        self.showMessage(
            iface,
            u'Proceso completado {0:.3f}MB'.format(
                peso / 1024.0 / 1000.0
            )
        )

    ############################################################

    def step_001(self):
        """"""
        self.iface.messageBar().pushInfo(
            u"Exportador:", u"Calculando peso"
        )

    def step_002(self, layer):
        """"""
        if self.DEBUG:
            self.log('calculate peso')
        request = QgsFeatureRequest(
        ).setFlags(
            QgsFeatureRequest.NoGeometry
        ).setSubsetOfAttributes(
            ['peso'], layer.fields()
        ).setFilterFids(
            layer.selectedFeaturesIds()
        )
        peso = 0
        # for idx, f in enumerate(layer.selectedFeatures()):
        for idx, f in enumerate(layer.getFeatures(request)):
            peso += int(f['peso'])
            self.log('{}'.format(peso))
        if self.DEBUG:
            self.log('end calculate peso')
