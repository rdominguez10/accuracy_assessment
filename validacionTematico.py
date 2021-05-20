from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt5.QtGui import *
import csv
import numpy as np
import os
from osgeo import gdal
from qgis.core import QgsVectorLayer
from qgis.core import QgsRasterLayer
from qgis.core import QgsProject
from qgis.core import QgsExpression
from qgis.core import QgsFeatureRequest
import time

DialogUi , DialogType= uic.loadUiType(os.path.join(os.path.dirname(__file__),'evaluacion_precisioningles2.ui'))
#DialogUi , DialogType= uic.loadUiType('/home/laige/Documentos/evaluacion/github/accuracy_assessment/evaluacion_precisioningles2.ui')

class validacion(DialogType,DialogUi):
    def __init__ (self):
        super().__init__()
        self.rutaSHPMuestras = ""
        self.rutaCSVSuperficie = ""
        self.dataNp = ""
        self.layer = ""
        self.direccionGuardar = ""
        self.csv_reader = ""
        self.layer2 = ""
        self.setupUi(self)
        self.loadLayers(1)
        self.loadLayers(2)
        self.bucarMuestas.clicked.connect(self.abrirShp)
        self.buscarSuperficie.clicked.connect(self.abrir)
        self.guardarResultado.clicked.connect(self.guardarArch)
        self.aceptar.clicked.connect(self.ejecutar)
        self.itemLayers.currentIndexChanged.connect(self.actualizarComboBox)
        self.itemSuperficie.currentIndexChanged.connect(self.comboBoxClases)
        self.cancelar.clicked.connect(self.close)
        
    def abrirShp(self):#Funcion que abre cuadro de dialogo para buscar las muestras de entrenamiento
        options = QFileDialog.Option()
        options |= QFileDialog.DontUseNativeDialog 
        fichero = QtWidgets.QFileDialog.getOpenFileName(self,"Abrir Fichero","","Shapefile Muestras(*.shp);;All Files (*)", options=options)
        if fichero[0] != '':
            self.rutaSHPMuestras=fichero[0]
            self.itemLayers.addItem(self.rutaSHPMuestras,1)
            self.itemLayers.setCurrentText(self.rutaSHPMuestras)
            #self.textMuestras.setText(self.rutaSHPMuestras)
            self.actualizarComboBox()
            
    def loadLayers(self,vecras):#Carga las capas que se encuentren en el proyecto de Qgis
        lista = QgsProject.instance().mapLayers().values()
        if(vecras == 1):
            self.itemLayers.addItem('')
            for layer in lista:
                if(str(layer.type()) == "QgsMapLayerType.VectorLayer"):
                    self.itemLayers.addItem(layer.name(), layer.id())
        else:
            self.itemSuperficie.addItem('')
            for layer in lista:
                    self.itemSuperficie.addItem(layer.name(), layer.id())
            
    def abrir(self):#Funcion que abre cuadro de dialogo para el mapa de cobertura del suelo (raster o vector)
        options = QFileDialog.Option()
        options |= QFileDialog.DontUseNativeDialog 
        fichero = QtWidgets.QFileDialog.getOpenFileName(self,"Abrir Fichero","",";;All Files (*)", options=options)
        if fichero[0] != '':
            if str(os.path.splitext(fichero[0])[1]) == ".tif" or str(os.path.splitext(fichero[0])[1]) == ".TIF" or str(os.path.splitext(fichero[0])[1]) == ".shp" or str(os.path.splitext(fichero[0])[1]) == ".SHP":
                self.rutaCSVSuperficie=fichero[0]
                self.itemSuperficie.addItem(self.rutaCSVSuperficie,1)
                self.itemSuperficie.setCurrentText(self.rutaCSVSuperficie)
            else:
                QMessageBox.information(self,"Error","Tipo de archivo no permitido",QMessageBox.Ok) 
            #self.openCSV()

    def guardarArch(self):#Copia la direccion del archivo seleccionado y se pega en la caja de textos textResultado
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dire = QFileDialog.getExistingDirectory(self, "Directorio","",
                                       QFileDialog.ShowDirsOnly
                                       | QFileDialog.DontResolveSymlinks)
        self.textResultado.setText(dire)
        self.direccionGuardar = dire
        #fileName =QtWidgets.QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*)", options=options)

    def comboBoxClases(self):#Extrae todas las columnas de tipo texto y numerico del mapa de covertura del suelo en formato vectorial
        #current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        nombre = self.itemSuperficie.currentText()
        if os.path.isfile(nombre):
            
            if str(os.path.splitext(nombre)[1]) == ".tif" or str(os.path.splitext(nombre)[1]) == ".TIF":
                self.layer2 = QgsRasterLayer(self.rutaCSVSuperficie, "aleatorios", "gdal")
            elif str(os.path.splitext(nombre)[1]) == ".shp" or str(os.path.splitext(nombre)[1]) == ".SHP":
                self.layer2 = QgsVectorLayer(self.rutaCSVSuperficie, "aleatorios", "ogr")
            #QgsVectorLayer(self.rutaCSVSuperficie, "aleatorios", "ogr")
        else:
            idLayerQg = self.itemSuperficie.currentData()
            self.layer2 = QgsProject.instance().mapLayer(str(idLayerQg))    
        self.columClase.clear()
        #print(self.layer2.type())
        try:
            if str(self.layer2.type()) == "QgsMapLayerType.VectorLayer":
                for campo in self.layer2.fields():
                    if(campo.type() == 10):
                        self.columClase.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "tex.png")),str(campo.name()))
                    elif(campo.type() == 4 or campo.type() == 2):
                        self.columClase.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "num.png")),str(campo.name()))
                    print(current_directory)
                    #self.columClase.addItem(str(campo.name()))
        except AttributeError:
            self.columClase.clear()
            
    def actualizarComboBox(self):#Extrae todas las columnas de tipo texto y numerico del vector de muestras
        nombre = self.itemLayers.currentText()
        if os.path.isfile(nombre):
            self.layer = QgsVectorLayer(self.rutaSHPMuestras, "aleatorios", "ogr")
        else:
            idLayerQg = self.itemLayers.currentData()
            self.layer = QgsProject.instance().mapLayer(str(idLayerQg))
        
        self.columnaVerdadera.clear()
        self.columnaValidar.clear()
        try:
            for campo in self.layer.fields():
                if(campo.type() == 10):
                    self.columnaVerdadera.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "tex.png")),str(campo.name()))
                    self.columnaValidar.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "tex.png")),str(campo.name()))
                elif(campo.type() == 4 or campo.type() == 2):
                    self.columnaVerdadera.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "num.png")),str(campo.name()))       
                    self.columnaValidar.addItem(QIcon(os.path.join(os.path.dirname(__file__), "icons", "num.png")),str(campo.name()))
                #self.columnaVerdadera.addItem(str(campo.name()) ,campo.type())
                #self.columnaValidar.addItem(str(campo.name()) ,campo.type())
        except AttributeError:
            self.columnaVerdadera.clear()
            self.columnaValidar.clear()
            
    def calcularArea(self,clasesMuestras):#Calcula el area de la superficie del mapa de covertura del suelo (Raster o Vector)
        error=True
        self.reultados.append("Inicia proceso de cálculo de áreas")
        idLayerQg = self.itemSuperficie.currentData()
        if(idLayerQg == 1):
            if str(os.path.splitext(self.rutaCSVSuperficie)[1]) == ".tif" or str(os.path.splitext(self.rutaCSVSuperficie)[1]) == ".TIF":
                layerArea = QgsRasterLayer(self.rutaCSVSuperficie, "aleatorios", "gdal")
            else:
                layerArea = QgsVectorLayer(self.rutaCSVSuperficie, "aleatorios", "ogr")
        else:
            layerArea = QgsProject.instance().mapLayer(str(idLayerQg))
        if str(layerArea.type()) == "QgsMapLayerType.VectorLayer":    
            features = layerArea.getFeatures()
            clases = self.columClase.currentText()
            features = layerArea.getFeatures()
            field = [f[clases] for f in features]
            Clasesunicas =np.unique(np.array(field))
            matrizAreaClass = np.empty((len(Clasesunicas), 2)).astype(str)
            if(len(clasesMuestras) == len(Clasesunicas)):
                #print(sorted(np.array(clasesMuestras).astype(str)))
                #print(sorted(np.array(Clasesunicas).astype(str)))
                classMapa = sorted(np.array(Clasesunicas).astype(str))
                classMuestras = sorted(np.array(clasesMuestras).astype(str))
                x = np.array_equal(classMuestras, classMapa)
                if(x):
                    i=0
                    self.reultados.append("Áreas por clase:")
                    for clase in Clasesunicas:
                        expr = QgsExpression( "\"{}\"='{}'".format( clases, clase ) )
                        clasesArea = layerArea.getFeatures( QgsFeatureRequest( expr ) )
                        suma = 0
                        for areas in clasesArea:
                            ha = areas.geometry().area()/10000
                            suma = suma + ha
                        
                        matrizAreaClass[i][0]=str(clase)
                        matrizAreaClass[i][1]=str(round(float(str(suma)),0))
                        self.reultados.append(str(matrizAreaClass[i][0])+": \t"+str(matrizAreaClass[i][1]))
                        i += 1 
                else:
                    QMessageBox.information(self,"Error","Hay clases que no coinciden en vector de muestras y mapa temático",QMessageBox.Ok)
                    error = False
                    matrizAreaClass = 0
            else:
                QMessageBox.information(self,"Error","Las clases del vector de muestras no tiene la misma cantidad de clases que el mapa temático",QMessageBox.Ok)
                error = False
                matrizAreaClass = 0
                
        else:
                pathRaster = layerArea.dataProvider().dataSourceUri()
                data = gdal.Open(pathRaster, gdal.GA_ReadOnly)                 
                getProjec = data.GetProjection()
                encontrarMetros = getProjec.find("metre") 
                
                if encontrarMetros != -1:
                    clasesNew = []
                    geotr = data.GetGeoTransform()
                    pixel_area = abs(geotr[1] * geotr[5])
                    band = data.GetRasterBand(1).ReadAsArray().astype(int)
                    unicos = np.unique(band)
                    clasesMuestras = clasesMuestras.astype(str)
                    unicos = unicos.astype(str)
                    for clase in clasesMuestras:
                        if clase in unicos:
                            clasesNew.append(clase)
                    if(len(clasesMuestras) == len(clasesNew)):
                        classMapa = sorted(np.array(clasesNew).astype(str))
                        classMuestras = sorted(np.array(clasesMuestras).astype(str))
                        if(np.array_equal(classMuestras, classMapa)):
                            i=0
                            self.reultados.append("Áreas por clase:")
                            matrizAreaClass = np.empty((len(classMapa), 2)).astype(str)
                            for clase in clasesNew:
                                condition = np.bitwise_not(band!=int(clase))
                                totalClase = np.extract(condition, band)
                                total = len(totalClase)
                                matrizAreaClass[i][0]=str(clase)
                                matrizAreaClass[i][1]=str(round(float(str((total * pixel_area)/10000)),0))
                                self.reultados.append(str(matrizAreaClass[i][0])+": \t"+str(matrizAreaClass[i][1]))
                                i += 1 
                        else:
                            QMessageBox.information(self,"Error","Hay clases que no coinciden en vector de muestras y mapa temático",QMessageBox.Ok)
                            error = False
                            matrizAreaClass = 0
                    else:
                        QMessageBox.information(self,"Error","Las clases del vector de muestras no tiene la misma cantidad de clases que el mapa temático",QMessageBox.Ok)
                        error = False
                        matrizAreaClass = 0
                else: 
                    QMessageBox.information(self,"Error","El Raster debe de estar en unidades Metricas",QMessageBox.Ok)
                    error = False
                    matrizAreaClass = 0
            
        return matrizAreaClass,error
            #layerArea.dataProvider().addAttributes([QgsField("area", QVariant.Double)])        
            #layerArea.updateFields()
            #features = []
    
            #processing.runAndLoadResults("native:dissolve", {'INPUT':layerArea,
            #'FIELD':['clasTPOT'],
            #'OUTPUT':'memory:'}, feedback = QgsProcessingFeedback() )
            #areas = []
    
            #areas = [ feat.geometry().area() for feat in layerArea.getFeatures() ]
            #field = QgsField("area", QVariant.Double)
            
            #provider.addAttributes([field])        
            
            #for feat in layerArea.getFeatures():
                #feature = QgsFeature()
                #feature.setFields(layerArea.fields())
                #feature.setAttribute("area",feat.geometry().area())
                #features.append(feature)
            #layerArea.dataProvider().addFeatures(features)
            #idx = layerArea.fieldNameIndex('area')
            #for area in areas:
                #new_values = {idx : float(area)}
                #provider.changeAttributeValues({areas.index(area):new_values})
                #print(provider)
            
    def openCSV(self):#Funcion que abre la edicion de archivo csv e imprima en QtextEdit la superficie de cada clase de la cobertura del suelo
        with open(self.rutaCSVSuperficie) as csv_file:
            self.csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in self.csv_reader:
                if line_count == 0:
                    for columna in range(len(row)):
                        self.superficie.addItem(str(row[columna]))
                    #print(f'{", ".join(row)}')
                    line_count += 1
                else:
                    line_count += 1
    
    def sumSuperficie(self, columSup):#Funcion que abre la edicion de archivo csv e imprima en QtextEdit la superficie de cada clase de la cobertura del suelo
        supTotal = []
        
        with open(self.rutaCSVSuperficie) as csv_file:
            line_count = 0
            self.csv_reader = csv.reader(csv_file, delimiter=',')
            for row in self.csv_reader:
                if line_count != 0:
                    supTotal.append(row[columSup])
                line_count += 1
        return supTotal
    
    def comprobarInterfaz(self):#Funcion que valida algunas caracteristicas de la interfaz del plugin 
        prueba = True        
        if(self.itemLayers.currentData() == None):
            QMessageBox.information(self,"Error","Seleccionar un vector de muestras",QMessageBox.Ok)
            prueba = False
        elif(self.columnaVerdadera.currentData() !=  self.columnaValidar.currentData()):
            prueba = False
            QMessageBox.information(self,"Error","Las columnas seleccionadas no tienen el mismo tipo de datos",QMessageBox.Ok)
        elif(self.itemSuperficie.currentData() == None):
            QMessageBox.information(self,"Error","Seleccionar un Mapa tematico a validar",QMessageBox.Ok)
            prueba = False
        elif(self.textResultado.text() == ""):
            QMessageBox.information(self,"Error","Seleccionar una carpeta para guardar los resultados",QMessageBox.Ok)
            prueba = False
        return prueba
    
    def ejecutar(self):#Funcion principal que ejecuta las funciones generarMatriz y calTablaError
        try:
            self.reultados.setText("")
            if (self.comprobarInterfaz() == True):
                self.reultados.append("Inicia proceso de validación")
                matriz,clases,error = self.generarMatriz()
                for n in range(11):
                    time.sleep(.1)
                    self.progressBar.setValue(n)
                if(error):
                    matrizArea,error = self.calcularArea(clases)
                    if(error):
                        for n in range(11,51):
                            time.sleep(.1)
                            self.progressBar.setValue(n)
                        confusion = np.array(matriz).astype(int)
                        clasesMapa = matrizArea[:,1].shape
                        self.calTablaError(matrizArea[:,1],confusion,clases,matriz)
                        for n in range(51,101):
                            time.sleep(.1)
                            self.progressBar.setValue(n)
                        QMessageBox.information(self,"Exito","Proceso termindado",QMessageBox.Ok)
                    else:
                        self.progressBar.setValue(0)
                else:
                    self.progressBar.setValue(0)
        except PermissionError:
            QMessageBox.information(self,"Error","Permiso denegado para guardar los resultados",QMessageBox.Ok)
            
    def calTablaError(self,csvSup,confusion,clases,matriz):#Genera la tabla de error apartir del metodo de oloffson et al.
        supInt = np.array(csvSup).astype(float)
        SupTot = sum(supInt)
        wi = np.array(supInt)/np.array(SupTot)
        nidot = confusion.sum(axis=1) 
        ndoti = confusion.sum(axis=0) 
        num = len(clases)
        pij = np.zeros((num, num))
        for i in range(0,num):
            if nidot[i] != 0:
                pij[i,] =wi[i]*confusion[i,]/nidot[i]
            else:
                pij[i,] = 0    
        matrizRedondeo = pij.round(decimals = 9)
        
        ovacc = matrizRedondeo.trace()
    
        UsAcc = np.diag(pij)/pij.sum(axis=1)
        ProdAcc = np.diag(pij)/pij.sum(axis=0)
        
        Aj  = SupTot * pij.sum(axis=0)
        
        Spdotj = np.zeros((num))  
        
        try:
            for i in range(0,num):           
                Spdotj[i] = pow(sum(pow(wi,2) * ((confusion[:,i]/nidot) * (1 - confusion[:,i]/nidot)/(nidot-1))),0.5)
                print(confusion[:,i])
        except FloatingPointError:
            QMessageBox.information(self,"Error","Existe la posibilidad que el resultado Aj_ics y Aj_ici, no sean correctos por falta de muentras en alguna clase",QMessageBox.Ok)

        VO = []
        VU = []
        for i in range(0,num):
            print(nidot[i])
            vu = (UsAcc[i]*(1-UsAcc[i]))/(nidot[i]-1)
            
            V=pow(wi[i],2)*vu
            vu = pow(vu,0.5)
            #print((UsAcc[i]*(1-UsAcc[i]))/(nidot-1))
            #print(nidot)
            vu = vu.round(decimals = 3)
            VU.append(vu)
            VO.append(V)
            
        se = pow(sum(VO),0.5) 
        se = se.round(decimals = 4)
        SAj = SupTot * Spdotj
        #print(SAj)
        Aj_ics = Aj + 1.96 * SAj
        Aj_ici = Aj - 1.96 * SAj
        UsAcc = UsAcc.round(decimals = 2)
        ProdAcc = ProdAcc.round(decimals = 2)
        Aj = Aj.round(decimals = 0)
        Aj_ics = Aj_ics.round(decimals = 0)
        Aj_ici = Aj_ici.round(decimals = 0)
        ovacc = ovacc.round(decimals = 2)
        columnas = ["classes","UsAcc","ProdAcc","Area","Areas_adj","Ci_sup","Ci_inf"]
        self.reultados.append("Tabla de error:")
        self.reultados.append("clases\tUsAcc\tProdAcc")
        with open(str(self.direccionGuardar)+"/accura.csv", mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(columnas)
            i = 0
            for dato in clases:
                conca = []
                conca.append(dato)
                conca = np.concatenate((np.array(conca), UsAcc[i]), axis=None)
                conca = np.concatenate((np.array(conca), ProdAcc[i]), axis=None)
                conca = np.concatenate((np.array(conca), supInt[i]), axis=None)
                conca = np.concatenate((np.array(conca), Aj[i]), axis=None)
                conca = np.concatenate((np.array(conca), Aj_ics[i]), axis=None)
                conca = np.concatenate((np.array(conca), Aj_ici[i]), axis=None)
                #conca = np.concatenate((np.array(conca), VU[i]), axis=None)
                self.reultados.append(str(dato)+"\t"+str(UsAcc[i])+"\t"+str(ProdAcc[i]))
                i += 1
                writer.writerow(conca)
            self.reultados.append("Exactitud Global:\t"+str(ovacc))
            self.reultados.append("STD Global::\t"+str(se))
            writer.writerow(["Overall accuracy:",str(ovacc)])
            writer.writerow(["StD Overall(S(O)):",str(se)])
            
    def generarMatriz(self):#Abre llama la funcion confusion_matrix para hacer la matriz de confusion, posteriormente guarda el resultado en CSV
        datos = self.layer.getFeatures()
        true = []
        pred = []
        nueva = []
        unicos = 0
        error = True
        for feature in datos:
            true.append(feature[str(self.columnaVerdadera.currentText())])
            pred.append(feature[str(self.columnaValidar.currentText())])
        true = np.array(true).astype(str)
        pred = np.array(pred).astype(str)
        x = len(np.unique(true))
        y = len(np.unique(pred))
        if (x == y):
            x = np.array_equal(np.unique(true), np.unique(pred))
            if(x):
                nueva, unicos = self.confusion_matrix(pred, true)#Se cambio la direccion de las columnas para seguir con las mismo metodo elaborado por Dr. Miguel
                primero = [" "]
                nameColumn = np.concatenate((np.array(primero), unicos), axis=None)
                with open(str(self.direccionGuardar)+"/confusion_matriX.csv", mode='w') as file:
                    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(nameColumn)
                    i = 0
                    self.reultados.append("Matriz de confusion: ")
                    for dato in unicos:
                        conca = []
                        conca.append(dato)
                        conca = np.concatenate((np.array(conca), nueva[i]), axis=None)
                        self.reultados.append(str(dato)+": \t"+str(nueva[i]))
                        i += 1
                        writer.writerow(conca)
            else:
                QMessageBox.information(self,"Error","Hay clases que no coinciden en el el vector de muestras",QMessageBox.Ok)
                error = False
        else:
            error = False
            QMessageBox.information(self,"clic","Las columnas a comparar no tienen el mismo número de clases",QMessageBox.Ok)
        return nueva,unicos,error
        
    def confusion_matrix(self,pred,true):#Funcion que genera la matriz de confusion
        unicos = np.unique(true)
        unicos2 = np.unique(pred)
        letras = ["a","b","c","d","e","f","g","h","i","j","k","l",
                "m","n","o","p","q","r","s","t","v","w","x","y","z",
		"aa","bb","cc","dd","ee","ff","gg","hh","ii","jj","kk","ll",
                "mm","nn","oo","pp","qq","rr","ss","tt","vv","ww","xx","yy","zz",
		"aaa","bbb","ccc","ddd","eee","fff","ggg","hhh","iii","jjj","kkk","lll",
                "mmm","nnn","ooo","ppp","qqq","rrr","sss","ttt","vvv","www","xxx","yyy","zzz"]
        encode = []
        encode2 = []
        j = 0
        for x in range(len(unicos)):
            encode.append(x)
            encode2.append(letras[j])
            j = j + 1
        encode = np.array(encode)
        encode2 = np.array(encode2)
        i = 0
        for clase in unicos:
            true = np.where(true==str(clase), str(encode2[i]), true)
            pred = np.where(pred==str(clase), str(encode2[i]), pred)
            i += 1   
        i = 0
        for clase in unicos:
            true = np.where(true==str(encode2[i]), str(encode[i]), true)
            pred = np.where(pred==str(encode2[i]), str(encode[i]), pred)            
            i += 1             
        longitud = len(np.unique(unicos)) # Number of classes 
        result = np.zeros((longitud, longitud))
        for a, p in zip(true, pred):
            result[int(p)][int(a)] += 1
        return result,unicos
    
#bloquear cuando terminemos        
#dialogo = validacion()

#dialogo.show()
#dialogo.exec_()#bloquea qgis
