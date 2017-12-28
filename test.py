# layer = iface.mapCanvas().currentLayer()
import processing
import timeit
from PyQt4.QtGui import QProgressDialog
from PyQt4.QtCore import QSettings


bar = QProgressDialog()
bar.show()
bar.setRange(0, 0)

layer = iface.activeLayer()

print("numFeatures", layer.selectedFeatureCount())

request = QgsFeatureRequest().setFlags(
    QgsFeatureRequest.NoGeometry
).setSubsetOfAttributes(
    ['peso', 'ruta'], layer.fields()
).setFilterFids(
    layer.selectedFeaturesIds()
)


# los ids q devuelve no son pks, sino internos...
# print(layer.selectedFeaturesIds())


def option1():
    peso = 0
    for idx, feature in enumerate(layer.getFeatures(request)):
        peso += feature['peso']
        print(feature['ruta'])
    print("peso", peso)

def option1_1():
    peso = 0
    for feature in layer.getFeatures(request):
        peso += feature['peso']
    print("peso", peso)


def option1_2():
    peso = 0
    features = processing.features(layer)
    for feature in features:
        peso += feature['peso']
    print("peso", peso)


def option2():
    peso = 0
    for idx, feature in enumerate(layer.selectedFeatures()):
        peso += feature['peso']
    print("peso", peso)
    
def option3(ids):
    qs = QSettings()
    """
    for k in sorted(qs.allKeys()):
        print k
    """
    print("username", qs.value("PostgreSQL/connections/Productos/username"))
           
    """
    db = QSqlDatabase.addDatabase('QPSQL')
    qry = QSqlQuery(db)
    sql = "select sum(peso) from ventas.productos where id in (8860, 12217)"
    qry.prepare(sql)
    qry.addBindValue(ids)
    qry.exec_()
    """


"""
start = timeit.default_timer()
option1()
stop = timeit.default_timer()
total_time = stop - start
print("option1 (segundos) ", total_time)
"""


print()
start = timeit.default_timer()
option1_1()
stop = timeit.default_timer()
total_time = stop - start
print("option1_1 (segundos)", total_time)

print()
start = timeit.default_timer()
option1_2()
stop = timeit.default_timer()
total_time = stop - start
print("option1_2 (segundos)", total_time)


"""
print()
start = timeit.default_timer()
option2()
stop = timeit.default_timer()
total_time = stop - start
print("option2 (segundos)", total_time)
"""

# option3([1,2])

bar.close()