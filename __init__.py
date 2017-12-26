# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GrafcanProductExporter
                                 A QGIS plugin
 Exportador Distribuidor de productos
                             -------------------
        begin                : 2017-12-26
        copyright            : (C) 2017 by Félix
        email                : fhernandeze@grafcan.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GrafcanProductExporter class from file GrafcanProductExporter.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .grafcan_product_exporter import GrafcanProductExporter
    return GrafcanProductExporter(iface)
