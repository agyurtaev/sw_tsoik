#!/usr/bin/env python
# -*- coding: cp1251 -*-

#from PyQt4 import QtCore, QtGui

import threading
import time

import sys

from PyQt4.QtCore import Qt, SIGNAL, SLOT, QThread, pyqtSignal, QString, QDateTime
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui


from ui_mainwindow import Ui_MainWindow

from testsequences import TestSequences

from testsequences import WriteEEPROM
from testsequences import TestAllEEPROM


class IPMIThread(QThread):


    on_ipmi_report = pyqtSignal( QString )
    on_end_write_ipmi = pyqtSignal()

    test = TestAllEEPROM()
    write = WriteEEPROM()
    quick = 0
    
    def run(self):
        date = QDateTime.currentDateTime()
        #self.on_ipmi_report.emit( QString( str(self.quick )) ) 
        res=0
        self.on_ipmi_report.emit( QString( u"Полная проверка EEPROM 10 минут." ).append( date.toString( "hh:mm:ss dd.MM.yyyy" ) ) )
        if (self.quick==0):
            res = self.test.run(self.on_ipmi_report)
        
        if (self.quick==1):
            res=1
        if (res==1):
            self.on_ipmi_report.emit( QString( u"Полная проверка EEPROM выполнена." ) )       
            date = QDateTime.currentDateTime()
            self.on_ipmi_report.emit( QString( u"Запись IPMI " ).append( date.toString( "hh:mm:ss dd.MM.yyyy" ) ) )
            res = self.write.run(self.on_ipmi_report)   
            if (res==1):
                self.on_ipmi_report.emit( QString( u"Запись IPMI выполнена." ) ) 

        self.on_end_write_ipmi.emit()

        
class TestThread(QThread):

    tests = []
    test = TestSequences()
    current_test = -1
    count_error = 0
    count_success = 0

    on_update_process = pyqtSignal( int )
    on_append_report = pyqtSignal( QString )
    on_end_tests = pyqtSignal()
    no_error = pyqtSignal()


    nom = u"0101010101" 
    mac1 = u"000000000000" 
    mac2 = u"000000000000" 
    mac3 = u"000000000000" 

        
    def get_result_string( self, r ):
        return {0: u"<span style=\" color:#aaaa00;\">Запуск</span>",
                1: u"<span style=\" color:#00aa00;\">Успешно</span>",
                -1: u"<span style=\" color:#aa0000;\">Сбой</span>",
                -2: u"<span style=\" color:#991010;\">Критический сбой</span>"
                }.get(r,u"<span style=\" color:#00aaaa;\">Неизвесно</span>")

    def run(self):

                
        date = QDateTime.currentDateTime()
        self.count_error = 0
        self.count_success = 0
        self.on_append_report.emit( QString( u"Запуск тестов " ).append( date.toString( "hh:mm:ss dd.MM.yyyy" ) ) )
        self.on_append_report.emit( QString( u"Колличество тестов: %1" ).arg( len( self.tests ) ) )
        self.on_append_report.emit( QString( u"Серийный номер ВИМ-3U-3: " ).append( self.nom ) )
        i = 0
        for test in self.tests :
            date = QDateTime.currentDateTime()
            self.on_append_report.emit( QString(u"%1 Тест %2: %3 - %4" ).arg( date.toString( "hh:mm:ss.zzz" ) ).arg( i ).arg( QString( self.test.name(test) ) ).arg( QString( self.get_result_string( 0 ) ) ) )
            self.current_test = test

            self.test.nom = self.nom
            self.test.mac1 = self.mac1
            self.test.mac2 = self.mac2
            self.test.mac3 = self.mac3




            
            res = self.test.run(test, self.on_append_report)
            self.current_test = -1
            date = QDateTime.currentDateTime()
            if (res==1):
                self.count_success+=1
            else:
                self.count_error+=1
                
            self.on_append_report.emit( QString(u"%1 Тест %2: %3 - %4" ).arg( date.toString( "hh:mm:ss.zzz" ) ).arg( i ).arg( QString( self.test.name(test) ) ).arg( QString( self.get_result_string( res ) ) ) )
            self.on_append_report.emit( QString(u"<hr/>") )
            i += 1
            self.on_update_process.emit( (i * 100) / len( self.tests ) )
            if (res == -2):
                break

        date = QDateTime.currentDateTime()
        self.on_append_report.emit( QString( u"Завершение тестов " ).append( date.toString( "hh:mm:ss dd.MM.yyyy" ) ) )
        self.on_append_report.emit( QString( u"успешно : %1 " ).arg( self.count_success ) )
        self.on_append_report.emit( QString( u"с ошибками : %1 " ).arg( self.count_error ) )
        self.on_append_report.emit( QString( u"не проведено : %1 " ).arg( len( self.tests ) - (self.count_success + self.count_error) ) )
        if self.count_error == 0:
            self.no_error.emit()
        self.on_end_tests.emit()

    def terminate( self ):
        if ( self.current_test != -1 ):
            self.test.stop( self.current_test )
            self.current_test = -1
        date = QDateTime.currentDateTime()
        self.on_append_report.emit( QString( u"Отмена " ).append( date.toString( "hh:mm:ss dd.MM.yyyy " ) ) )
        self.on_append_report.emit( QString( u"успешно : %1 " ).arg( self.count_success ) )
        self.on_append_report.emit( QString( u"с ошибками : %1 " ).arg( self.count_error ) )
        self.on_append_report.emit( QString( u"не проведено : %1 " ).arg( len( self.tests ) - (self.count_success + self.count_error) ) )
        super(TestThread, self).terminate()

