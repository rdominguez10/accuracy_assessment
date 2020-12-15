# encoding: utf-8
#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .validacionTematico import validacion
from .muestras_aleatorias import aleatorios
import os
import inspect
class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.menu_name_plugin = self.tr("Accuracy Assessment")
    def initGui(self):
        current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.action = QAction(QIcon(os.path.join(current_directory, "icons", "icono_accuracy.png")),'accuracy_assessment', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        
        self.dockable_action = QAction(QIcon(os.path.join(current_directory, "icons", "icono_accuracy.png")), 'accuracy_assessment', self.iface.mainWindow())
        self.iface.addPluginToMenu(self.menu_name_plugin, self.dockable_action)
        self.dockable_action.triggered.connect(self.run)
        
        
        self.action2 = QAction(QIcon(os.path.join(current_directory, "icons", "icono_random.png")),'Random point', self.iface.mainWindow())
        self.action2.triggered.connect(self.runRandom)
        self.iface.addToolBarIcon(self.action2)
        
        self.dockable_action2 = QAction(QIcon(os.path.join(current_directory, "icons", "icono_random.png")), self.tr('Random point'), self.iface.mainWindow())
        self.iface.addPluginToMenu(self.menu_name_plugin, self.dockable_action2)
        self.dockable_action2.triggered.connect(self.runRandom)

    def tr(self, message):
        return QCoreApplication.translate('AccuracyAssessment', message)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu(self.menu_name_plugin, self.dockable_action)
        self.iface.removePluginMenu(self.menu_name_plugin, self.dockable_action2)
        del self.action

    def run(self):
    	dialogo = validacion()
    	dialogo.exec_()
    
    def runRandom(self):
        dialogo = aleatorios()
        dialogo.exec_()