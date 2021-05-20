from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
from osgeo import gdal, ogr
import numpy as np
import random
import osr
import os
from osgeo import gdalconst
import math
import csv
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.core import QgsRasterLayer
import time

DialogUi , DialogType= uic.loadUiType(os.path.join(os.path.dirname(__file__),'aleatoriosingles.ui'))
#DialogUi , DialogType= uic.loadUiType('/home/laige/Documentos/evaluacion/aleatorios/aleatoriosingles.ui')

class aleatorios(DialogType,DialogUi):
    def __init__ (self):
        super().__init__()
        self.pathRaster = ''
        self.setupUi(self)
        self.loadLayers(2)
        self.mapa.currentIndexChanged.connect(self.actualizarComboBox)
        self.aceptar.clicked.connect(self.areaRaster)
        self.guardarResultado.clicked.connect(self.guardarArch)
        self.bucarMapa.clicked.connect(self.abrirShp)
        self.cancelar.clicked.connect(self.close)
        self.prueba = True

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
                    QMessageBox.information(self,"Error","Distancia minima 100 m",QMessageBox.Ok)
                    self.prueba = False  
        except ValueError:    
            QMessageBox.information(self,"Error","La distancia debe de ser númerico",QMessageBox.Ok)
            self.prueba = False
        try:
            if self.muestras_peque.text() != "":
                if(int(self.muestras_peque.text()) < 50):
                    QMessageBox.information(self,"Error","Número de muestras para clases raras debe ser un minimo de 50",QMessageBox.Ok)
                    self.prueba = False  
        except ValueError:    
            QMessageBox.information(self,"Error","Número de muestras para clases raras debe ser númerico",QMessageBox.Ok)
            self.prueba = False            
        #return self.prueba


    def abrirShp(self):#Funcion que abre cuadro de dialogo para buscar las muestras de entrenamiento
        options = QFileDialog.Option()
        options |= QFileDialog.DontUseNativeDialog 
        fichero = QtWidgets.QFileDialog.getOpenFileName(self,"Abrir Fichero","","Shapefile Muestras(*.tif);;All Files (*)", options=options)
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
            data = gdal.Open(self.pathRaster, gdal.GA_ReadOnly) 
            getProjec = data.GetProjection()
            band = data.GetRasterBand(1)
            nodata = band.GetNoDataValue()
            encontrarMetros = getProjec.find("metre")
            if encontrarMetros != -1:
                self.prueba = True
                band = data.GetRasterBand(1).ReadAsArray().astype(int)
                unicos = np.unique(band)
                unicos = unicos.astype(str)
                self.tableWidget.setRowCount(len(unicos)-1)
                i = 0
                for clase in unicos:
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
            
        #except AttributeError:
        #      
            #
            
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

    def areaRaster(self,raster):
        try:
            self.comprobarInterfaz()
            if (self.prueba == True):
                ui,error = self.generarUi()
                if int(error) != int(1):
                    direccion = 'sitios.shp'
                    data = gdal.Open(self.pathRaster, gdal.GA_ReadOnly) 
                    getProjec = data.GetProjection()
                    band = data.GetRasterBand(1)
                    nodata = band.GetNoDataValue()
                    encontrarMetros = getProjec.find("metre")
                    tipoData = gdal.GetDataTypeName(band.DataType)
                    if encontrarMetros != -1:
                        geotr = data.GetGeoTransform()
                        pixel_area = abs(geotr[1] * geotr[5])
                        band = data.GetRasterBand(1).ReadAsArray().astype(int)
                        unicos = np.unique(band)
                        #clasesMuestras = clasesMuestras.astype(str)
                        unicos = unicos.astype(str)
                        if nodata != None:
                            matrizAreaClass = np.empty((len(unicos)-1, 2)).astype(int)
                        i = 0
                        #print(nodata)
                        for clase in unicos:
                            
                            if str(clase) != str(int(nodata)):
                                #print(clase)
                                condition = np.bitwise_not(band!=int(clase))
                                totalClase = np.extract(condition, band)
                                total = len(totalClase)
                                matrizAreaClass[i][0] = round(float(str((total * pixel_area)/10000)),0)
                                matrizAreaClass[i][1] = clase
                                i = i + 1
                        
                        for n in range(11):
                            time.sleep(.1)
                            self.progressBar.setValue(n)
                        #print(ui)
                        
                        clases, aleatorios = self.numeroMuestras(ui, matrizAreaClass) 
                        #time.sleep(1)
                        for x in range(11,41):
                            time.sleep(.1)
                            self.progressBar.setValue(x)
                        dataImg = data.ReadAsArray()
                        GeoTransforImg = data.GetGeoTransform()
                        tamanox = data.RasterXSize  
                        tamanoy = data.RasterYSize
                        
                        coordenadaExtremaX = GeoTransforImg[0]+(tamanox*GeoTransforImg[1])
                        coordenadaExtremaY = GeoTransforImg[3]+(tamanoy*GeoTransforImg[5])
                        
                        aleatorioX = random.randint(1, tamanox)
                        aleatorioY = random.randint(1, tamanoy)
                        
                        distancia = int(int(self.distancia.text())/GeoTransforImg[1])
                        #print(distancia)
                        nuevaCoordenadaY = GeoTransforImg[3]+(aleatorioY*GeoTransforImg[5])
                        nuevaCoordenadaX = GeoTransforImg[0]+(aleatorioX*GeoTransforImg[1])
                        CoordenadXOrigen = nuevaCoordenadaX
                        nuevaCoordenadaYarriba = nuevaCoordenadaY-(int(distancia)*GeoTransforImg[5])
                        coordenadaXIzquierda = nuevaCoordenadaX-(int(distancia)*GeoTransforImg[1])
                        CoordenadXOrigenIzquierda = coordenadaXIzquierda
                        proj = osr.SpatialReference(wkt=data.GetProjection())
                        
                        self.iniciarSapeFile(direccion,proj)
                        idUnico = 1
                        self.guardarDatos(nuevaCoordenadaX,nuevaCoordenadaY,idUnico,direccion,GeoTransforImg,dataImg)
                        while coordenadaExtremaY < nuevaCoordenadaY:
                            nuevaCoordenadaX = CoordenadXOrigen
                            coordenadaXIzquierda = CoordenadXOrigenIzquierda 
                            #print(nuevaCoordenadaY)
                            while coordenadaExtremaX > nuevaCoordenadaX:   
                                self.guardarDatos(nuevaCoordenadaX,nuevaCoordenadaY,idUnico,direccion,GeoTransforImg,dataImg)
                                idUnico = idUnico + 1
                                nuevaCoordenadaX = nuevaCoordenadaX + (int(distancia) * GeoTransforImg[1])
                            while GeoTransforImg[0] < coordenadaXIzquierda:
                                self.guardarDatos(coordenadaXIzquierda,nuevaCoordenadaY,idUnico,direccion,GeoTransforImg,dataImg)
                                idUnico = idUnico + 1
                                coordenadaXIzquierda = coordenadaXIzquierda - (int(distancia) * GeoTransforImg[1])    
                            nuevaCoordenadaY = nuevaCoordenadaY+(int(distancia)*GeoTransforImg[5])
                        for y in range(41,61):
                            time.sleep(.1)
                            self.progressBar.setValue(y)                            
                        while GeoTransforImg[3] > nuevaCoordenadaYarriba:
                            CoordenadXOrigen2 = CoordenadXOrigen
                            CoordenadXOrigenIzquierda2 = CoordenadXOrigenIzquierda
                            while coordenadaExtremaX > CoordenadXOrigen2:   
                                #print(str(CoordenadXOrigen),str(nuevaCoordenadaYarriba))
                                self.guardarDatos(CoordenadXOrigen2,nuevaCoordenadaYarriba,idUnico,direccion,GeoTransforImg,dataImg)
                                idUnico = idUnico + 1
                                CoordenadXOrigen2 = CoordenadXOrigen2 + (int(distancia) * GeoTransforImg[1])
                            while GeoTransforImg[0] < CoordenadXOrigenIzquierda2:
                                #print(str(CoordenadXOrigenIzquierda),str(nuevaCoordenadaYarriba))
                                self.guardarDatos(CoordenadXOrigenIzquierda2,nuevaCoordenadaYarriba,idUnico,direccion,GeoTransforImg,dataImg)
                                idUnico = idUnico + 1
                                CoordenadXOrigenIzquierda2 = CoordenadXOrigenIzquierda2 - (int(distancia) * GeoTransforImg[1])
                            nuevaCoordenadaYarriba = nuevaCoordenadaYarriba-(int(distancia)*GeoTransforImg[5])
                        for y in range(61,81):
                            time.sleep(.1)
                            self.progressBar.setValue(y)  
                        #shapeData.Destroy() #lets close the shapefile  
                        #data.GetProjectionRef()
                        puntos = self.abriraleatorios(direccion)
                        self.generarAleatorios(puntos,proj,aleatorios,nodata,clases,tipoData)
                        for y in range(81,91):
                            time.sleep(.1)
                            self.progressBar.setValue(y)
                            
                        os.remove("sitios.shp")
                        os.remove("sitios.prj")
                        os.remove("sitios.shx")
                        os.remove("sitios.dbf")
                        time.sleep(.3)
                        for y in range(91,101):
                            self.progressBar.setValue(y)       
                        QMessageBox.information(self,"Exito","Proceso termindado",QMessageBox.Ok)
                        capa = QgsVectorLayer("sitiosAleatorios.shp", "sitiosAleatorios", "ogr")
                        QgsProject.instance().addMapLayer(capa)
                        self.progressBar.setValue(0) 
                        self.tableWidget.clear()
                        self.tableWidget.setRowCount(0)
                        self.tableWidget.setHorizontalHeaderLabels(['Clases','valor precisión (0-1)'])
                        self.loadLayers(2)
                        self.distancia.setText('')
                        self.textResultado.setText('')
                        

        except PermissionError:
            QMessageBox.information(self,"Error","Permiso denegado para guardar los resultados",QMessageBox.Ok)
            self.progressBar.setValue(0)
            #else:
            #self.mapa.clear()  
                #break
    			#twi1 = self.ui.tableWidget.cellWidget(row,1)
    			#twi2 = self.ui.tableWidget.cellWidget(row,2)
            
            
            
            #for currentQTableWidgetItem in self.tableWidget.item():
            #    print(currentQTableWidgetItem.text())
            
            #self.ui.tableWidget.currentRow(), i).text()
            #return matrizAreaClass
    
    
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
                        QMessageBox.information(self,"Error","los valodes deben de estar entre 1 y 0",QMessageBox.Ok)
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
            #print(ui)
            si = math.sqrt(ui*(1-ui))
            #print(si)
            n2 = (sum(wi*si)**2)/(so**2+((1/supTot)*sum(wi*si**2)))
            n2 = round(n2,0)  
            n.append(n2)
        #ni_eq = round((n/numcat),0)
        #print(n)
        ni_prop = (((supCat*si)/sum(supCat*si))*n)
        ni0 = ni_prop.astype(int)
        ni_prop2 = ni0
        ni_prop2[ni_prop2 <= muestras] = muestras
        x = ni_prop.astype(int)
        #columnas = [" ","Clases","Superficies (ha)","Muestras_apropiadas","Muestras_sugeridas"]
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
        #n2 = sum(ni_prop)
        #print(n2)
        #i = np.where(ni0<=50) 
        #idif = np.where(ni0>50)
        #ntemp = n - len(ni0[i])*50
        #ni_temp = ((supCat[idif]*si)/sum(supCat[idif]*si))*ntemp
        #a = supCat[idif]*si[idif]
        #print(ni_temp)
        return areas[:,1].astype(float),ni_prop2
        
    
    def transforPixel(self,coordenadaInicial,imagenTransfor): 
    
        xOrigin = imagenTransfor[0]
        yOrigin = imagenTransfor[3]
        pixelWidth = imagenTransfor[1]
        pixelHeight = -imagenTransfor[5]
        
        p1 = coordenadaInicial
        #p2 = coordenadaExtrema
        
        #print(p1[0])
        #print(p2[0])
        i1 = int((p1[0] - xOrigin) / pixelWidth)
        j1 = int((yOrigin - p1[1] ) / pixelHeight)
        #i2 = int((p2[0] - xOrigin) / pixelWidth)
        #j2 = int((yOrigin - p2[1]) / pixelHeight)
        #new_cols = i2-i1
        #new_rows = j2-j1
    
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
    
    
    def abriraleatorios(self,direccion):
        aleatoreos = ogr.Open(direccion, gdalconst.GA_ReadOnly)  
        assert(aleatoreos)
        infoShp = aleatoreos.GetLayer(0)
        #features = infoShp.getFeatures()
        matrizAreaClass = np.empty((len(infoShp), 5)).astype(str)
        #print(len(matrizAreaClass))
        i = 0
        for feature in infoShp:
            geom = feature.GetGeometryRef()
            listaGeometria = str(geom).split()
            matrizAreaClass[i][0] = feature.GetField('id')
            matrizAreaClass[i][1] = feature.GetField('clases') 
            #print()
            matrizAreaClass[i][2] = listaGeometria[0]
            matrizAreaClass[i][3] = listaGeometria[1]
            matrizAreaClass[i][4] = listaGeometria[2]
            #print(matrizAreaClass[i][3])
            i = i + 1
        return matrizAreaClass
    
    def generarAleatorios(self,puntos,proj,aleatorios,nodata,clases,tipoData):
        direccion = 'sitiosAleatorios.shp'
        self.iniciarSapeFile(direccion,proj)
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(direccion, 1)
        layer = dataSource.GetLayer()
        layer_defn = layer.GetLayerDefn()
        point = ogr.Geometry(ogr.wkbPoint)
        #clases = np.unique(puntos[:,1])
        j = 0
        #print(clases)
        for clase in clases.tolist():
            
            #print(str(clase)+" clas")
            if str(clase) != str(nodata):
                #print(tipoData)
                if tipoData == 'Byte' or tipoData == 'Int16' or tipoData == 'UInt16' or tipoData == 'UInt32' or tipoData == 'Int32' or tipoData == 'CInt16' or tipoData == 'CInt32':
                    cla = int(clase)
                else:
                    cla = float(clase)
                puntosClase =puntos[puntos[:,1] == str(cla)]
                #print(puntosClase)
                longitud = len(puntosClase)
                #print(longitud)
                #print(aleatorios[i])
                numeroOptimo = aleatorios[j] * 3
                if longitud > numeroOptimo: 
                    muestras = aleatorios[j]
                    #randomPuntos = random.sample(puntosClase[:,0].tolist(),aleatorios[i])
                else: 
                    muestras = int(longitud/3)
                    #randomPuntos = random.sample(puntosClase[:,0].tolist(),int(numeroOptimo))
                
                bandera = 0
                n1 = []
                bufferDistance = int(self.distancia.text())+10
                for sitio in range(1,muestras+1):
                    print(sitio)
                    if bandera == 0:
                        n2 = random.sample(puntosClase[:,0].tolist(),1)
                        #print(n2)
                        n1.append(n2)                        
                        punto2 = puntosClase[puntosClase[:,0] ==n2] 
                        
                        geometria2 = punto2[0,2]+" "+punto2[0,3]+" "+punto2[0,4]
                        #print(geometria2)
                        point2 = ogr.CreateGeometryFromWkt(geometria2)                        
                        point.AddPoint(point2.GetX(), point2.GetY())
                        feature = ogr.Feature(layer_defn)
                        feature.SetGeometry(point)
                        feature.SetField("id",punto2[0,0])
                        feature.SetField("clases",str(punto2[0,1]))
                        layer.CreateFeature(feature)
                        bandera = 1 
                        
                    else:
                        n3 = random.sample(puntosClase[:,0].tolist(),1)
                        nuevoPunto = puntosClase[puntosClase[:,0] ==n3] 
                        geometria = nuevoPunto[0,2]+" "+nuevoPunto[0,3]+" "+nuevoPunto[0,4]
                        point3 = ogr.CreateGeometryFromWkt(geometria)
                        #poly = point.Buffer(bufferDistance)
                        #print(len(n1))
                        #prueba = True                        
                        #while prueba:
                        #print("inicio: "+str(n3))
                        bandera1 = 0
                        
                        i= 0
                        prueba = True
                        cont2 = 0
                        while prueba:                            
                            for sitioAleatorio in n1:
                                #print(sitioAleatorio)
                                #print(i)
                                punto2 = puntosClase[puntosClase[:,0] ==sitioAleatorio] 
                                geometria2 = punto2[0,2]+" "+punto2[0,3]+" "+punto2[0,4]
                                #print(geometria2)
                                point2 = ogr.CreateGeometryFromWkt(geometria2)
                                
                                distancia = point3.Distance(point2)
                                i = i +1
                                #time.sleep(1)
                                
                                while sitioAleatorio == n3:
                                    n3 = random.sample(puntosClase[:,0].tolist(),1)
                                #print(str(sitioAleatorio) + " "+ str(n3)+" dist: "+str(distancia))
                                if distancia < bufferDistance:
                                    i= 0
                                    #print("entro")
                                    bandera1 = 1
                                    n3 = random.sample(puntosClase[:,0].tolist(),1)
                                    nuevoPunto = puntosClase[puntosClase[:,0] ==n3]
                                    geometria = nuevoPunto[0,2]+" "+nuevoPunto[0,3]+" "+nuevoPunto[0,4]
                                    point3 = ogr.CreateGeometryFromWkt(geometria)
                                    #poly = point.Buffer(bufferDistance)
                                    #distancia = point3.Distance(point2)
                                    cont2 = cont2 + 1
                                    #print("cont == "+str(cont2))
                                    if cont2 == 2:
                                        bandera1 == 0
                                        cont2 = 0
                                        prueba = False
                                        break
                                    #time.sleep(1)
                                    else:
                                        #print("break "+str(n3))
                                        break
                                else:
                                    bandera1 = 0
                                #print(str(sitioAleatorio) + " "+ str(n3)+" dist: "+str(distancia))
                            if bandera1 == 0:
                                #print("Guarda")
                                if cont2 != 2:
                                    #print("guarda")
                                    n1.append(n3)
                                    for buscar in n1:
                                        indice = np.where(puntosClase == buscar)    
                                        np.delete(puntosClase, indice, axis = 0)
                                    #print(len(puntosClase))
                                    point3.AddPoint(point3.GetX(), point3.GetY())
                                    feature = ogr.Feature(layer_defn)
                                    feature.SetGeometry(point3)
                                    feature.SetField("id",nuevoPunto[0,0])
                                    feature.SetField("clases",str(nuevoPunto[0,1]))
                                    layer.CreateFeature(feature)
                                    cont2 = 0
                                else:
                                    cont2 = 0
                                    prueba = False
                                prueba = False
                            '''while distancia < bufferDistance:
                                
                                if sitioAleatorio != n3:
                                     
                                    #print(punto[0,0])
                                    geometria = str(nuevoPunto[0,2])
                                    point3 = ogr.CreateGeometryFromWkt(geometria)
                                    #poly = point.Buffer(bufferDistance)
                                    distancia = point3.Distance(point2)
                                    cont2 = cont2 + 1
                                if cont2 == 5:  
                                    break
                        #print(cont2)
'''
                #print(len(randomPuntos))
                #nuevosPuntos = []
                #for punto in randomPuntos:   
                    #for compara in randomPuntos:
                        #if punto != compara:
                            #puntos2 = puntosClase[puntosClase[:,0] ==punto] 
                            #puntos3 = puntosClase[puntosClase[:,0] ==compara] 
                            #geometria = str(puntos2[0,2])
                            #geometria2 = str(puntos3[0,2])
                            #print(geometria)
                            #bufferDistance = 401
                            #point = ogr.CreateGeometryFromWkt(geometria)
                            #poly = point.Buffer(bufferDistance)
                            #print(poly)
                            #point2 = ogr.CreateGeometryFromWkt(geometria2)
                            #if poly.Contains(point2):
                                #randomPuntos = random.sample(puntosClase[:,0].tolist(),int(numeroOptimo))
                                #print(puntos3[0,0])
                                #print("hay pegados")

                                #puntos2.remove(puntos3[0,0])
                            #print(poly.ExportToWkt())
                j=j+1 
                    
                #print(puntos2[0,2])
            #print(randomPuntos)        
            
        
            
            
        '''try:
            for campo in self.layer.fields():
                if(campo.type() == 10 or campo.type() == 2):
                    self.columnaVerdadera.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "tex.png")),str(campo.name()))
                    self.columnaValidar.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "tex.png")),str(campo.name()))
                elif(campo.type() == 4):
                    self.columnaVerdadera.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "num.png")),str(campo.name()))       
                    self.columnaValidar.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "num.png")),str(campo.name()))
                #self.columnaVerdadera.addItem(str(campo.name()) ,campo.type())
                #self.columnaValidar.addItem(str(campo.name()) ,campo.type())
        except AttributeError:
            self.columnaVerdadera.clear()
            self.columnaValidar.clear()'''

''' 
if encontrarMetros != -1:
    geotr = data.GetGeoTransform()
    pixel_area = abs(geotr[1] * geotr[5])
    band = data.GetRasterBand(1).ReadAsArray().astype(int)
    unicos = np.unique(band)
    #clasesMuestras = clasesMuestras.astype(str)
    unicos = unicos.astype(str)
    
for clase in unicos:
    condition = np.bitwise_not(band!=int(clase))
    totalClase = np.extract(condition, band)
    total = len(totalClase)
    print(str(round(float(str((total * pixel_area)/10000)),0)))'''
    


        
    
'''
  
    

  

'''
    
'''if __name__ == "__main__":
    direccion = '/home/laige/Escritorio/basura/example.shp'
    distancia = 200
    ui = 0.7
    raster = "/home/laige/Escritorio/basura/revisar_regeneracion_2010_2015/2015_clip_10m_2.tif" 
    areas =areaRaster(raster)
    x = numeroMuestras(ui,areas)

    data = gdal.Open(raster, gdal.GA_ReadOnly) 
    
    #'''
    

    
#dialogo = aleatorios()
#dialogo.show()