class MainForm(QMainWindow, Ui_MainWindow):


    write = 0
    error = 1
    quick = 0
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        
        self.setupUi(self)

#        self.test_therad = threading.Thread(target=self.clock, args=(5,))
#        self.test_therad.daemon = True



        
        self.test_therad = TestThread()
        self.test_therad.on_update_process.connect( self.pb_ctrl_test_progress.setValue )
        self.test_therad.on_append_report.connect( self.on_append_report_fn )
        self.test_therad.on_end_tests.connect( self.on_end_tests_fn )
        self.test_therad.no_error.connect( self.no_error_fn )

        self.ipmi_therad = IPMIThread()
        self.ipmi_therad.on_ipmi_report.connect( self.on_ipmi_report_fn )
        self.ipmi_therad.on_end_write_ipmi.connect( self.on_end_write_ipmi_fn )

        self.b_test_selectnone.clicked.connect( self.on_b_test_selectnone_clicked_fn )
        self.b_test_selectall.clicked.connect( self.on_b_test_selectall_clicked_fn )
        self.b_ctrl_savereport.clicked.connect( self.on_b_ctrl_savereport_clicked_fn )
        self.b_ctrl_start.clicked.connect( self.on_b_ctrl_start_clicked_fn )
        self.b_ctrl_stop.clicked.connect( self.on_b_ctrl_stop_clicked_fn )

        self.b_write_ipmi.clicked.connect( self.on_b_write_ipmi_clicked_fn )
    

        self.lineEdit.setText( QString("0101010101") )
        self.lineEdit_2.setText( QString("000000000000") )
        self.lineEdit_3.setText( QString("000000000000") )
        self.lineEdit_4.setText( QString("000000000000") )

    def on_b_test_selectnone_clicked_fn( self ):
        for i in range( 0, self.l_test_selectlst.count() ):
            self.l_test_selectlst.item(i).setCheckState( Qt.Unchecked )

    def on_b_test_selectall_clicked_fn( self ):
        for i in range( 0, self.l_test_selectlst.count() ):
            self.l_test_selectlst.item(i).setCheckState( Qt.Checked )

    def on_b_ctrl_savereport_clicked_fn( self ):
        f_qt = QFileDialog.getSaveFileName(self, u'Сохранение отчета в формате HTML (UTF8)', "VIM_3U_3_REPORT.html", filter='*.html')
        if (f_qt.isEmpty()):
            return
        f = open( f_qt.toUtf8() , 'w')
        f.write( self.te_report.toHtml().toUtf8() )
        f.close()


    def on_b_ctrl_start_clicked_fn( self ):
        self.b_ctrl_start.setEnabled( False )
        self.b_ctrl_stop.setEnabled( True )
        self.b_write_ipmi.setEnabled( False )
        self.pb_ctrl_test_progress.setValue( 0 )

        #self.f_quick_write_ipmi.setCheckState(QtCore.Qt.Unchecked)
        self.f_quick_write_ipmi.setEnabled( False )

        #text = self.lineEdit.text()
        #text1 = self.lineEdit_2.text()
        #text2 = self.lineEdit_3.text()
        #text3 = self.lineEdit_4.text()

        #if text == "":
        #    self.lineEdit.setText( QString("0101010101") )

        #if text1 == "":
        #    self.lineEdit_2.setText( QString("000000000000") )

        #if text2 == "":
        #    self.lineEdit_3.setText( QString("000000000000") )

        #if text3 == "":
        #    self.lineEdit_4.setText( QString("000000000000") )

        self.lineEdit.setReadOnly( True )
        self.lineEdit_2.setReadOnly( True )
        self.lineEdit_3.setReadOnly( True )
        self.lineEdit_4.setReadOnly( True )

        self.test_therad.tests = []
        for i in range( 0, self.l_test_selectlst.count() ):
            if ( self.l_test_selectlst.item(i).checkState() == Qt.Checked ):
                self.test_therad.tests.append(i)
        
        self.test_therad.nom = self.lineEdit.text()
        self.test_therad.mac1 = self.lineEdit_2.text()
        self.test_therad.mac2 = self.lineEdit_3.text()
        self.test_therad.mac3 = self.lineEdit_4.text()
        self.test_therad.start()

    def on_b_write_ipmi_clicked_fn( self ):
        self.b_ctrl_start.setEnabled( False )
        self.b_write_ipmi.setEnabled( False )
        self.f_quick_write_ipmi.setEnabled( False )

        self.ipmi_therad.quick = self.quick

        item = self.l_test_selectlst.item(0)
        item.setCheckState(QtCore.Qt.Checked)
        item = self.l_test_selectlst.item(1)
        item.setCheckState(QtCore.Qt.Unchecked)

        if ( self.f_quick_write_ipmi.checkState() == Qt.Checked ):
            item = self.l_test_selectlst.item(2)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.quick = 1
            
        if ( self.f_quick_write_ipmi.checkState() == Qt.Unchecked ):
            item = self.l_test_selectlst.item(2)
            item.setCheckState(QtCore.Qt.Checked)
            self.quick = 0
            
        self.ipmi_therad.quick = self.quick
        
        for i in range (3, 8):
            item = self.l_test_selectlst.item(i)
            item.setCheckState(QtCore.Qt.Checked)
        
        for i in range (8, 45):
            item = self.l_test_selectlst.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

        #for i in range (0, 45):
        #    item = self.l_test_selectlst.item(i)
        #    item.setCheckState(QtCore.Qt.Unchecked)

        #for i in range (6, 8):
        #    item = self.l_test_selectlst.item(i)
        #    item.setCheckState(QtCore.Qt.Checked)

        self.test_therad.tests = []
        for i in range( 0, self.l_test_selectlst.count() ):
            if ( self.l_test_selectlst.item(i).checkState() == Qt.Checked ):
                self.test_therad.tests.append(i)

        self.write = 1
        self.error = 1
        self.test_therad.start()
       

    def on_b_ctrl_stop_clicked_fn( self ):
        self.test_therad.terminate()
        self.on_end_tests_fn()

    def no_error_fn(self):
        self.error = 0

    def on_end_tests_fn(self):

        if (self.write ==1) and (self.error == 0): 
            self.ipmi_therad.start()
            
        if  self.write ==0:        
            self.b_ctrl_start.setEnabled( True )
            self.b_ctrl_stop.setEnabled( False )
            self.b_write_ipmi.setEnabled( True )
            self.lineEdit.setReadOnly( False )
            self.lineEdit_2.setReadOnly( False )
            self.lineEdit_3.setReadOnly( False )
            self.lineEdit_4.setReadOnly( False )
            self.f_quick_write_ipmi.setEnabled( True )
            self.pb_ctrl_test_progress.setValue( 100 )

        if (self.write ==1) and (self.error == 1):

            self.b_ctrl_start.setEnabled( True )
            self.b_ctrl_stop.setEnabled( False )
            self.b_write_ipmi.setEnabled( True )
            self.lineEdit.setReadOnly( False )
            self.lineEdit_2.setReadOnly( False )
            self.lineEdit_3.setReadOnly( False )
            self.lineEdit_4.setReadOnly( False )
            self.f_quick_write_ipmi.setEnabled( True )
            self.pb_ctrl_test_progress.setValue( 100 )
            
            for i in range (0, 22):
                item = self.l_test_selectlst.item(i)
                item.setCheckState(QtCore.Qt.Checked)

            for i in range (23, 37):
                item = self.l_test_selectlst.item(i)
                item.setCheckState(QtCore.Qt.Checked)

        self.error = 1
        self.write = 0
        
    def on_end_write_ipmi_fn(self):
        self.b_ctrl_start.setEnabled( True )
        self.b_write_ipmi.setEnabled( True )
        self.f_quick_write_ipmi.setEnabled( True )
        for i in range (0, 22):
            item = self.l_test_selectlst.item(i)
            item.setCheckState(QtCore.Qt.Checked)

        for i in range (23, 37):
            item = self.l_test_selectlst.item(i)
            item.setCheckState(QtCore.Qt.Checked)
            
        self.error = 1
        self.write = 0

    def on_append_report_fn(self, msg):
        self.te_report.append( msg )
        sb = self.te_report.verticalScrollBar();
        sb.setValue( sb.maximum() );


    def on_ipmi_report_fn(self, msg):
        self.ipmi_report.append( msg )
        sb = self.ipmi_report.verticalScrollBar();
        sb.setValue( sb.maximum() );
       


    #def clock(c, interval):
        #i = 0
        #while True:
            #i = i+1
            #self.pb_ctrl_test_progress.setValue( i )
            #print("The time is %s" % time.ctime())
            #time.sleep(interval)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    form = MainForm()
    form.show()
    sys.exit(app.exec_())


