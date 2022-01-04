from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
from osgeo import gdal, ogr, osr
import numpy as np
import random
#import osr
import os
from osgeo import gdalconst
import math
import csv
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.core import QgsRasterLayer
import time
import processing
from numpy import genfromtxt
import csv


DialogUi , DialogType= uic.loadUiType(os.path.join(os.path.dirname(__file__),'aleatoriosingles.ui'))
#DialogUi , DialogType= uic.loadUiType('/home/laige/Documentos/evaluacion/aleatorios/aleatoriosingles.ui')

class aleatorios(DialogType,DialogUi):
    def __init__ (self):
        super().__init__()
        self.pathRaster = ''
        self.setupUi(self)
        self.loadLayers(2)
        self.mapa.currentIndexChanged.connect(self.actualizarComboBox)
        self.aceptar.clicked.connect(self.principal)
        self.guardarResultado.clicked.connect(self.guardarArch)
        self.bucarMapa.clicked.connect(self.abrirShp)
        self.cancelar.clicked.connect(self.close)
        self.prueba = True
        self.areaHa = []
        self.clases = []
        self.data = ''
        self.conteo = 0

    def comprobarInterfaz(self):#Funcion que valida algunas caracteristicas de la interfaz del plugin 
        self.prueba =  True        
        error = 0
        if(self.mapa.currentData() == None):
            QMessageBox.information(self,"Error","Seleccionar un mapa tematico",QMessageBox.Ok)
            #self.loadLayers(2)
            self.prueba = False
        elif(self.distancia.text() == ""):
            #error = 1
            QMessageBox.information(self,"Error","Ingresar una distancia minima",QMessageBox.Ok)
            self.prueba = False            
        elif(self.muestras_peque.text() == ""):
            QMessageBox.information(self,"Error","Ingresar un número de muestras para clases raras",QMessageBox.Ok)
            self.prueba = False  
        elif(self.textResultado.text() == ""):
            QMessageBox.information(self,"Error","Seleccionar una carpeta para guardar los resultados",QMessageBox.Ok)
            self.prueba = False
        try:
            if self.distancia.text() != "":
                if(int(self.distancia.text()) < 50):
                    QMessageBox.information(self,"Error","Distancia minima 50 m",QMessageBox.Ok)
                    self.prueba = False  
        except ValueError:    
            QMessageBox.information(self,"Error","La distancia debe de ser númerico",QMessageBox.Ok)
            self.prueba = False
        try:
            if self.muestras_peque.text() != "":
                if(int(self.muestras_peque.text()) < 10):
                    QMessageBox.information(self,"Error","Número de muestras para clases raras debe ser un minimo de 50",QMessageBox.Ok)
                    self.prueba = False  
        except ValueError:    
            QMessageBox.information(self,"Error","Número de muestras para clases raras debe ser númerico",QMessageBox.Ok)
            self.prueba = False            
        #return self.prueba


    def abrirShp(self):#Funcion que abre cuadro de dialogo para buscar las muestras de entrenamiento
        options = QFileDialog.Option()
        options |= QFileDialog.DontUseNativeDialog 
        fichero = QtWidgets.QFileDialog.getOpenFileName(self,"Abrir Fichero","","Mapa de referencia(*.tif);;All Files (*)", options=options)
        if fichero[0] != '':
            self.rutaSHPMuestras=fichero[0]
            self.mapa.addItem(self.rutaSHPMuestras,1)
            self.mapa.setCurrentText(self.rutaSHPMuestras)
            #self.textMuestras.setText(self.rutaSHPMuestras)
        
        
    def loadLayers(self,vecras):#Carga las capas que se encuentren en el proyecto de Qgis
        self.mapa.clear()
        lista = QgsProject.instance().mapLayers().values()
        if(vecras == 1):
            self.mapa.addItem('')
            for layer in lista:
                if(str(layer.type()) == "QgsMapLayerType.VectorLayer"):
                    self.mapa.addItem(layer.name(), layer.id())
        else:
            self.mapa.addItem('')
            for layer in lista:
                if str(layer.type()) == "QgsMapLayerType.RasterLayer":
                    self.mapa.addItem(layer.name(), layer.id())


    def actualizarComboBox(self):#Extrae todas las columnas de tipo texto y numerico del vector de muestras
        nombre = self.mapa.currentText()
        
        if os.path.isfile(nombre):
            
            layer = QgsRasterLayer(self.rutaSHPMuestras, "aleatorios", "gdal")
        else:
            idLayerQg = self.mapa.currentData()
            layer = QgsProject.instance().mapLayer(str(idLayerQg))
            
        #if str(self.layer.type()) == "QgsMapLayerType.RasterLayer":
        if layer != None:
        #try:
            self.pathRaster = layer.dataProvider().dataSourceUri()
            self.data = gdal.Open(self.pathRaster, gdal.GA_ReadOnly) 
            getProjec = self.data.GetProjection()
            band = self.data.GetRasterBand(1)
            nodata = band.GetNoDataValue()
            #x = processing.run("gdal:gdalinfo", { 'EXTRA' : '', 'INPUT' : '/home/laige/Escritorio/basura/agropecuario/chiapas_2/comb_2010_2015_reclas_webm.tif', 'MIN_MAX' : False, 'NOGCP' : False, 'NO_METADATA' : False, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'STATS' : False })
            #print(x)
            #print (data.GetMetadata())
            direccion = os.path.dirname(os.path.abspath(self.pathRaster))
            encontrarMetros = getProjec.find("metre")
            processing.run("qgis:rasterlayeruniquevaluesreport", {'BAND':1, 'INPUT': self.pathRaster,'OUTPUT_TABLE':direccion+'/area.csv'})
            #data = genfromtxt(direccion+'/area.csv', delimiter=',',skip_header=1)
            with open(direccion+'/area.csv', encoding="latin-1") as File:
                reader = csv.reader(File, delimiter=',', quotechar=',',quoting=csv.QUOTE_MINIMAL)
                inicio = 0
                for row in reader:
                    if inicio != 0:
                        #inicio = 1
                        self.areaHa.append(float(row[2])/10000)
                        self.clases.append(int(float(row[0])))
                    else:
                        inicio = 1
            print(self.areaHa)
            print(self.clases)
            #self.areaHa = data[0:,2]/10000
            #self.clases = data[0:,0].astype(int)
            if encontrarMetros != -1:
                self.prueba = True
                #band = data.GetRasterBand(1).ReadAsArray().astype(int)
                #unicos = np.unique(band)
                #unicos = unicos.astype(str)
                self.tableWidget.setRowCount(len(self.clases))
                i = 0
                for clase in self.clases:
                    if str(clase) != str(int(nodata)):
                        self.tableWidget.setItem(i,0, QTableWidgetItem(str(clase)))
                        self.tableWidget.setItem(i,1, QTableWidgetItem('.6'))
                        i = i+1
            
            else:
                QMessageBox.information(self,"Error","El raster debe de estar en proyecciones metricas",QMessageBox.Ok)
                self.prueba = False
                self.mapa.clear()
                self.loadLayers(2)
        else:
            self.prueba = False
            
            
    def guardarArch(self):#Copia la direccion del archivo seleccionado y se pega en la caja de textos textResultado
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dire = QFileDialog.getExistingDirectory(self, "Directorio","",
                                       QFileDialog.ShowDirsOnly
                                       | QFileDialog.DontResolveSymlinks)
        if dire != '':
            self.textResultado.setText(dire)
            self.direccionGuardar = dire
            os.chdir(self.direccionGuardar)
            
    def calcularArea(self,direccion,geotr,nodata):   
        #processing.run("qgis:rasterlayeruniquevaluesreport", {'BAND':1, 'INPUT': direccion,'OUTPUT_TABLE':'area.csv'})
        '''unicos = np.unique(band)
        unicos = unicos.astype(str)
        pixel_area = abs(geotr[1] * geotr[5])
        if nodata != None:
            matrizAreaClass = np.empty((len(unicos)-1, 2)).astype(int)
        i = 0
        for clase in unicos:
            if str(clase) != str(int(nodata)):
                condition = np.bitwise_not(band!=int(clase))
                totalClase = np.extract(condition, band)
                total = len(totalClase)
                matrizAreaClass[i][0] = round(float(str((total * pixel_area)/10000)),0)
                matrizAreaClass[i][1] = clase
                i = i + 1'''
        
        #data = genfromtxt('area.csv', delimiter=',',encoding= 'bytes')
        #areaHa = data[1:,2]/10000
        #clases = data[1:,0]
        matrizAreaClass = np.empty((len(self.clases), 2)).astype(int)
        i = 0
        for clase in self.clases:
             matrizAreaClass[i][0] = self.areaHa[i]
             matrizAreaClass[i][1] = clase
             i += 1
        print(matrizAreaClass)
        #print(self.areaHa)
        #print(self.clases)
        return  matrizAreaClass

    def principal(self,raster):
        start_time = time.time()
        if self.conteo == 0:
            #os.path.exists('testfile.txt')
            self.direccion = 'RandomSample'
            #self.conteo = self.conteo +1
            for layer in  QgsProject.instance().mapLayers().values():
                capas = layer.name()
                encontrar = capas.find("RandomSample")
                if encontrar != -1:
                    self.conteo += 1
                    self.direccion = 'RandomSample'+ str(self.conteo)

        else:
            print(self.conteo)
            self.direccion = 'RandomSample'+ str(self.conteo)
            self.conteo = self.conteo +1
        try:
            self.comprobarInterfaz()
            if (self.prueba == True):
                ui,error = self.generarUi()
                if int(error) != int(1):
                    #data = gdal.Open(self.pathRaster, gdal.GA_ReadOnly) 
                    getProjec = self.data.GetProjection()
                    band = self.data.GetRasterBand(1)
                    nodata = band.GetNoDataValue()
                    encontrarMetros = getProjec.find("metre")
                    tipoData = gdal.GetDataTypeName(band.DataType)
                        
                    if encontrarMetros != -1:
                        geotr = self.data.GetGeoTransform()                    
                        #band = self.data.GetRasterBand(1).ReadAsArray().astype(int)
                        matrizAreaClass = self.calcularArea(self.pathRaster,geotr,nodata)                  
                        for n in range(11):
                            time.sleep(.01)
                            self.progressBar.setValue(n)
                        clases, aleatorios = self.numeroMuestras(ui, matrizAreaClass) 
                        for x in range(11,41):
                            time.sleep(.01)
                            self.progressBar.setValue(x)
                        #dataImg = self.data.ReadAsArray()
                        GeoTransforImg = self.data.GetGeoTransform()
                        tamanox = self.data.RasterXSize  
                        tamanoy = self.data.RasterYSize                        
                        coordenadaExtremaX = GeoTransforImg[0]+(tamanox*GeoTransforImg[1])
                        coordenadaExtremaY = GeoTransforImg[3]+(tamanoy*GeoTransforImg[5]) 
                        random.seed()
                        aleatorioX = random.randint(1, tamanox)
                        aleatorioY = random.randint(1, tamanoy)
                        distanciaX = (abs(GeoTransforImg[0]-coordenadaExtremaX))
                        distanciaY =(abs(GeoTransforImg[3]-coordenadaExtremaY))
                        promedio = (distanciaX + distanciaY)/2
                        distanciaUsuario = int(self.distancia.text())
                        numeroPuntos = (promedio/distanciaUsuario)
                        #print(numeroPuntos)
                        distanciaUsuario = 100
                        comprobarDistancia = 1
                        while numeroPuntos > 2000:
                            comprobarDistancia = 0
                            numeroPuntos = (promedio/distanciaUsuario)
                            distanciaUsuario = distanciaUsuario + 100
                        if  comprobarDistancia == 1:
                            distanciaUsuario = int(self.distancia.text())
                        
                        distancia = int((distanciaUsuario)/GeoTransforImg[1])
                        #print(distanciaUsuario)
                        #else:
                        #    distancia = int(500/GeoTransforImg[1])
                        nuevaCoordenadaY = GeoTransforImg[3]+(aleatorioY*GeoTransforImg[5])
                        nuevaCoordenadaX = GeoTransforImg[0]+(aleatorioX*GeoTransforImg[1])
                        CoordenadXOrigen = nuevaCoordenadaX
                        nuevaCoordenadaYarriba = nuevaCoordenadaY-(int(distancia)*GeoTransforImg[5])
                        coordenadaXIzquierda = nuevaCoordenadaX-(int(distancia)*GeoTransforImg[1])
                        CoordenadXOrigenIzquierda = coordenadaXIzquierda
                        proj = osr.SpatialReference(wkt=self.data.GetProjection())
                        
                        idUnico = 0
                        clasesExtraida = []
                        idClase = []
                        cordenadaX = []
                        cordenadaY = []
                        coordenadaInicial = (nuevaCoordenadaX,nuevaCoordenadaY)
                        x,y= self.transforPixel(coordenadaInicial,GeoTransforImg)
                        datoGuardar =  self.data.ReadAsArray(x,y,1,1)
                        if tipoData == 'Byte' or tipoData == 'Int16' or tipoData == 'UInt16' or tipoData == 'UInt32' or tipoData == 'Int32' or tipoData == 'CInt16' or tipoData == 'CInt32':
                            clasesExtraida.append(int(datoGuardar[0]))
                        else:
                            clasesExtraida.append(float(datoGuardar[0]))

                        idClase.append(idUnico)
                        cordenadaX.append(str(nuevaCoordenadaX))
                        cordenadaY.append(str(nuevaCoordenadaY))
                        while coordenadaExtremaY < nuevaCoordenadaY:
                            nuevaCoordenadaX = CoordenadXOrigen
                            coordenadaXIzquierda = CoordenadXOrigenIzquierda 
                            while coordenadaExtremaX > nuevaCoordenadaX:   
                                coordenadaInicial = (nuevaCoordenadaX,nuevaCoordenadaY)
                                x,y= self.transforPixel(coordenadaInicial,GeoTransforImg)
                                datoGuardar =  self.data.ReadAsArray(x,y,1,1)
                                if str(datoGuardar) != str(nodata):                                        
                                    if tipoData == 'Byte' or tipoData == 'Int16' or tipoData == 'UInt16' or tipoData == 'UInt32' or tipoData == 'Int32' or tipoData == 'CInt16' or tipoData == 'CInt32':
                                        clasesExtraida.append(int(datoGuardar[0]))
                                    else:
                                        clasesExtraida.append(float(datoGuardar[0]))
                                    idClase.append(idUnico)
                                    cordenadaX.append(str(nuevaCoordenadaX))
                                    cordenadaY.append(str(nuevaCoordenadaY))
                                    idUnico = idUnico + 1
                                nuevaCoordenadaX = nuevaCoordenadaX + (int(distancia) * GeoTransforImg[1])
                            while GeoTransforImg[0] < coordenadaXIzquierda:
                                coordenadaInicial = (coordenadaXIzquierda,nuevaCoordenadaY)
                                x,y= self.transforPixel(coordenadaInicial,GeoTransforImg)
                                datoGuardar =  self.data.ReadAsArray(x,y,1,1)
                                if str(datoGuardar) != str(nodata):                                     
                                    if tipoData == 'Byte' or tipoData == 'Int16' or tipoData == 'UInt16' or tipoData == 'UInt32' or tipoData == 'Int32' or tipoData == 'CInt16' or tipoData == 'CInt32':
                                        clasesExtraida.append(int(datoGuardar[0]))
                                    else:
                                        clasesExtraida.append(float(datoGuardar[0]))
                                    idClase.append(idUnico)
                                    cordenadaX.append(str(coordenadaXIzquierda))
                                    cordenadaY.append(str(nuevaCoordenadaY))
                                    idUnico = idUnico + 1
                                coordenadaXIzquierda = coordenadaXIzquierda - (int(distancia) * GeoTransforImg[1])    
                            nuevaCoordenadaY = nuevaCoordenadaY+(int(distancia)*GeoTransforImg[5])
                        for y in range(41,61):
                            time.sleep(.05)
                            self.progressBar.setValue(y)                            
                        while GeoTransforImg[3] > nuevaCoordenadaYarriba:
                            CoordenadXOrigen2 = CoordenadXOrigen
                            CoordenadXOrigenIzquierda2 = CoordenadXOrigenIzquierda
                            while coordenadaExtremaX > CoordenadXOrigen2:   
                                coordenadaInicial = (CoordenadXOrigen2,nuevaCoordenadaYarriba)
                                x,y= self.transforPixel(coordenadaInicial,GeoTransforImg)
                                datoGuardar =  self.data.ReadAsArray(x,y,1,1)
                                if str(datoGuardar) != str(nodata):                                     
                                    if tipoData == 'Byte' or tipoData == 'Int16' or tipoData == 'UInt16' or tipoData == 'UInt32' or tipoData == 'Int32' or tipoData == 'CInt16' or tipoData == 'CInt32':
                                        clasesExtraida.append(int(datoGuardar[0]))
                                    else:
                                        clasesExtraida.append(float(datoGuardar[0]))
                                    idClase.append(idUnico)
                                    cordenadaX.append(str(CoordenadXOrigen2))
                                    cordenadaY.append(str(nuevaCoordenadaYarriba))
                                    idUnico = idUnico + 1
                                CoordenadXOrigen2 = CoordenadXOrigen2 + (int(distancia) * GeoTransforImg[1])
                            while GeoTransforImg[0] < CoordenadXOrigenIzquierda2:
                                coordenadaInicial = (CoordenadXOrigenIzquierda2,nuevaCoordenadaYarriba)
                                x,y= self.transforPixel(coordenadaInicial,GeoTransforImg)
                                datoGuardar =  self.data.ReadAsArray(x,y,1,1)
                                if str(datoGuardar) != str(nodata):                                
                                    if tipoData == 'Byte' or tipoData == 'Int16' or tipoData == 'UInt16' or tipoData == 'UInt32' or tipoData == 'Int32' or tipoData == 'CInt16' or tipoData == 'CInt32':                                        
                                        clasesExtraida.append(int(datoGuardar[0]))
                                    else:
                                        clasesExtraida.append(float(datoGuardar[0]))
                                    idClase.append(idUnico)
                                    cordenadaX.append(str(CoordenadXOrigenIzquierda2))
                                    cordenadaY.append(str(nuevaCoordenadaYarriba))
                                    idUnico = idUnico + 1
                                CoordenadXOrigenIzquierda2 = CoordenadXOrigenIzquierda2 - (int(distancia) * GeoTransforImg[1])
                            nuevaCoordenadaYarriba = nuevaCoordenadaYarriba-(int(distancia)*GeoTransforImg[5])
                        for y in range(61,81):
                            time.sleep(.05)
                            self.progressBar.setValue(y)
                        #dataImg = None
                        self.data = None
                        puntos = self.abriraleatorios(idClase,clasesExtraida,cordenadaX,cordenadaY)
                        self.generarAleatorios(puntos,proj,aleatorios,nodata,clases,tipoData,distanciaUsuario)
                        #for y in range(81,91):
                        #    time.sleep(.05)
                        #    self.progressBar.setValue(y)
                        
                        elapsed_time = time.time() - start_time
                        print("Elapsed time: %0.10f seconds." % elapsed_time)
                        time.sleep(.01)
                        for y in range(99,101):
                            self.progressBar.setValue(y)       
                        QMessageBox.information(self,"Exito","Proceso termindado",QMessageBox.Ok)
                        capa = QgsVectorLayer(self.direccion+".shp", self.direccion, "ogr")
                        QgsProject.instance().addMapLayer(capa)
                        self.progressBar.setValue(0) 
                        self.tableWidget.clear()
                        self.tableWidget.setRowCount(0)
                        self.tableWidget.setHorizontalHeaderLabels(['Clases','valor precisión (0-1)'])
                        self.loadLayers(2)
                        self.distancia.setText('')
                        self.textResultado.setText('')
                        self.muestras_peque.setText('')  
                        self.areaHa = []
                        self.clases = []

        except PermissionError:
            QMessageBox.information(self,"Error","Permiso denegado para guardar los resultados",QMessageBox.Ok)
            self.progressBar.setValue(0)

    
    def generarUi(self):
        porcentaje = []
        allRows = self.tableWidget.rowCount()
        error = 0
        try:
            try:
                for row in range(0,allRows):            
                    twi0 = self.tableWidget.item(row,1)
                    porcentajeError = float(twi0.text())
                    if porcentajeError<=1 and porcentajeError > 0:
                        porcentaje.append(porcentajeError)
                       
                    else:
                        QMessageBox.information(self,"Error","los valores deben de estar entre 1 y 0",QMessageBox.Ok)
                        error = 1
                        break
            except ValueError:
                QMessageBox.information(self,"Error","Los valores de presición deben de ser decimales",QMessageBox.Ok)
                error = 1
                #break
        except AttributeError:
            QMessageBox.information(self,"Error","Es necesario agregar valores de presición",QMessageBox.Ok)
            error = 1
        return porcentaje, error

    def numeroMuestras(self, uis, areas):
        muestras = int(self.muestras_peque.text())
        n = []
        so = 0.02
        numcat = len(areas[:,1])
        supCat = areas[:,0]
        supTot = sum(areas[:,0])
        wi = supCat/supTot
        for ui in uis:    
            si = math.sqrt(ui*(1-ui))
            n2 = (sum(wi*si)**2)/(so**2+((1/supTot)*sum(wi*si**2)))
            n2 = round(n2,0)  
            n.append(n2)
        ni_prop = (((supCat*si)/sum(supCat*si))*n)
        ni0 = ni_prop.astype(int)
        ni_prop2 = ni0
        ni_prop2[ni_prop2 <= muestras] = muestras
        x = ni_prop.astype(int)
        columnas = [" ","Classes","area (ha)","samples_neyman","samples_adjusted"]
        self.reultados.append("Sitios optimos por clase:")
        self.reultados.append("clases\tSuperficies\tMuestras_apropiadas")
        with open("tama_muestra.csv", mode='w') as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(columnas)
                i = 0
                for dato in areas[:,1]:
                    conca = []
                    conca.append(i)
                    conca = np.concatenate((np.array(conca), dato), axis=None)
                    conca = np.concatenate((np.array(conca), areas[i,0]), axis=None)
                    conca = np.concatenate((np.array(conca), x[i]), axis=None)
                    conca = np.concatenate((np.array(conca), ni_prop2[i]), axis=None)
                    self.reultados.append(str(dato)+"\t"+str(areas[i,0])+"\t"+str(ni_prop2[i]))
                    i += 1
                    writer.writerow(conca)
        return areas[:,1].astype(float),ni_prop2
        
    
    def transforPixel(self,coordenadaInicial,imagenTransfor): 
    
        xOrigin = imagenTransfor[0]
        yOrigin = imagenTransfor[3]
        pixelWidth = imagenTransfor[1]
        pixelHeight = -imagenTransfor[5]
        p1 = coordenadaInicial
        i1 = int((p1[0] - xOrigin) / pixelWidth)
        j1 = int((yOrigin - p1[1] ) / pixelHeight)
    
        return i1,j1
    
    def guardarDatos(self,nuevaCoordenadaX,nuevaCoordenadaY,idUnico,direccion,GeoTransforImg,dataImg):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(direccion, 1)
        layer = dataSource.GetLayer()
        layer_defn = layer.GetLayerDefn()
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(nuevaCoordenadaX, nuevaCoordenadaY) #create a new point at given ccordinates
        feature = ogr.Feature(layer_defn)
        feature.SetGeometry(point)
        feature.SetField("id",idUnico)
        #layer.CreateFeature(feature)
        coordenadaInicial = (nuevaCoordenadaX,nuevaCoordenadaY)
        x,y= self.transforPixel(coordenadaInicial,GeoTransforImg)
        feature.SetField("clases",str(dataImg[y,x]))
        layer.CreateFeature(feature)
        ## lets add now a second point with different coordinates:   
        
            
            
    def iniciarSapeFile(self,direccion,spatialReference):
        driver = ogr.GetDriverByName('ESRI Shapefile') # will select the driver foir our shp-file creation.
        shapeData = driver.CreateDataSource(direccion) #so there we will store our data
        layer = shapeData.CreateLayer('customs', spatialReference, ogr.wkbPoint) #this will create a corresponding layer for our data with given spatial information.
         # gets parameters of the current shapefile
        new_field = ogr.FieldDefn("id", ogr.OFTInteger)
        new_field.SetWidth(10)
        new_field2 = ogr.FieldDefn("clases", ogr.OFTString)
        new_field2.SetWidth(20)
        layer.CreateField(new_field)
        layer.CreateField(new_field2)
        return layer
    
    
    def abriraleatorios(self,idClase,clasesExtraida,cordenadaX,cordenadaY):

        matrizAreaClass = np.empty((len(clasesExtraida), 5)).astype(str)
        i = 0
        for feature in clasesExtraida:
            matrizAreaClass[i][0] = idClase[i]
            matrizAreaClass[i][1] = feature 
            matrizAreaClass[i][2] = "POINT ("
            matrizAreaClass[i][3] = str(cordenadaX[i])
            matrizAreaClass[i][4] = str(cordenadaY[i])+")"
            i = i + 1
        return matrizAreaClass

    def guardarExitosos(self,sitios,puntosClase):
        #print(sitios)
        matrizAreaClass = np.empty((len(sitios), 5)).astype(str)
        i = 0
        for feature in sitios:
            sitio = puntosClase[puntosClase[:,0] ==feature]
            #print(sitio[0,1])
            matrizAreaClass[i][0] = sitio[0,0]
            matrizAreaClass[i][1] = sitio[0,1]
            #geom = cordenada[i].replace(","," ")
            matrizAreaClass[i][2] = str(sitio[0,2])
            matrizAreaClass[i][3] = str(sitio[0,3])
            matrizAreaClass[i][4] = str(sitio[0,4])+")"
            i = i + 1
        return matrizAreaClass
    
    def eliminarAceptados(self,sitios,puntosClase):
        for punto in sitios:
            x = np.where(puntosClase == punto)
            puntosClase = np.delete(puntosClase, int(x[0]), axis=0)    
    
    def guardarRandom(self,num, puntosClase):
        matrizAreaClass = np.empty((len(num), 5)).astype(str)
        i = 0
        for feature in num:
            sitio = puntosClase[puntosClase[:,0] ==feature]
            #print(sitio[0,1])
            matrizAreaClass[i][0] = sitio[0,0]
            matrizAreaClass[i][1] = sitio[0,1]
            #geom = cordenada[i].replace(","," ")
            matrizAreaClass[i][2] = str(sitio[0,2])
            matrizAreaClass[i][3] = str(sitio[0,3])
            matrizAreaClass[i][4] = str(sitio[0,4])+")"
            i = i + 1
        return matrizAreaClass        
    
    def validarDistancia(self,sitiosSeleccionados,randomPrimera,puntosClase,bufferDistance,layer,layer_defn,clase):
        distanciaNoValida = 0
        indices = 1

        for punto in sitiosSeleccionados: 
            indiceComparar = indices 
            indices += 1                                           
            punto3 = randomPrimera[randomPrimera[:,0] ==punto]
            geometria = punto3[0,2]+" "+punto3[0,3]+" "+punto3[0,4]
            pointBase = ogr.CreateGeometryFromWkt(geometria)  
            
            while indiceComparar < len(sitiosSeleccionados): 
                puntoComparar = randomPrimera[randomPrimera[:,0] ==sitiosSeleccionados[indiceComparar]]
                geometriaComparar = puntoComparar[0,2]+" "+puntoComparar[0,3]+" "+puntoComparar[0,4]
                pointComparar = ogr.CreateGeometryFromWkt(geometriaComparar)  
                distancia = pointBase.Distance(pointComparar)
                #if clase == 8:    
                    #print(len(sitiosSeleccionados))
                    #print(str(punto)+ " == " + str(distancia) + " - "+str(bufferDistance) +" * "+str(puntoComparar[0,0]))                    
                if distancia < bufferDistance:
                    distanciaNoValida = distanciaNoValida + 1
                    indiceEliminar = np.where(puntosClase == sitiosSeleccionados[indiceComparar])
                    puntosClase = np.delete(puntosClase, int(indiceEliminar[0]), axis=0)
                    sitiosSeleccionados.remove(str(sitiosSeleccionados[indiceComparar]))
                    #print(len(sitiosSeleccionados))
                    break
                indiceComparar += 1
            pointBase.AddPoint(pointBase.GetX(), pointBase.GetY())
            feature = ogr.Feature(layer_defn)
            feature.SetGeometry(pointBase)
            feature.SetField("id",punto3[0,0])
            feature.SetField("clases",str(punto3[0,1]))
            layer.CreateFeature(feature)
                       
        return  distanciaNoValida, puntosClase

    def buscarSitiosFaltantes(self,distanciaNoValida,puntosClase,layer,layer_defn,sitiosSeleccionados,muestrasSeleccionadas,bufferDistance):
        if distanciaNoValida != 0:
            numero = 0
            conteo = 0                    
            while numero < distanciaNoValida:
                probarBandera = True
                if len(puntosClase[:,0]) != 0:
                    sitioAleatorio = random.sample(puntosClase[:,0].tolist(),1)  
                    for sitio2 in sitiosSeleccionados: 
                        try:                            
                            punto2 = muestrasSeleccionadas[muestrasSeleccionadas[:,0] ==sitio2]
                            geometria2 = punto2[0,2]+" "+punto2[0,3]+" "+punto2[0,4]
                            point = ogr.CreateGeometryFromWkt(geometria2) 
                            punto3 = puntosClase[puntosClase[:,0] ==sitioAleatorio]
                            geometria = punto3[0,2]+" "+punto3[0,3]+" "+punto3[0,4]
                            point2 = ogr.CreateGeometryFromWkt(geometria) 
                            distancia = point2.Distance(point) 
                                                             
                            if distancia < bufferDistance:
                                print("distancia")
                                conteo = conteo + 1
                                if conteo != 2:
                                    x = np.where(puntosClase == punto3[0,0])
                                    puntosClase = np.delete(puntosClase, int(x[0]), axis=0)
                                    #mues.remove(str(punto2[0,0]))
                                    probarBandera = False
                                else:
                                    x = np.where(puntosClase == punto3[0,0])
                                    puntosClase = np.delete(puntosClase, int(x[0]), axis=0)
                                    probarBandera = False
                                    numero += 1
                                    conteo = 0
                                break
                        except ValueError:
                            probarBandera = False
                    if probarBandera:
                        numero +=1
                        point2.AddPoint(point2.GetX(), point2.GetY())
                        feature = ogr.Feature(layer_defn)
                        feature.SetGeometry(point2)
                        feature.SetField("id",punto3[0,0])
                        feature.SetField("clases",str(punto3[0,1]))
                        layer.CreateFeature(feature)
                else:
                    numero = distanciaNoValida
    def generarAleatorios(self,puntos,proj,aleatorios,nodata,clases,tipoData,distanciaOptima):
        self.iniciarSapeFile(self.direccion+".shp",proj)
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(self.direccion+".shp", 1)
        layer = dataSource.GetLayer()
        layer_defn = layer.GetLayerDefn()
        point = ogr.Geometry(ogr.wkbPoint)
        j = 0
        segmento = 18/len(clases)
        inicio = 81
        final = segmento + 81
        for clase in clases.tolist():
            if str(clase) != str(nodata):
                if tipoData == 'Byte' or tipoData == 'Int16' or tipoData == 'UInt16' or tipoData == 'UInt32' or tipoData == 'Int32' or tipoData == 'CInt16' or tipoData == 'CInt32':
                    cla = int(clase)
                else:
                    cla = float(clase)
                puntosClase =puntos[puntos[:,1] == str(cla)] 
                cantidadTotalMuestas=len(puntosClase)                   
                muestras = aleatorios[j] * 3    
                if muestras < cantidadTotalMuestas:
                    muestras = aleatorios[j]
                else:
                    muestras = cantidadTotalMuestas
                #print(muestras)
                bufferDistance = distanciaOptima+20
                #print(distanciaOptima)
                sitiosDisponibles = len(puntosClase)
                if(sitiosDisponibles >= aleatorios[j]):
                    sitiosSeleccionados = random.sample(puntosClase[:,0].tolist(),aleatorios[j])
                else:
                    sitiosSeleccionados = random.sample(puntosClase[:,0].tolist(),sitiosDisponibles)
                randomPrimera = self.guardarRandom(sitiosSeleccionados, puntosClase)                
                distanciaNoValida, puntosClase= self.validarDistancia(sitiosSeleccionados,randomPrimera,puntosClase,bufferDistance,layer,layer_defn,clase)                
                #muestrasSeleccionadas = self.guardarExitosos(sitiosSeleccionados,puntosClase)
                #self.eliminarAceptados(sitiosSeleccionados,puntosClase)
                #self.buscarSitiosFaltantes(distanciaNoValida,puntosClase,layer,layer_defn,sitiosSeleccionados,muestrasSeleccionadas,bufferDistance) 
                                                                         
                j += 1
            
            time.sleep(.1)
            
            for y in range(int(inicio),int(final)):
                self.progressBar.setValue(y) 
            inicio = final
            final = segmento + final
    
#dialogo = aleatorios()
#dialogo.show()
