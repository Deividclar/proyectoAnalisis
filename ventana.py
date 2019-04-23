# encoding: utf-8
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import Vista.widget as widg
import Vista.statusbar as st
from Modelo.lexclass import *
import Modelo.semantico as semantico
from Modelo.colores import *
from Modelo.worker import *

import time, threading

#CLASE DE LA VENTANA
#VISTA PRINCIPAL

# -------------------------------------------------------------------------------------------------
#       clase ventana: -> extiende de QMainWindow
#               reune:
#               widget principal
#               interfaz precargada del diseñador -> ventana.ui
#               acciones y control general del aplicativo
# -------------------------------------------------------------------------------------------------
class ventana(QMainWindow):
    #CONSTRUCTOR DE LA CLASE
    #signal = qtcore.pyqtSignal(str)
    def __init__(self):
        #CONSTRUCTOR DE LA CLASE HEREDADA
        QMainWindow.__init__(self)
        
        #SE CARGA LA INTERFAZ GRAFICA .UI
        #REALIZADA EN QTDESIGNER
        uic.loadUi("ventana.ui",self)
        
        #TITULO DE LA VENTANA
        self.setWindowTitle("EDITOR")
        #self.accion_lineas = QAction("Marca", self.Barra)
        #self.accion_tiempos = QAction("Timepos",self.Barra)
        self.principal = widg.widget()              #incializa todos los compentes principales de la aplicacion
        self.setCentralWidget(self.principal)       #se asigna el editor como el componente principal
        self.lexico = Lexico()                      #instancia del analizador lexico
        self.__icons_actions()                      #asigna los iconos
        self.__signals()                            #asigna los metodos a ejecutar cuando se da click en una accion
        self.__acciones()                           #atajos de teclado para las acciones
        self.__crear_toolbar()                      #crea la barra de herramientas

        self.nodito = 0                             #nodo actual

        self.dicci = {}                             #diccionario para las graficas
        self.contador = 0

        #analizador semantico
        self.sema = semantico.Semantico(self.principal.estado, self.principal.terminal, self.principal.editor)
        #hilo que manejara el analizador semantico
        self.hilo = threading.Thread()


        ##barra de estado inferior
        self.status = st.StatusBar()
        self.setStatusBar(self.status)

        sld = QSlider(Qt.Horizontal, self)
        sld.setFocusPolicy(Qt.NoFocus)
        sld.setValue(50)
        sld.setMaximumWidth(200)
        sld.valueChanged[int].connect(self.__changeValue)

        #velocidad del modo automatico
        self.velocidad = 50;

        #hilo que maneja el modo automatico
        self.timer = QTimer()
        self.timer.timeout.connect(self.__continue_line)

        self.timer.setInterval((self.velocidad + 1) * 50)

        # labelSlider = QLabel(self)
        # labelSlider.setText('Velocidad')
        # labelSlider.setGeometry(600, 20, 200, 30)

        self.Barra.addWidget(sld)

        #tamaño y posicion de la ventana principal
        self.setGeometry(200, 100, 900, 600)




    #------------------------------------------------------------------------------------------------
    #       muestra el numero de linea y la prosicion en la linea del cursor en un status bar
    #------------------------------------------------------------------------------------------------
    def __actualizar_status_bar(self):
        pos = self.principal.editor.getCursorPosition()
        self.status.actualizar_label(pos[0],pos[1])

    #-------------------------------------------------------------------------------------------------
    #       asigna imagenes a las acciones
    #-------------------------------------------------------------------------------------------------
    def __icons_actions(self):
        self.actionN.setIcon(QIcon('Imagenes/Add.png'))
        self.actionOpen.setIcon(QIcon('Imagenes/Enter.png'))
        self.actionSave.setIcon(QIcon('Imagenes/Download.png'))
        self.actionLine.setIcon(QIcon('Imagenes/Pin.png'))
        self.actionClearTerm.setIcon(QIcon('Imagenes/Bin.png'))
        #self.actionClearEst.setIcon(QIcon('Imagenes/Bin.png'))
        self.actionContinue.setIcon(QIcon('Imagenes/next.png'))
        self.actionRun.setIcon(QIcon('Imagenes/FlagGreen.png'))
        self.actionCancel.setIcon(QIcon('Imagenes/FlagRed.png'))
        self.actionExit.setIcon(QIcon('Imagenes/Cancel.png'))
        #self.actionInfo.setIcon(QIcon('Imagenes/Info.png'))
        self.actionBreakpoints.setIcon(QIcon('Imagenes/location.png'))
        #self.actionTree.setIcon(QIcon('Imagenes/brush.png'))
        self.actionAutomatic.setIcon(QIcon('Imagenes/graph.png'))


    #--------------------------------------------------------------------------------------------
    #       asigna las señales a las respectivas acciones(botones del menu o de la barra de herramientas)
    #--------------------------------------------------------------------------------------------
    def __signals(self):
        self.principal.editor.cursorPositionChanged.connect(self.__actualizar_status_bar)
        self.actionN.triggered.connect(self.__new_file)
        self.actionOpen.triggered.connect(self.__open_file)
        self.actionSave.triggered.connect(self.__save_file)
        self.actionLine.triggered.connect(self.__get_line)
        self.actionClearTerm.triggered.connect(self.__limpiar_terminal)
        #self.actionClearEst.triggered.connect(self.__limpiar_estado)
        self.actionContinue.triggered.connect(self.__continue_line)
        self.actionRun.triggered.connect(self.__run)
        self.actionCancel.triggered.connect(self.__cancel)
        self.actionExit.triggered.connect(self.__salir)
        self.actionBreakpoints.triggered.connect(self.__mostrarLineasMarcadas)
        self.actionInfo.triggered.connect(self.__info)
        self.actionAutomatic.triggered.connect(self.__automatico)

        #self.accion_lineas.triggered.connect(self.mostrarLineasMarcadas)
        #self.accion_tiempos.triggered.connect(self.mostrarTiempos)

    #-------------------------------------------------------------------------------------------------
    #               limpia el area donde se muestran las variables
    #-------------------------------------------------------------------------------------------------
    def __limpiar_estado(self):
        self.principal.estado.clear()

    # -------------------------------------------------------------------------------------------------
    #               limpia el area que hace el papel de terminal
    # -------------------------------------------------------------------------------------------------
    def __limpiar_terminal(self):
        self.principal.terminal.clear()
    # -------------------------------------------------------------------------------------------------
    #               asigna atajos de teclado a las acciones
    # -------------------------------------------------------------------------------------------------
    def __acciones(self):
        self.actionN.setShortcut("Ctrl+N")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionSave.setShortcut("Ctrl+S")
        self.actionContinue.setShortcut("Ctrl+R")
        self.actionRun.setShortcut("Ctrl+E")
        self.actionCancel.setShortcut("Ctrl-Q")

    # -------------------------------------------------------------------------------------------------
    #               añade las acciones a la barra de herramientas
    # -------------------------------------------------------------------------------------------------
    def __crear_toolbar(self):
        self.Barra.addAction(self.actionN)
        self.Barra.addAction(self.actionOpen)
        self.Barra.addAction(self.actionSave)
        self.Barra.addSeparator()
        self.Barra.addAction(self.actionLine)
        self.Barra.addAction(self.actionContinue)
        self.Barra.addSeparator()
        self.Barra.addAction(self.actionRun)
        self.Barra.addAction(self.actionCancel)
        self.Barra.addSeparator()
        #self.Barra.addAction(self.actionInfo)
        self.Barra.addAction(self.actionClearTerm)
        #self.Barra.addAction(self.actionClearEst)
        self.Barra.addAction(self.actionBreakpoints)
        #self.Barra.addAction(self.actionTree)
        self.Barra.addSeparator()
        self.Barra.addAction(self.actionAutomatic)


        #self.Barra.addAction(self.accion_lineas)
        #self.Barra.addAction(self.accion_tiempos)

    # -------------------------------------------------------------------------------------------------
    #       metodo de informacion de la aplicacion
    # -------------------------------------------------------------------------------------------------
    def __info(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Info")

        msg.setText("Editor \n\n\nAngey Velez Vela \nDeivid Steven Gonzalez\n\n\nUniversidad de caldas\n2019")
        msg.exec_()

    # -------------------------------------------------------------------------------------------------
    #       limpia el editor para crear un nuevo archivo
    # -------------------------------------------------------------------------------------------------
    def __new_file(self):
        self.principal.editor.clear()

    # -------------------------------------------------------------------------------------------------
    #       abre un archivo en el editor
    # -------------------------------------------------------------------------------------------------
    def __open_file(self):
        try:
            options = QFileDialog.Options()
            options = QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self,"Open File", "","All Files (*)", options=options)
            f = open(fileName,'r')
            filedata = f.read()
            self.principal.editor.setText(filedata)
            f.close()
        except FileNotFoundError:
            print("No se pudo abrir el archivo")


    # -------------------------------------------------------------------------------------------------
    #       guarda el contenido del editor en un archivo
    # -------------------------------------------------------------------------------------------------
    def __save_file(self):
        try:
            options = QFileDialog.Options()
            options = QFileDialog.DontUseNativeDialog
            fileName = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
            print (fileName)
            f = open(fileName[0],'w')
            filedata = self.principal.editor.text()
            f.write(filedata)
            f.close()
        except FileNotFoundError:
            print("No se pudo guardar")

    # -------------------------------------------------------------------------------------------------
    #         obtiene la posicion donde esta ubicado el cursor
    # -------------------------------------------------------------------------------------------------
    def __get_line(self):
        pos = self.principal.editor.getPosicion()
        self.principal.terminal.append("<span style='color:#F44336'>Linea x : "+str(pos[0])+" Linea y : "+str(pos[1])+"</span>")

    # -------------------------------------------------------------------------------------------------
    #         avanza la linea en tiempo de ejecucion del algoritmo
    # -------------------------------------------------------------------------------------------------
    def __continue_line(self):
        pos = self.principal.editor.getPosicion()
        texto = self.__getLine(pos)

        if(self.sema != None):
            if self.hilo.isAlive():
                if self.sema.variables_actuales != None:
                    self.principal.estado.clear() #limpiamos las variables anteriores
                    self.__mostrar_variables(self.sema.variables_actuales) #se muestran las variables
                    #self.sema.arbolito.get_root().print_tree()

                actual = self.sema.ambiente_actual  #nodo actual
                root = self.sema.arbolito.get_root() #raiz del arbol
                nodo = self.sema.arbolito.find(actual, root) #se busca el nodo actual desde la raiz
                nodo.activo = True #se hace el nodo como activo
                self.principal.grafico.arbolito = self.sema.arbolito
                self.principal.grafico.dibujar() #se dibuja el arbol
                nodo.activo = False #se hace el nodo como no activo

                self.sema.avanzar = False #se para el avance de linea para poder que sea paso a paso
            else: 
                self.timer.stop()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Paso a paso")

            msg.setText("Debe compilar el código, antes de ver paso a paso")
            msg.exec_()


    # -------------------------------------------------------------------------------------------------
    #       muestra las lineas marcadas y las veces que pasa por ellas
    # -------------------------------------------------------------------------------------------------
    def __mostrarLineasMarcadas(self):
        #lineas = self.principal.editor.getMarcadas()
        if not self.sema.lineas_marcadas:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Breakpoints")

            msg.setText("Recuerde que para para establecer los puntos de ruptura\ndebe presionar sobre el numero de linea, y asi empezara a contar."
                        "\n\nLa informacion acerca de los puntos de ruptura se muestra en la consola, encerrados entre corchetes, donde\n\n"
                        "1). El primer valor corresponde a la linea\n"+
                        "2). El segundo valor las veces que paso por ese punto")
            msg.exec_()
        else:
            lineas = self.sema.lineas_marcadas
            self.principal.terminal.append(str(lineas))
        #self.principal.estado.show()


    # -------------------------------------------------------------------------------------------------
    #           muestra el estado de las variables en el area de estado para el entorno actual
    # -------------------------------------------------------------------------------------------------
    def __mostrar_variables(self, variables):
        # print("----------------------------------------------------")

        self.principal.estado.append("----------------------------------------------------")
        for k, v in variables.items():
            if type(v[0]) == tuple:
                # print("Nombre de la variable, de tipo ARRAY " + str(k) + " Tipo de ARRAY " + str(
                #    v[0][0]) + " Tamaño " + str(v[0][1]))
                # print("Contenido " + str(v[1]))
                self.principal.estado.append(spanh_azul_oscuro + "Variable: " + spanb + spanh_verde + str(
                    k) + spanb + spanh_azul_oscuro + " ARRAY :" + str(v[0][0]) + spanb + " Tamaño " + str(v[0][1]))
                self.principal.estado.append(spanh_azul_oscuro + "Valor: " + str(v[1]) + spanb)

            else:
                # print(
                #    "Nombre de la variable " + str(k) + " Tipo de dato " + str(v[0]))
                self.principal.estado.append(spanh_azul_oscuro + "Variable: " + spanb + spanh_verde + str(
                    k) + spanb + spanh_azul_oscuro + " Tipo de dato " + str(v[0]) + spanb)
                if (v[0] == 'GRAPH'):
                    #    print("Nodos " + str(v[1].nodes()))
                    #    print("Aristas " + str(v[1].edges()))
                    self.principal.estado.append(spanh_azul_oscuro + "Nodos " + str(v[1].nodes()) + spanb)
                    self.principal.estado.append(spanh_azul_oscuro + "Aristas " + str(v[1].edges()) + spanb)
                else:
                    #    print("Contenido " + str(v[1]))
                    self.principal.estado.append(spanh_azul_oscuro + "Valor: " + str(v[1]) + spanb)
        # print("----------------------------------------------------")
                self.principal.estado.append("----------------------------------------------------")

    def __changeValue(self, value):
        self.velocidad = value
        self.timer.setInterval((self.velocidad + 1) * 50)
        print((self.velocidad + 1) * 50)

    def __automatico(self):
        if self.hilo.isAlive():
            self.timer.start()
        else: 
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Automatico")

            msg.setText("Debe compilar el código, antes de la ejecución automatica")
            msg.exec_()

    # -------------------------------------------------------------------------------------------------
    #           metodo principal inicia el hilo que hara el analisis sintactico y semantico
    # -------------------------------------------------------------------------------------------------
    def __run(self):
        if (not self.hilo.isAlive()):

            pos = pos = self.principal.editor.getPosicion()
            linea = str(self.__getLine(pos))
            texto = self.principal.editor.text()
            #sintac.cancelar = False
            self.lexico.setTerminal(self.principal.terminal)
            lineas = self.principal.editor.getMarcadas()

            self.sema.construir_parser()    #analisis sintactico
            self.sema.limpiar_variables()   #limpia las variables utilizadas en anteriores ejecuciones
            self.hilo = threading.Thread(target=self.sema.analizar, args=(texto,lineas,))
            self.hilo.start()
            #self.principal.grafico.arbolito = self.sema.arbolito
            #self.principal.grafico.dibujar()
            self.principal.grafico.escena.clear()   #limpia el area de dibujo del arbol cada vez que se vuelve a ejecutar el codigo
            #sintac.analizar(texto,self.principal.estado,self.principal.terminal,self.principal.editor)

        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("Espere a que termine la ejecucion")
            msg.exec_()


    # -------------------------------------------------------------------------------------------------
    #               detiene la ejecucion
    # -------------------------------------------------------------------------------------------------
    def __cancel(self):
        #sintac.cancelar = True
        #sintac.close()
        self.sema.detener = True # para poder matar el hilo
        self.sema.avanzar = False # hacemos que avance hacia su fin
        self.principal.editor.setCursorPosition(0, 0)

    # -------------------------------------------------------------------------------------------------
    #       devuelve la posicion del cursor
    # -------------------------------------------------------------------------------------------------
    def __getLine(self,pos):
        return self.principal.editor.text(pos[0])

    # -------------------------------------------------------------------------------------------------
    #       termina la ejecucion de toda la aplicacion
    # -------------------------------------------------------------------------------------------------
    def __salir(self):
        #sintac.close()
        self.__cancel()
        sys.exit()


# -------------------------------------------------------------------------------------------------
#       ejecuta la aplicacion general
# -------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    #INSTANCIA DE LA APLICAION PRINCIPAL
    app = QApplication(sys.argv)
    #INSTANCIA DE LA CLASE VENTANA
    _ventana = ventana()
    #SE MUESTRA LA VENTANA
    _ventana.show()

    app.setWindowIcon(QIcon('Imagenes/Application.png'))
    #SE EJECUTA LA APP
    app.exec_()
        
        
