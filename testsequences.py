# -*- coding: utf-8 -*-
import string
import time
import serial
import re
import random
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, SIGNAL, SLOT, pyqtSignal, QString
import telnetlib

class C1ser:
#    serial_port = '/dev/ttyUSB1'
    serial_port = 'COM2'
    serial_speed = 115200

    ser = None

    def topen( self ):
        self.ser = serial.Serial(self.serial_port, self.serial_speed, timeout=1)
        self.log_f = open('c1_raw.log', 'w')

    def tsend ( self, msg ):
#        print "<< %s" % msg
        self.log_f.write( "<< %s" % msg )
        self.ser.write( msg )

    def tresv ( self, count = 1 ):
        msg = self.ser.read( count)
#        print ">> " + msg
        self.log_f.write( ">> " + msg )
        return msg

    def tclose( self ):
        self.ser.close()
        self.log_f.close()

class C2ser:
#    serial_port = '/dev/ttyUSB1'
    serial_port = 'COM3'
    serial_speed = 115200

    ser = None

    def topen( self ):
        self.ser = serial.Serial(self.serial_port, self.serial_speed, timeout=1)
        self.log_f = open('c2_raw.log', 'w')

    def tsend ( self, msg ):
#        print "<< %s" % msg
        self.log_f.write( "<< %s" % msg )
        self.ser.write( msg )

    def tresv ( self, count = 1 ):
        msg = self.ser.read( count)
#        print ">> " + msg
        self.log_f.write( ">> " + msg )
        return msg

    def tclose( self ):
        self.ser.close()
        self.log_f.close()

class RS485ser:
#    serial_port = '/dev/ttyUSB1'
    serial_port = 'COM6'
    serial_speed = 115200

    ser = None

    def topen( self ):
        self.ser = serial.Serial(self.serial_port, self.serial_speed, timeout=1)
        self.log_f = open('c3_raw.log', 'w')

    def tsend ( self, msg ):
#        print "<< %s" % msg
        self.log_f.write( "<< %s" % msg )
        self.ser.write( msg )

    def tresv ( self, count = 1 ):
        msg = self.ser.read( count)
#        print ">> " + msg
        self.log_f.write( ">> " + msg )
        return msg

    def tclose( self ):
        self.ser.close()
        self.log_f.close()

class Tser:
#    serial_port = '/dev/ttyS0'
    serial_port = 'COM1'
    serial_speed = 115200

    ser = None

    def topen( self ):
        self.ser = serial.Serial(self.serial_port, self.serial_speed, timeout=1)
        self.log_f = open('tests_raw.log', 'w')

    def tsend ( self, msg ):
#        print "<< %s" % msg
        self.log_f.write( "<< %s" % msg )
        self.ser.write( msg )

    def tresv ( self, count = 1 ):
        msg = self.ser.read( count)
#        print ">> " + msg
        self.log_f.write( ">> " + msg )
        return msg

    def tclose( self ):
        self.ser.close()
        self.log_f.close()

    def a_cmd( self, msg ):
        print "a_cmd( %s )\n" % msg
        self.tsend("%s \n" % msg)
        timeout = 10 # secound
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += self.tresv()
            match = re.search( ur" # ", st )
            if (match != None):
                return 1
        return -1 
        
    def a_fpga_write( self, msg ):
        print "a_fpga_write( %s )\n" % msg
        st = ur""
        self.tsend("cd /tests \r")
        self.tsend("./fpga.sh write %s \r" % msg)
        timeout = 2
        test_start_time = time.time()
        while ((time.time() - test_start_time) < timeout):
            st += self.tresv()
            match = re.search( ur"result=OK", st )
            if (match != None):
                return 1
        print "Repeat \n"
        return self.a_fpga_write(msg)

    def a_fpga_read( self, msg ):
        print "a_fpga_read( %s )\n" % msg
        res = None;
        self.tsend("cd /tests \r")
        self.tsend("./fpga.sh read %s \r" % msg)
        st = ""
        while (res == None):
            st += self.tresv()
            res = re.search( ur"result=(\d+)", st )
        return res.group(1)

class A1ser:
#    serial_port = '/dev/ttyS0'
#    serial_port = 'COM13'
    serial_port = 'COM4'
    serial_speed = 115200

    ser = None

    #Размеры портов и групп битов сдвигового регистра
    TEST_MODE_LEN_C = 6

    DSA_TEST_LEN_C = 10
    DSB_TEST_LEN_C = 8
    DSC_TEST_LEN_C = 2
    DSD_TEST_LEN_C = 1

    DS_R_PON_LEN_C = 1
    DS_R_NON_LEN_C = 1

    DSA_T_L_LEN_C = 10
    DSB_T_L_LEN_C = 8
    DSA_T_H_LEN_C = 10
    DSB_T_H_LEN_C = 8

    GA_LEN_C = 5
    GAP_LEN_C     = 1
    SYSCON_LEN_C = 1
    DS_LV_LEN_C     = 2

    INOUT_LEN_C     = 4
    REG_INOUT_DIR_LEN_C = INOUT_LEN_C
    REG_INOUT_WR_LEN_C = INOUT_LEN_C
    #СУММА 6+10+8+2+1+1+1+10+8+10+8+5+1+1+2+4+4=82

    #Размеры групп битов для чтения
    DSX_R_L_LEN_C = 1
    DSA_R_L_LEN_C = 2
    DSA_R_H_LEN_C = 2
    REG_INOUT_RD_LEN_C = INOUT_LEN_C

    #Размер дополняющей группы битов (для кратности общей длины 8)
    DUMMY_LEN_C     = 5
    #СУММА 3+2+4+5=14

    #Базовые адреса в сдвиговом регистре SREG
    #Запись
    TEST_MODE_BASE_C    = 0
    DSA_TEST_BASE_C     = TEST_MODE_BASE_C +    TEST_MODE_LEN_C # 0+6=6
    DSB_TEST_BASE_C     = DSA_TEST_BASE_C  +    DSA_TEST_LEN_C # 6+10=16
    DSC_TEST_BASE_C     = DSB_TEST_BASE_C  +    DSB_TEST_LEN_C # 16+8=24
    DSD_TEST_BASE_C     = DSC_TEST_BASE_C  +    DSC_TEST_LEN_C # 24+2=26

    DS_R_PON_BASE_C     = DSD_TEST_BASE_C  +    DSD_TEST_LEN_C
    DS_R_NON_BASE_C     = DS_R_PON_BASE_C  +    DS_R_PON_LEN_C

    DSA_T_L_BASE_C      = DS_R_NON_BASE_C  +    DS_R_NON_LEN_C
    DSB_T_L_BASE_C      = DSA_T_L_BASE_C   +    DSA_T_L_LEN_C
    DSA_T_H_BASE_C      = DSB_T_L_BASE_C   +    DSB_T_L_LEN_C
    DSB_T_H_BASE_C      = DSA_T_H_BASE_C   +    DSA_T_H_LEN_C

    GA_BASE_C       = DSB_T_H_BASE_C    +    DSB_T_H_LEN_C
    GAP_BASE_C      = GA_BASE_C            +    GA_LEN_C
    SYSCON_BASE_C   = GAP_BASE_C    +    GAP_LEN_C
    DS_LV_BASE_C    = SYSCON_BASE_C    +    SYSCON_LEN_C
    REG_INOUT_DIR_BASE_C    = DS_LV_BASE_C    +    DS_LV_LEN_C
    REG_INOUT_WR_BASE_C     = REG_INOUT_DIR_BASE_C    +    REG_INOUT_DIR_LEN_C # 78

    #Базовые адреса в векторе inputs
    INPUTS_DSX_R_L_BASE_C       = REG_INOUT_WR_BASE_C           +       REG_INOUT_WR_LEN_C
    INPUTS_DSA_R_L_BASE_C       = INPUTS_DSX_R_L_BASE_C        +       DSX_R_L_LEN_C
    INPUTS_DSA_R_H_BASE_C       = INPUTS_DSA_R_L_BASE_C        +    DSA_R_L_LEN_C
    INPUTS_REG_INOUT_RD_BASE_C  = INPUTS_DSA_R_H_BASE_C        +    DSA_R_H_LEN_C
    INPUTS_DUMMY_BASE_C         = INPUTS_REG_INOUT_RD_BASE_C    +    REG_INOUT_RD_LEN_C


    def topen( self ):
        self.ser = serial.Serial(self.serial_port, self.serial_speed, timeout=1)
        self.log_f = open('tests_raw_a1.log', 'w')

    def tsend ( self, msg ):
#        print "<< %s" % msg
        self.log_f.write( "<< %s" % msg )
        self.ser.write( msg )

    def tresv ( self, count = 1 ):
        msg = self.ser.read( count)
#        print ">> " + msg
        self.log_f.write( ">> " + msg )
        return msg

    def tclose( self ):
        self.ser.close()
        self.log_f.close()

    def a_open( self ):
        self.topen()
        #while (self.tresv()!='>'):
        #    continue

    def a_cmd( self, msg ):
        print "a1.cmd(%s)" % msg
        self.tsend("%s\r" % msg)
        while (self.tresv()!='#'):
            continue

    def a_read( self, msg ):
        print "a1.read(%s)" % msg
        timeout = 2 # secound
        self.tsend("%s\r" % msg)
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < timeout):
            ch = self.tresv()
            if (ch == '@'):
                st = ""
                continue
            if (ch == '#'):
                print "res=%s" % st
                return st
            st += ch

class A2ser:
#    serial_port = '/dev/ttyS1'
#    serial_port = 'COM14'
    serial_port = 'COM5'
    serial_speed = 115200

    ser = None

    #Размеры портов и групп битов сдвигового регистра
    JN8F_LEN_C = 12
    JN8C_LEN_C = 12
    DUMMY_LEN_C = 0
    #СУММА 12+12+0=24

    #Базовые адреса в сдвиговом регистре SREG
    JN8F_BASE_C = 0
    JN8C_BASE_C = JN8F_BASE_C + JN8F_LEN_C

    def topen( self ):
        self.ser = serial.Serial(self.serial_port, self.serial_speed, timeout=1)
        self.log_f = open('tests_raw_a2.log', 'w')

    def tsend ( self, msg ):
#        print "<< %s" % msg
        self.log_f.write( "<< %s" % msg )
        self.ser.write( msg )

    def tresv ( self, count = 1 ):
        msg = self.ser.read( count)
#        print ">> " + msg
        self.log_f.write( ">> " + msg )
        return msg

    def tclose( self ):
        self.ser.close()
        self.log_f.close()

    def a_open( self ):
        self.topen()
        #while (self.tresv()!='>'):
        #    continue

    def a_cmd( self, msg ):
        print "a2.cmd(%s)" % msg
        self.tsend("%s\r" % msg)
        while (self.tresv()!='#'):
            continue

    def a_read( self, msg ):
        print "a2.read(%s)" % msg
        timeout = 2 # secound
        self.tsend("%s\r" % msg)
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < timeout):
            ch = self.tresv()
            if (ch == '@'):
                st = ""
                continue
            if (ch == '#'):
                print "res=%s" % st
                return st
            st += ch

class TestNULL:
    def run( self , s , on_append_report ):
        time.sleep(1)
        return 2
    def stop( self ):
        return 0
    def name( self ):
        return u"Неизвестный"

class TestUbootLoad:
    def run( self, s , on_append_report ):

##        msgBox = QMessageBox()
##        msgBox.setText(u"Нажмите ОК и включите источники питания ТСОиК")
##        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
##        msgBox.setDefaultButton(QMessageBox.Ok)
##        ret = msgBox.exec_()
##        if ( ret != QMessageBox.Ok):
##            return -1
        on_append_report.emit(QString( u"Включите питание блока"))
        timeout = 60 # secound
        test_start_time = time.time()
        st = ""
        ver_z = 0
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()

            match = re.search( ur"U-Boot 2011.09-rc1-02167-gade87b7-dirty", st )
            if (match != None):
                ver_z = 1
            
            match = re.search( ur"### ERROR ### Please RESET the board ###", st )
            if (match != None):
                on_append_report.emit(QString( u"POR test: Ошибка при тесте самотестирования, перезагрузите плату"))
                return -2
            match = re.search( ur"Hit any key to stop autoboot", st )
            if (match != None):
                s.tsend("\r")
                on_append_report.emit(QString( u"POR test: Подтверждена работоспособность процессора"))
                on_append_report.emit(QString( u"POR test: Подтверждена работоспособность РПЗУ NOR1"))
                on_append_report.emit(QString( u"POR test: Подтверждена корректность тактовой частоты и её конфигурации"))
                on_append_report.emit(QString( u"POR test: Проведен тест ОЗУ"))

                if ver_z == 1:
                    on_append_report.emit(QString( u"Подтверждена корректность версии загрузчика"))   

                if ver_z == 0:
                    on_append_report.emit(QString( u"Некорректная версия загрузчика"))                   
                    return -1
                
                return 1
        return -2
    def stop( self, s ):
        return 0
    def name( self ):
        return u"Тест запуска u-boot"

class TestComplexNOR1NOR2:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        sc = 0
        sca = 0
        timeout = 1000 # secound
        test_start_time = time.time()
        s.tsend(" run test_nor \n")
        on_append_report.emit(QString( u"Внимание: тестирование занимает примерно 12 минут, подождите"))
        on_append_report.emit(QString( u"Внимание: Сбой во время прохождения теста может повлечь повреждение начального загрузчика"))
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"eTSEC1\: No link\.", st )
            if (match != None):
                on_append_report.emit(QString( u"Ошибка: Не установлено соединение через технологический Ethernet" ))
                on_append_report.emit(QString( u"Внимание: Немедленно отключите питание ВИМ-3U-3" ))
                return -2
            match = re.search( ur"Using eTSEC1 device", st )
            if (match != None):
                on_append_report.emit(QString( u"Соединение через технологический Ethernet установлено" ))
                st = ""
            match = re.search( ur"Using AFDX_1 device", st )
            if (match != None):
                on_append_report.emit(QString( u"Ошибка: не удается подключиться к TFTP серверу ТСОиК" ))
                on_append_report.emit(QString( u"Внимание: Немедленно отключите питание ВИМ-3U-3" ))
                on_append_report.emit(QString( u"Внимание: Проверьте, что TFTP и HTTP сервера запущены" ))
                return -2
            match = re.search( ur"Total of 33554432 bytes were the same", st )
            if (match != None):
                on_append_report.emit(QString( u"Блок данных проверен" ))
                st = ""
                sc += 1
            match = re.search( ur"CRC32 for ee000000 \.\.\. efffffff ==> 76a9cb4e", st )
            if (match != None):
                on_append_report.emit(QString( u"Контроль корректности данных на NOR1 выполнен" ))
                st = ""
                sc += 1
            match = re.search( ur"CRC32 for ec000000 \.\.\. edffffff ==> b3dc32dc", st )
            if (match != None):
                on_append_report.emit(QString( u"Контроль корректности данных на NOR2 выполнен" ))
                st = ""
                sc += 1				
            if (sc==5):
                on_append_report.emit(QString( u"Комплексный тест NOR1 и NOR2 завершен удачно" ))
                st = ""
		break
	print "s=%s" % st
	timeout = 60 # secound
	test_start_time = time.time()
	s.tsend(" run update_uboot\r")
	while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
	    match = re.search( ur"done", st )
	    if (match != None):
		on_append_report.emit(QString( u"Загрузчик восстановлен" ))
		sca = 1
		break
	if (sc == 5)and(sca == 1):
	    return 1
	on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -2
    def stop( self, s ):
        return -1
    def name( self ):
        return u"Комплексный тест NOR1 и NOR2"

class LinuxUpload:
    def run( self, s , on_append_report ):
        sc=0
        time.sleep(6)
        timeout = 360 # secound
        test_start_time = time.time()
        s.tsend(" run reload_linux\n")
        on_append_report.emit(QString( u"Внимание: операция занимает примерно 5 минут, подождите"))
        on_append_report.emit(QString( u"Внимание: Сбой во время прохождения теста может повлечь повреждение начального загрузчика и операционной системы"))
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"eTSEC1\: No link\.", st )
            if (match != None):
                on_append_report.emit(QString( u"Ошибка: Не установлено соединение через технологический Ethernet" ))
                on_append_report.emit(QString( u"Внимание: Немедленно отключите питание ВИМ-3U-3" ))
                return -2
            match = re.search( ur"Using eTSEC1 device", st )
            if (match != None):
                on_append_report.emit(QString( u"Соединение через технологический Ethernet установлено" ))
                st = ""
            match = re.search( ur"Using AFDX_1 device", st )
            if (match != None):
                on_append_report.emit(QString( u"Ошибка: не удается подключиться к TFTP серверу ТСОиК" ))
                on_append_report.emit(QString( u"Внимание: Немедленно отключите питание ВИМ-3U-3" ))
                on_append_report.emit(QString( u"Внимание: Проверьте, что TFTP и HTTP сервера запущены" ))
                return -2
            match = re.search( ur"13225344 bytes written to volume rootfs", st )
            if (match != None):
                on_append_report.emit(QString( u"Прошивка успешно завершена" ))
                st = ""
                return 1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -2



        time.sleep(1)

        on_append_report.emit(QString( u"Запись Uboot в РПЗУ - начато"))
        s.tsend(" ; run update_uboot\n")
        timeout = 10 # secound
        test_start_time = time.time()
        st = ""
        test = 0
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"done", st )
            if (match != None):
                s.tsend("\r")
                test = 1
                break
        if (test == 0):
            return -2
        on_append_report.emit(QString( u"Запись Uboot в РПЗУ - завершено"))

        time.sleep(1)
        
        on_append_report.emit(QString( u"Запись Linux в РПЗУ - начато"))
        s.tsend(" ; run update_kernel\n")
        timeout = 30 # secound
        test_start_time = time.time()
        st = ""
        test = 0
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"done", st )
            if (match != None):
                s.tsend("\r")
                test = 1
                break
        if (test == 0):
            return -2
        on_append_report.emit(QString( u"Запись Linux в РПЗУ - завершено"))

        time.sleep(1)

        on_append_report.emit(QString( u"Запись DTB в РПЗУ - начато"))
        s.tsend(" ; run update_dtb\n")
        timeout = 5 # secound
        test_start_time = time.time()
        st = ""
        test = 0
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"done", st )
            if (match != None):
                s.tsend("\r")
                test = 1
                break
        if (test == 0):
            return -2
        on_append_report.emit(QString( u"Запись DTB в РПЗУ - завершено"))

        time.sleep(1)

        on_append_report.emit(QString( u"Запись корневой файловой системы в РПЗУ - начато"))
        s.tsend(" ; run update_rootfs\n")
        timeout = 250 # secound
        test_start_time = time.time()
        st = ""
        test = 0
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"written to volume rootfs", st )
            if (match != None):
                s.tsend("\r")
                test = 1
                break
        if (test == 0):
            return -2
        on_append_report.emit(QString( u"Запись корневой файловой систем в РПЗУ - завершено"))
        return 1 
    def stop( self, s ):
        return 0
    def name( self ):
        return u"Запись Linux ОС в РПЗУ NOR1"

class TestReset:
    def run( self, s , on_append_report ):

        s.tsend(" ; reset\n")
        
        timeout = 30 # secound
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"### ERROR ### Please RESET the board ###", st )
            if (match != None):
                on_append_report.emit(QString( u"POR test: Ошибка при тесте самотестирования, перезагрузите плату"))
                return -2
            match = re.search( ur"Hit any key to stop autoboot", st )
            if (match != None):
                s.tsend("\r")
                on_append_report.emit(QString( u"POR test: Подтверждена работоспособность процессора"))
                on_append_report.emit(QString( u"POR test: Подтверждена работоспособность РПЗУ NOR1"))
                on_append_report.emit(QString( u"POR test: Подтверждена корректность тактовой частоты и её конфигурации"))
                on_append_report.emit(QString( u"POR test: Проведен тест ОЗУ"))
                return 1
        return -2
    def stop( self, s ):
        return 0
    def name( self ):
        return u"Тест сигнала сброса модуля"

class LinuxLoad:
    def run( self, s , on_append_report ):
        for channel in range(1,5):
            s.tsend(" ; run norboot \n")
            timeout = 15 # secound
            test_start_time = time.time()
            st = ""
            while ((time.time() - test_start_time) < timeout):
                st += s.tresv()
                match = re.search( ur"Wrong Image Format for bootm command", st )
                if (match != None):
                    on_append_report.emit(QString( u"Ошибка: в NOR1 образ ядра поврежден"))
                    return -2
                match = re.search( ur"/ #", st )
                if (match != None):
                    s.tsend("\r")
                    return 1
        return -2 
    def stop( self, s ):
        return 0
    def name( self ):
        return u"Проверка запуска Linux ОС"

class TestPortTRS:
    salt = 0

    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 1 # secound
        test_start_time = time.time()
        s.tsend( "echo \"TEST%i\"\r" % self.salt )
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"TEST%i" % self.salt, st  )
            if (match != None):
                return 1
        return -1
    def stop( self, s ):
        return -1
    def name( self ):
        return u"Тестирование технологического последовательного порта TRS"

class TestScriptsUpload:
    def run( self, s , on_append_report ):

        s.a_cmd("cd /")
        s.a_cmd("ifconfig eth0 192.168.30.2")
        s.a_cmd("ping -c 4 -W 1 192.168.30.1")
        s.a_cmd("rm -rf /tests")
        s.a_cmd("mkdir ./tests")
        s.a_cmd("cd ./tests")
        s.a_cmd("wget http://192.168.30.1/utils/fmap1.xml")
        s.a_cmd("wget http://192.168.30.1/utils/fpga.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_eth_afdx1.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_eth_afdx2.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_i2c_eeprom.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_i2c_termo.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_i2c_vpx.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_i2c_xmc.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_pcie_vpx.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_pcie_xmc.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_nand.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_nor1.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_nor2.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_nor2_r.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_nor2_w.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_pcie1_eth.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_rk.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_spi_fram1.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_spi_fram2.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_spi_fpga.sh")
        s.a_cmd("wget http://192.168.30.1/utils/test_teth.sh")
        s.a_cmd("wget http://192.168.30.1/utils/eeprom.bin")
        s.a_cmd("chmod +x *.sh")
        s.a_cmd("mkdir ./sw_fpga")
        s.a_cmd("cd ./sw_fpga")
        s.a_cmd("wget http://192.168.30.1/utils/sw_fpga/fpga")
        s.a_cmd("chmod +x fpga")
        s.a_cmd("sync")	

	#time.sleep(3)	
	
        return 1 
    def stop( self, s ):
        return 0
    def name( self ):
        return u"Запись тестовых скриптов в корневую файловую систему"
	


class TestNOR1:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 10 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_nor1.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        print "s=%s" % st
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Проверка РПЗУ NOR1"

class TestNOR2:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 300 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_nor2.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"test (\d+)MB - OK", st )
            if (match != None):
                on_append_report.emit(QString( u"Завершено тестирование %s Мб РПЗУ" % match.group(1)))
                st = ""
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        print "s=%s" % st
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Проверка РПЗУ NOR2"
		
class TestNAND:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
	
	time.sleep(3)
	
        timeout = 180 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_nand.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"Finished pass (\d+) successfully", st )
            if (match != None):
                on_append_report.emit(QString( u"Завершен проход %s" % match.group(1)))
                st = ""
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей (допускается ложное отрицательное срабатывание)"))
                    on_append_report.emit(QString( u"Перезапустите тест"))
                    return -1
        print "s=%s" % st
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Проверка РПЗУ NAND"

class TestSpiFRAM1:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 20 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_spi_fram1.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование SPI FRAM 1 (nvRAM)"

class TestSpiFRAM2:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 20 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_spi_fram2.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование SPI FRAM 2 (nvRAM)"

class TestSpiFPGA:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 10 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_spi_fpga.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    on_append_report.emit(QString( u"POR test: Подтверждена корректность версии ПЛИС"))
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование SPI FPGA"

class TestI2CEEPROM:
    salt = 0

    nom = u"0101010101" 
    mac1 = u"000000000000" 
    mac2 = u"000000000000" 
    mac3 = u"000000000000"
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):


        error = 0


        if self.nom == "0101010101" or len(self.nom) <> 10:
            on_append_report.emit(QString( u"Не указан серийный номер."))
            error = 1
        if self.mac1 == "000000000000" or len(self.mac1) <> 12: 
            on_append_report.emit(QString( u"Не указан MAC-адрес 1."))
            error = 1
        if self.mac2 == "000000000000" or len(self.mac2) <> 12: 
            on_append_report.emit(QString( u"Не указан MAC-адрес 2."))
            error = 1
        if self.mac3 == "000000000000" or len(self.mac3) <> 12: 
            on_append_report.emit(QString( u"Не указан MAC-адрес 3."))
            error = 1
        if error == 1: 
            on_append_report.emit(QString( u"Введите IPMI информацю и перезапустите тест."))
            return -1


        #on_append_report.emit(QString( u"Время тестирования: 30 секунд"))
        timeout = 20 # secound
        test_start_time = time.time()
        st = ""

        s.tsend("cd /tests \r")
        time.sleep(1)
        s.tsend("./fpga.sh write I2C_CTRL.EN_INT 1 \r")
        time.sleep(1)
        s.tsend("./fpga.sh write I2C_CTRL.EN_XMC 0 \r")
        time.sleep(1)
        s.tsend("./fpga.sh write I2C_CTRL.EN_VPX 0 \r")
        time.sleep(1)
        s.tsend("hexdump -n 200 -C /sys/bus/i2c/devices/0-0050/eeprom \r")
        time.sleep(2)

        ok = 0
        ok1 = 0
        ok2 = 0
        ok3 = 0
        

        nomm = str(self.nom)
        nommm = '3' + nomm[0] +' ' + '3' + nomm[1] +' ' + '3' + nomm[2] +' ' + '3' + nomm[3] +' ' + '3' + nomm[4] +' ' + '3' + nomm[5] +' ' + '3' + nomm[6] +' ' + '3' + nomm[7] +'  ' + '3' + nomm[8] +' ' + '3' + nomm[9]
        mac1m = str(self.mac1)
        mac1mm = mac1m[0] + mac1m[1] +' ' + mac1m[2] + mac1m[3] + ' ' + mac1m[4] + mac1m[5] +' '+ mac1m[6] + mac1m[7] +' '+ mac1m[8] + mac1m[9] +' '+ mac1m[10] + mac1m[11]    
        mac2m = str(self.mac2)
        mac2mm = mac2m[0] + mac2m[1] +' ' + mac2m[2] + mac2m[3] + '  ' + mac2m[4] + mac2m[5] +' '+ mac2m[6] + mac2m[7] +' '+ mac2m[8] + mac2m[9] +' '+ mac2m[10] + mac2m[11]    
        mac3m = str(self.mac3)
        mac3mm = mac3m[0] + mac3m[1] +' ' + mac3m[2] + mac3m[3] + ' ' + mac3m[4] + mac3m[5] +' '+ mac3m[6] + mac3m[7] +'  '+ mac3m[8] + mac3m[9] +' '+ mac3m[10] + mac3m[11]    

     
        #on_append_report.emit(QString(nommm))
        #on_append_report.emit(QString(mac1mm))
        #on_append_report.emit(QString(mac2mm))
        #on_append_report.emit(QString(mac3mm))

        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
          
            match = re.search( nommm, st )
            if (match != None):
                ok = 1

            match1 = re.search( mac1mm, st )
            if (match1 != None):
                ok1 = 1

            match2 = re.search( mac2mm, st )
            if (match2 != None):
                ok2 = 1

            match3 = re.search( mac3mm, st )
            if (match3 != None):
                ok3 = 1

            if ok == 1 and ok1 == 1 and ok2 == 1 and ok3 == 1:
                break


        if ok == 0:
            on_append_report.emit(QString(u"Серийный номер некорректен"))

        if ok1 == 0:
            on_append_report.emit(QString( u"MAC-адрес 1 некорректен"))
 
        if ok2 == 0:
            on_append_report.emit(QString( u"MAC-адрес 2 некорректен"))

        if ok3 == 0:
            on_append_report.emit(QString( u"MAC-адрес 3 некорректен"))
            
        okw = 0
        okw1 = 0
        okw2 = 0
        okw3 = 0
        okw4 = 0
        okw5 = 0

        timeout = 10
        
        s.tsend("dd if=/sys/bus/i2c/devices/0-0050/eeprom of=/tests/eeprom.bin bs=256 count=1 \r")
        time.sleep(1)
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"256 bytes", st )
            if (match != None):
                okw = 1
                break
        
        s.tsend("dd if=/dev/urandom of=/tests/eeprom_in.bin bs=256 count=1 \r")
        time.sleep(1)
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"256 bytes", st )
            if (match != None):
                okw1 = 1
                break
        
        s.tsend("dd if=/tests/eeprom_in.bin of=/sys/bus/i2c/devices/0-0050/eeprom \r")
        time.sleep(1)
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"256 bytes", st )
            if (match != None):
                okw2 = 1
                break
            
        s.tsend("dd if=/sys/bus/i2c/devices/0-0050/eeprom of=/tests/eeprom_out.bin bs=256 count=1 \r")
        time.sleep(1)
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"256 bytes", st )
            if (match != None):
                okw3 = 1
                break
            
        s.tsend("diff -qs /tests/eeprom_in.bin /tests/eeprom_out.bin \r")
        time.sleep(1)
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"differ", st )
            if (match != None):
                okw4 = 1
                break       

        if okw4 == 0:
            on_append_report.emit(QString(u"Резистор защиты от записи EEPROM не удалён!"))

            s.tsend("dd if=/tests/eeprom.bin of=/sys/bus/i2c/devices/0-0050/eeprom \r")
            time.sleep(1)
            test_start_time = time.time()
            st = ""
            while ((time.time() - test_start_time) < timeout):
                st += s.tresv()
                match = re.search( ur"256 bytes", st )
                if (match != None):
                    on_append_report.emit(QString(u"Данные EEPROM восстановленны."))
                    okw5 = 1
                    break       

            if okw5 == 0:
                on_append_report.emit(QString(u"Данные EEPROM  не восстановленны!"))
            
        if ok == 1 and ok1 == 1 and ok2 == 1 and ok3 == 1 and okw == 1 and okw1 == 1 and okw2 == 1 and okw3 == 1 and okw4 == 1:   
            return 1
     
        if ok == 0 or ok1 == 0 or ok2 == 0 or ok3 == 0 or okw == 0 or okw1 == 0 or okw2 == 0 or okw3 == 0 or okw4 == 0: 
            on_append_report.emit(QString( u"Тест завершился неудачей"))
            return -1


    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование I2C EEPROM"

class TestI2CTERMO:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 2 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_i2c_termo.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            
            match = re.search( ur"termo2\(%i\)=(\d+)" % self.salt, st )
            if (match != None):
                on_append_report.emit(QString( u"Измеренная температура = %s " % match.group(1)))
                st = ""
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование I2C термо-датчик"


class TestTEth:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 25 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_teth.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование Ethernet TETH"

class TestEthAFDX1:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 25 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_eth_afdx1.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование Ethernet AFDX1"

class TestEthAFDX2:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 25 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_eth_afdx2.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование Ethernet AFDX2"

class TestPCIeXMC:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 5 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_pcie_xmc.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование шины PCIe XMC"

class TestI2CXMC:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 10 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_i2c_xmc.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование I2C XMC bus"

class TestPCIeVPX:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 5 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_pcie_vpx.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование шины PCIe VPX"

class TestI2CVPX:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        timeout = 10 # secound
        test_start_time = time.time()
        s.tsend("cd /tests \r")
        s.tsend("./test_i2c_vpx.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    return 1
                else:
                    on_append_report.emit(QString( u"Тест завершился неудачей"))
                    return -1
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Тестирование I2C VPX bus"

class TestRS232C_1:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        pattern1 = "ASDFGHJKLQWERTYUIOPZXCVBNM1234"
        pattern2 = "SFNJKASFBHWIUFHSDKJASDHNWUIDNA"
        c1 = C1ser()
        c1.topen()
        
        timeout = 3 # secound
        test_start_time = time.time()
        s.a_cmd("stty -icanon -F /dev/ttyS2 speed 115200")
        s.a_cmd("echo \"%s\" > /dev/ttyS2 " % pattern1)
        st = c1.tresv(30)
        if (st != pattern1 ):
            on_append_report.emit(QString( u"Ошибка передачи данных, где передающая сторона ВИМ-3U-3"))

        s.tsend("cat /dev/ttyS2 \r")
        
        st = ""
        while ((time.time() - test_start_time) < timeout):
            c1.tsend("%s \r " % pattern2)
            st += s.tresv()
            match = re.search( pattern2, st )
            if (match != None):
                c1.tclose()
                s.tsend("\x03 \r")
                return 1
        print "st=%s" % st
        on_append_report.emit(QString( u"Ошибка приёма данных, где принимающая сторона ВИМ-3U-3"))
        s.tsend("\x03 \r")
        c1.tclose()
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Проверка последовательного порта RS232C_1"

class TestRS232C_2:
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        pattern1 = "SDKFBSKDJFSKDFJSDNBFKSJDFKJSDF"
        pattern2 = "DSFUSHDFKSLJDFHSKLDJFHSDFKLJHS"
        c2 = C2ser()
        c2.topen()
        
        timeout = 3 # secound
        test_start_time = time.time()
        s.a_cmd("stty -icanon -F /dev/ttyS3 speed 115200")
        s.a_cmd("echo \"%s\" > /dev/ttyS3 " % pattern1)
        st = c2.tresv(30)
        if (st != pattern1 ):
            on_append_report.emit(QString( u"Ошибка передачи данных, где передающая сторона ВИМ-3U-3"))
            c2.tclose()
            return -1
        s.tsend("cat /dev/ttyS3 \r")
        st = ""
        while ((time.time() - test_start_time) < timeout):
            c2.tsend("%s \r " % pattern2)
            st += s.tresv()
            match = re.search( pattern2, st )
            if (match != None):
                c2.tclose()
                s.tsend("\x03 \r")
                return 1
        on_append_report.emit(QString( u"Ошибка приёма данных, где принимающая сторона ВИМ-3U-3"))
        s.tsend("\x03 \r")
        c2.tclose()
        return -1
    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Проверка последовательного порта RS232C_2"

class TestTRS_RS485:
    salt = 0
    #a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        # reboot
        s.a_cmd("reboot")
        test_start_time = time.time()
        st = ""
        while ((time.time() - test_start_time) < 20):
            st += s.tresv()
            match = re.search( ur"/ #", st )
            if (match != None):
                s.tsend("\r")
                break

        # run test
        #self.a1_s.a_open()
        pattern1 = "DSKLGJNSDLGKJSDNGKLJSBDGKLSJDG"
        pattern2 = "DSNGKLJDNGLSKJSDGNSLDKGJNSDLKJ"
        
        # start telnetd
        s.a_cmd("ifconfig eth0 192.168.30.2")
        time.sleep(5)
        s.a_cmd("telnetd -l /bin/sh -b 192.168.30.2")
        # open telnet
        HOST = "192.168.30.2"
        tn = telnetlib.Telnet(HOST)
        # physical connect rs485
        #self.a1_s.a_cmd("O 9 1")
        msgBox = QMessageBox()
        msgBox.setText(u"Подключите адаптер RS485 и нажмите ОК")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Ok)
        ret = msgBox.exec_()
        if ( ret != QMessageBox.Ok):
            return -1
        # open RS485
        c2 = RS485ser()
        c2.topen()

        tn.read_until(" # ")
        tn.write("cd /tests \r")
        tn.read_until(" # ")
        tn.write("./fpga.sh write BANK 0 \r")
        tn.read_until(" # ")
        tn.write("./fpga.sh write TRS_PHY_CTRL.EN 1 \r")
        tn.read_until(" # ")
        tn.write("./fpga.sh write TRS_PHY_CTRL.RS232#_RS485 1 \r")
        tn.read_until(" # ")
        tn.write("./fpga.sh write TRS_PHY_CTRL.ECHO485_EN 0 \r")
        tn.read_until(" # ")
        tn.write("./fpga.sh write TRS_PHY_CTRL.TE485 1 \r")
        tn.read_until(" # ")
        
        tn.write("stty -icanon -F /dev/ttyS0 speed 115200 \r")
        tn.read_until(" # ")
        tn.write("./fpga.sh write TRS_PHY_CTRL.DE485 1 \r")
        tn.read_until(" # ")
        tn.write("echo \"%s\" > /dev/ttyS0 \n" % pattern1)
        tn.read_until(" # ")

        timeout = 3 # secound
        test_start_time = time.time()
        st = ""
        res = 0
        while ((time.time() - test_start_time) < timeout):
            st += c2.tresv()
            match = re.search( pattern1, st )
            if (match != None):
                res = 1
                break
        if (res == 0 ):
            print "st=%s" % st
            on_append_report.emit(QString( u"Ошибка передачи данных, где передающая сторона ВИМ-3U-3"))
            tn.write("./fpga.sh write TRS_PHY_CTRL.RS232#_RS485 0 \r")
            tn.read_until(" # ")
            tn.write("./fpga.sh write TRS_PHY_CTRL.TE485 0 \r")
            tn.read_until(" # ")
            tn.write("./fpga.sh write TRS_PHY_CTRL.DE485 0 \r")
            tn.read_until(" # ")
            tn.close()
            c2.tclose()
            on_append_report.emit(QString( u"Отключите RS485 адаптер"))
            #self.a1_s.a_cmd("O 9 0")
            return -1

        tn.write("./fpga.sh write TRS_PHY_CTRL.DE485 0 \r")
        tn.read_until(" # ")
        tn.write("./fpga.sh write TRS_PHY_CTRL.ECHO485_EN 1 \r")
        tn.read_until(" # ")
        c2.tsend("\r ")
        c2.tsend("treshcmd ; echo \"%s\" > /tests/rs485in.dat \r " % pattern2)
        time.sleep(1)
        tn.write("cat /tests/rs485in.dat \r")
        timeout = 2
        test_start_time = time.time()
        st = "" # tn.read_very_eager()
        print "st=%s" % st
        res = 0
        while ((time.time() - test_start_time) < timeout):
            st += tn.read_eager()
            match = re.search( pattern2, st )
            if (match != None):
                res = 1
                break
        if (res == 0 ):
            print "st=%s" % st
            on_append_report.emit(QString( u"Ошибка приёма данных, где принимающая сторона ВИМ-3U-3"))
            tn.write("\x03 \r")
            tn.write("./fpga.sh write TRS_PHY_CTRL.RS232#_RS485 0 \r")
            tn.read_until("result=OK")
            tn.write("./fpga.sh write TRS_PHY_CTRL.TE485 0 \r")
            tn.read_until("result=OK")
            tn.write("./fpga.sh write TRS_PHY_CTRL.ECHO485_EN 0 \r")
            tn.read_until("result=OK")
            tn.close()
            c2.tclose()
            on_append_report.emit(QString( u"Отключите RS485 адаптер"))
            #self.a1_s.a_cmd("O 9 0")
            return -1
        tn.write("rm /tests/rs485in.dat \r")
        tn.read_until(" # ")
        c2.tclose()

        #self.a1_s.a_cmd("O 9 0")
        msgBox = QMessageBox()
        msgBox.setText(u"Отключите адаптер RS485 и нажмите ОК")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Ok)
        ret = msgBox.exec_()
        if ( ret != QMessageBox.Ok):
            return -1

        tn.write("./fpga.sh write TRS_PHY_CTRL.RS232#_RS485 0 \r")
        tn.read_until(" # ")
        tn.write("./fpga.sh write TRS_PHY_CTRL.ECHO485_EN 0 \r")
        tn.read_until(" # ")
        tn.write("./fpga.sh write TRS_PHY_CTRL.TE485 0 \r")
        tn.read_until(" # ")
        tn.close()
        
        s.a_cmd("killall telnetd")
        return 1

    def stop( self, s ):
        s.tsend("\x03 \r")
        return -1
    def name( self ):
        return u"Проверка последовательного порта RS485"



class TestDS0_DS9:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
##        msgBox = QMessageBox()
##        msgBox.setText(u"Убедитесь, что на МКИ светятся светодиоды \"+3.3V\", \"+27V\"")
##        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
##        msgBox.setDefaultButton(QMessageBox.Ok)
##        ret = msgBox.exec_()
##        if ( ret != QMessageBox.Ok):
##            return -1
        
        self.a1_s.a_open()
        for channel in range(0,9)+range(15,22):
            on_append_report.emit(QString( u"Тестирование разовой команды %i" % channel ))
            self.a1_s.a_cmd("C")
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.TEST_MODE_BASE_C+2))
            if (channel <= 9):
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.DSA_T_L_BASE_C+channel))
            if (channel >= 15):
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.DSB_T_L_BASE_C+channel-15))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+1))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+2))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+3))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+4))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GAP_BASE_C))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+1))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+2))
            self.a1_s.a_cmd("S")
            s.a_fpga_write( "RK_IN_CTRL.DS_TA_H 1")
            s.a_fpga_write( "RK_IN_CTRL.DS_TB_H 1")
            s.a_fpga_write( "RK_IN_CTRL.DS_TA_L 0")
            s.a_fpga_write( "RK_IN_CTRL.DS_TB_L 0")

            time.sleep(0.01)
            # check
            if (channel < 8):
                res = s.a_fpga_read("RK_CONFIG0.DS_R%i" % channel)
            if (channel >= 8) and (channel < 10):
                res = s.a_fpga_read("RK_CONFIG1.DS_R%i" % channel)
            if (channel >= 15) and (channel < 19):
                res = s.a_fpga_read("RK_IN0.DS_R%i_P" % channel)
            if (channel >= 19) and (channel < 23):
                res = s.a_fpga_read("RK_IN1.DS_R%i_P" % channel)
            if (res != '0'):
                on_append_report.emit(QString( u"РК %i - не может быть активирована" % channel ))
                return -1;
                
            for k_channel in range(0,9)+range(15,22):
                if (k_channel != channel):
                    if (k_channel < 8):
                        res = s.a_fpga_read("RK_CONFIG0.DS_R%i" % k_channel)
                    if (k_channel >= 8) and (k_channel < 10):
                        res = s.a_fpga_read("RK_CONFIG1.DS_R%i" % k_channel)
                    if (k_channel >= 15) and (k_channel < 19):
                        res = s.a_fpga_read("RK_IN0.DS_R%i_P" % k_channel)
                    if (k_channel >= 19) and (k_channel < 23):
                        res = s.a_fpga_read("RK_IN1.DS_R%i_P" % k_channel)
                    if (res != '1'):
                        on_append_report.emit(QString( u"РК %i и %i возможно замкнуты" % (channel, k_channel) ))
                        return -1;
                    if (k_channel >= 15) and (k_channel < 19):
                        res = s.a_fpga_read("RK_IN0.DS_R%i_N" % k_channel)
                    if (k_channel >= 19) and (k_channel < 23):
                        res = s.a_fpga_read("RK_IN1.DS_R%i_N" % k_channel)
                    if (res != '1'):
                        on_append_report.emit(QString( u"РК %i и %i возможно замкнуты" % (channel, k_channel) ))
                        return -1;

            self.a1_s.a_cmd("W %i 0" %  (self.a1_s.DSA_T_L_BASE_C+channel))
            self.a1_s.a_cmd("W %i 0" %  (self.a1_s.DSB_T_L_BASE_C+channel))
            on_append_report.emit(QString( u"РК %i - Исправна" % channel ))

        self.a1_s.tclose()
        return 1
        #self.a1_s.a_cmd("S")
        #q = self.a1_s.a_read("R 1")
        #self.a1_s.tclose()
        #if (q == "1"):
        #    return 1
        #else:
        #    return -1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"Тест РК0..9"

class TestDS0_DS9_0V_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()
        for v27_s in [18,31]:
##            msgBox = QMessageBox()
##            msgBox.setText(u"Установите на источнике питание напряжение \"27В ВИМ\" в значение \"%i В\"" % v27_s)
##            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
##            msgBox.setDefaultButton(QMessageBox.Ok)
##            ret = msgBox.exec_()
##            if ( ret != QMessageBox.Ok):
##                return -1
            for channel in range(0,9):
                on_append_report.emit(QString( u"Тестирование разовой команды %i" % channel ))
                self.a1_s.a_cmd("C")
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.DSA_T_L_BASE_C+channel))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+1))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+2))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+3))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+4))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GAP_BASE_C))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+1))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+2))
                self.a1_s.a_cmd("S")
                #s.tsend("./fpga.sh octet_write 31 1 \r")
                s.a_fpga_write( "BANK 1")
                s.a_fpga_write( "RK_IN_CTRL.DS_TA_H 1")
                s.a_fpga_write( "RK_IN_CTRL.DS_TB_H 1")
                s.a_fpga_write( "RK_IN_CTRL.DS_TA_L 0")
                s.a_fpga_write( "RK_IN_CTRL.DS_TB_L 0")

                time.sleep(0.01)
                # check
                if (channel < 8):
                    res = s.a_fpga_read("RK_CONFIG0.DS_R%i" % channel)
                if (channel >= 8) and (channel < 10):
                    res = s.a_fpga_read("RK_CONFIG1.DS_R%i" % channel)
                if (res != '0'):
                    on_append_report.emit(QString( u"РК %i - не может быть активирована" % channel ))
                    return -1;
                    
                for k_channel in range(0,9)+range(15,22):
                    if (k_channel != channel):
                        if (k_channel < 8):
                            res = s.a_fpga_read("RK_CONFIG0.DS_R%i" % k_channel)
                        if (k_channel >= 8) and (k_channel < 10):
                            res = s.a_fpga_read("RK_CONFIG1.DS_R%i" % k_channel)
                        if (k_channel >= 15) and (k_channel < 23):
                            res = s.a_fpga_read("RK_IN0P.DS_R%i" % k_channel)
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i и %i возможно замкнуты" % (channel, k_channel) ))
                            return -1;
                        if (k_channel >= 15) and (k_channel < 23):
                            res = s.a_fpga_read("RK_IN0N.DS_R%i" % k_channel)
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i и %i возможно замкнуты" % (channel, k_channel) ))
                            return -1;

                self.a1_s.a_cmd("W %i 0" %  (self.a1_s.DSA_T_L_BASE_C+channel))
                on_append_report.emit(QString( u"РК %i - исправен" % channel ))

        self.a1_s.tclose()
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"РК 0В/Обрыв. Входы. Конфигурационные (DS(0)..DS(9)).  Проверка срабатывания."

class TestDS15_DS22_0V_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()
        for v27_s in [18,31]:
##            msgBox = QMessageBox()
##            msgBox.setText(u"Установите на источнике питание напряжение \"27В ВИМ\" в значение \"%i В\"" % v27_s)
##            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
##            msgBox.setDefaultButton(QMessageBox.Ok)
##            ret = msgBox.exec_()
##            if ( ret != QMessageBox.Ok):
##                return -1
            for channel in range(15,22):
                on_append_report.emit(QString( u"Тестирование разовой команды %i" % channel ))
                self.a1_s.a_cmd("C")
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.DSB_T_L_BASE_C+channel-15))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+1))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+2))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+3))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+4))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GAP_BASE_C))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+1))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+2))
                self.a1_s.a_cmd("S")
                s.a_fpga_write( "BANK 1")
                s.a_fpga_write( "RK_IN_CTRL.DS_TA_H 1")
                s.a_fpga_write( "RK_IN_CTRL.DS_TB_H 1")
                s.a_fpga_write( "RK_IN_CTRL.DS_TA_L 0")
                s.a_fpga_write( "RK_IN_CTRL.DS_TB_L 0")

                time.sleep(0.01)
                # check
                if (channel >= 15) and (channel < 23):
                    res = s.a_fpga_read("RK_IN0P.DS_R%i" % channel)
                if (res != '0'):
                    on_append_report.emit(QString( u"РК %i - не может быть активирована" % channel ))
                    return -1;
                if (channel >= 15) and (channel < 23):
                    res = s.a_fpga_read("RK_IN0N.DS_R%i" % channel)
                if (res != '1'):
                    on_append_report.emit(QString( u"РК %i - не исправна (активен IN0P и IN0N)" % channel ))
                    return -1;
                    
                for k_channel in range(0,9)+range(15,22):
                    if (k_channel != channel):
                        if (k_channel < 8):
                            res = s.a_fpga_read("RK_CONFIG0.DS_R%i" % k_channel)
                        if (k_channel >= 8) and (k_channel < 10):
                            res = s.a_fpga_read("RK_CONFIG1.DS_R%i" % k_channel)
                        if (k_channel >= 15) and (k_channel < 23):
                            res = s.a_fpga_read("RK_IN0P.DS_R%i" % k_channel)
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i и %i сработали одновременно" % (channel, k_channel) ))
                            return -1;
                        if (k_channel >= 15) and (k_channel < 23):
                            res = s.a_fpga_read("RK_IN0N.DS_R%i" % k_channel)
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i и %i сработали одновременно" % (channel, k_channel) ))
                            return -1;

                self.a1_s.a_cmd("W %i 0" %  (self.a1_s.DSB_T_L_BASE_C+channel-15))
                on_append_report.emit(QString( u"РК %i - исправен" % channel ))

        self.a1_s.tclose()
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"РК 0В/Обрыв. Входы. Настраиваемые (DS(15)..DS(22)).  Проверка срабатывания."

class TestDS15_DS22_27V_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()
        for channel in range(15,22):
            on_append_report.emit(QString( u"Тестирование разовой команды %i" % channel ))
            self.a1_s.a_cmd("C")
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.DSB_T_H_BASE_C+channel-15))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+1))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+2))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+3))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+4))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GAP_BASE_C))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+1))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+2))
            self.a1_s.a_cmd("S")
            s.a_fpga_write( "BANK 1")
            s.a_fpga_write( "RK_IN_CTRL.DS_TA_H 0")
            s.a_fpga_write( "RK_IN_CTRL.DS_TB_H 0")
            s.a_fpga_write( "RK_IN_CTRL.DS_TA_L 1")
            s.a_fpga_write( "RK_IN_CTRL.DS_TB_L 1")

            time.sleep(0.01)
            # check
            if (channel >= 15) and (channel < 23):
                res = s.a_fpga_read("RK_IN0N.DS_R%i" % channel)
            if (res != '0'):
                on_append_report.emit(QString( u"РК %i - не может быть активирована" % channel ))
                self.a1_s.tclose()
                return -1;
            if (channel >= 15) and (channel < 23):
                res = s.a_fpga_read("RK_IN0P.DS_R%i" % channel)
            if (res != '1'):
                on_append_report.emit(QString( u"РК %i - не исправна (активен IN0P и IN0N)" % channel ))
                self.a1_s.tclose()
                return -1;
                
            for k_channel in range(0,9)+range(15,22):
                if (k_channel != channel):
                    if (k_channel < 8):
                        res = s.a_fpga_read("RK_CONFIG0.DS_R%i" % k_channel)
                    if (k_channel >= 8) and (k_channel < 10):
                        res = s.a_fpga_read("RK_CONFIG1.DS_R%i" % k_channel)
                    if (k_channel >= 15) and (k_channel < 23):
                        res = s.a_fpga_read("RK_IN0P.DS_R%i" % k_channel)
                    if (res != '1'):
                        on_append_report.emit(QString( u"РК %i и %i сработали одновременно" % (channel, k_channel) ))
                        self.a1_s.tclose()
                        return -1;
                    if (k_channel >= 15) and (k_channel < 23):
                        res = s.a_fpga_read("RK_IN0N.DS_R%i" % k_channel)
                    if (res != '1'):
                        on_append_report.emit(QString( u"РК %i и %i сработали одновременно" % (channel, k_channel) ))
                        self.a1_s.tclose()
                        return -1;
            self.a1_s.a_cmd("W %i 0" %  (self.a1_s.DSB_T_H_BASE_C+channel-15))
            on_append_report.emit(QString( u"РК %i - исправен" % channel ))

        self.a1_s.tclose()
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"РК 27В/Обрыв. Входы. Настраиваемые (DS(15)..DS(22)).  Проверка срабатывания."

class TestDS23_DS24_0V_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()
        for dc_mode in [1,2]:
##            msgBox = QMessageBox()
##            if (dc_mode == 1):
##                msgBox.setText(u"Установите на источнике питание напряжения следующие напряжения:\n 27В ВИМ = 18 В \n 27В РК = 27 В ")
##            if (dc_mode == 2):
##                msgBox.setText(u"Установите на источнике питание напряжения следующие напряжения:\n 27В ВИМ = 31 В \n 27В РК = 27 В ")
##            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
##            msgBox.setDefaultButton(QMessageBox.Ok)
##            ret = msgBox.exec_()
##            if ( ret != QMessageBox.Ok):
##                return -1
            on_append_report.emit(QString( u"Проверка в режим питания %i" % dc_mode ))
            for channel in range(23,24+1):
                on_append_report.emit(QString( u"Тестирование разовой команды %i" % channel ))
                self.a1_s.a_cmd("C")
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.DS_R_PON_BASE_C))
                print "W %i 1" %  (self.a1_s.DS_R_PON_BASE_C)
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+1))
                print "W %i 1" %  (self.a1_s.GA_BASE_C+1)
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+2))
                print "W %i 1" %  (self.a1_s.GA_BASE_C+2)
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+3))
                print "W %i 1" %  (self.a1_s.GA_BASE_C+3)
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+4))
                print "W %i 1" %  (self.a1_s.GA_BASE_C+4)
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GAP_BASE_C))
                print "W %i 1" %  (self.a1_s.GAP_BASE_C)
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+1))
                print "W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+1)
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+2))
                print "W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+2)
                self.a1_s.a_cmd("S")
                s.a_fpga_write( "BANK 1")
                s.a_fpga_write( "RK_OUT_CTRL.DS_T24_MODE 0")
                s.a_fpga_write( "RK_OUT_CTRL.DS_T23_MODE 0")
                s.a_fpga_write( "RK_OUT_CTRL.TEST_OUT_HON 1")
                s.a_fpga_write( "RK_OUT_CTRL.TEST_OUT_LON 0")
                s.a_fpga_write( "RK_OUT.DS_T%i 1" % channel)
                for k_channel in range(23,24+1):
                    if (k_channel != channel):
                        s.a_fpga_write( "RK_OUT.DS_T%i 0" % k_channel)
                
                time.sleep(0.01)
                # check
                res = s.a_fpga_read("RK_OUT_TEST.DS_T%i_RESH" % channel)
                print "res=%s\n" % res
                if (res != '0'):
                    on_append_report.emit(QString( u"РК %i - Ошибка цепи ВСК resh" % channel ))
                    self.a1_s.tclose()
                    return -1;
                res = s.a_fpga_read("RK_OUT_TEST.DS_T%i_RESL" % channel)
                if (res != '1'):
                    on_append_report.emit(QString( u"РК %i - Ошибка цепи ВСК resl" % channel ))
                    self.a1_s.tclose()
                    return -1;
                for k_channel in range(23,24+1):
                    if (k_channel != channel):
                        res = s.a_fpga_read("RK_OUT_TEST.DS_T%i_RESH" % k_channel)
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i - Ошибка цепи ВСК resh (проверка отсутствия замыкания)" % k_channel ))
                            self.a1_s.tclose()
                            return -1;
                        res = s.a_fpga_read("RK_OUT_TEST.DS_T%i_RESL" % k_channel)
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i - Ошибка цепи ВСК resl (проверка отсутствия замыкания)" % k_channel ))
                            self.a1_s.tclose()
                            return -1;
                self.a1_s.a_cmd("S")
                res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSA_R_H_BASE_C+channel-23))
                if (res != '1'):
                    on_append_report.emit(QString( u"РК %i - Ошибка цепи ds_r_h МКИ" % channel ))
                    self.a1_s.tclose()
                    return -1;
                res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSA_R_L_BASE_C+channel-23))
                if (res != '0'):
                    on_append_report.emit(QString( u"РК %i - Ошибка цепи ds_r_l МКИ" % channel ))
                    self.a1_s.tclose()
                    return -1;
                for k_channel in range(23,24+1):
                    if (k_channel != channel):
                        res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSA_R_H_BASE_C+k_channel-23))
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i - Ошибка цепи ds_r_h МКИ (проверка отсутствия замыкания)" % k_channel ))
                            self.a1_s.tclose()
                            return -1;
                        res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSA_R_L_BASE_C+k_channel-23))
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i - Ошибка цепи ds_r_l МКИ (проверка отсутствия замыкания)" % k_channel ))
                            self.a1_s.tclose()
                            return -1;
                s.a_fpga_write( "RK_OUT.DS_T%i 0" % channel)
                on_append_report.emit(QString( u"РК %i - исправен" % channel ))

        self.a1_s.tclose()
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"РК 0В/Обрыв. Выходы.  Проверка срабатывания."

class TestDS23_DS24_27V_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()
        for dc_mode in [1,2]:
##            msgBox = QMessageBox()
##            if (dc_mode == 1):
##                msgBox.setText(u"Установите на источнике питание напряжения следующие напряжения:\n 27В ВИМ = 18 В \n 27В РК = 27 В ")
##            if (dc_mode == 2):
##                msgBox.setText(u"Установите на источнике питание напряжения следующие напряжения:\n 27В ВИМ = 31 В \n 27В РК = 27 В ")
##            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
##            msgBox.setDefaultButton(QMessageBox.Ok)
##            ret = msgBox.exec_()
##            if ( ret != QMessageBox.Ok):
##                return -1
            on_append_report.emit(QString( u"Проверка в режим питания %i" % dc_mode ))
            for channel in range(23,24+1):
                on_append_report.emit(QString( u"Тестирование разовой команды %i" % channel ))
                self.a1_s.a_cmd("C")
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.DS_R_NON_BASE_C))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+1))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+2))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+3))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+4))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GAP_BASE_C))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+1))
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+2))
                self.a1_s.a_cmd("S")
                s.a_fpga_write( "BANK 1")
                s.a_fpga_write( "RK_OUT_CTRL.DS_T24_MODE 1")
                s.a_fpga_write( "RK_OUT_CTRL.DS_T23_MODE 1")
                s.a_fpga_write( "RK_OUT_CTRL.TEST_OUT_HON 0")
                s.a_fpga_write( "RK_OUT_CTRL.TEST_OUT_LON 1")
                s.a_fpga_write( "RK_OUT.DS_T%i 1" % channel)
                for k_channel in range(23,24+1):
                    if (k_channel != channel):
                        s.a_fpga_write( "RK_OUT.DS_T%i 0" % k_channel)
            
                time.sleep(0.01)
                # check
                res = s.a_fpga_read("RK_OUT_TEST.DS_T%i_RESH" % channel)
                if (res != '1'):
                    on_append_report.emit(QString( u"РК %i - Ошибка цепи ВСК resh" % channel ))
                    self.a1_s.tclose()
                    return -1;
                res = s.a_fpga_read("RK_OUT_TEST.DS_T%i_RESL" % channel)
                if (res != '0'):
                    on_append_report.emit(QString( u"РК %i - Ошибка цепи ВСК resl" % channel ))
                    self.a1_s.tclose()
                    return -1;
                for k_channel in range(23,24+1):
                    if (k_channel != channel):
                        res = s.a_fpga_read("RK_OUT_TEST.DS_T%i_RESH" % k_channel)
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i - Ошибка цепи ВСК resh (проверка отсутствия замыкания)" % k_channel ))
                            self.a1_s.tclose()
                            return -1;
                        res = s.a_fpga_read("RK_OUT_TEST.DS_T%i_RESL" % k_channel)
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i - Ошибка цепи ВСК resl (проверка отсутствия замыкания)" % k_channel ))
                            self.a1_s.tclose()
                            return -1;
                self.a1_s.a_cmd("S")
                res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSA_R_H_BASE_C+channel-23))
                if (res != '0'):
                    on_append_report.emit(QString( u"РК %i - Ошибка цепи ds_r_h МКИ" % channel ))
                    self.a1_s.tclose()
                    return -1;
                res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSA_R_L_BASE_C+channel-23))
                if (res != '1'):
                    on_append_report.emit(QString( u"РК %i - Ошибка цепи ds_r_l МКИ" % channel ))
                    self.a1_s.tclose()
                    return -1;
                for k_channel in range(23,24+1):
                    if (k_channel != channel):
                        res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSA_R_H_BASE_C+k_channel-23))
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i - Ошибка цепи ds_r_h МКИ (проверка отсутствия замыкания)" % k_channel ))
                            self.a1_s.tclose()
                            return -1;
                        res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSA_R_L_BASE_C+k_channel-23))
                        if (res != '1'):
                            on_append_report.emit(QString( u"РК %i - Ошибка цепи ds_r_l МКИ (проверка отсутствия замыкания)" % k_channel ))
                            self.a1_s.tclose()
                            return -1;
                s.a_fpga_write( "RK_OUT.DS_T%i 0" % channel)
                on_append_report.emit(QString( u"РК %i - исправен" % channel ))

        self.a1_s.tclose()
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"РК 27В/Обрыв. Выходы.  Проверка срабатывания."
class TestDS12_0V_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()
        for dc_mode in [1,2]:
#            msgBox = QMessageBox()
#            if (dc_mode == 1):
#            msgBox.setText(u"Установите на источнике питание напряжения следующие напряжения:\n 27В ВИМ = 18 В \n 27В РК = 27 В ")
#            if (dc_mode == 2):
#                msgBox.setText(u"Установите на источнике питание напряжения следующие напряжения:\n 27В ВИМ = 31 В \n 27В РК = 27 В ")
#            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
#            msgBox.setDefaultButton(QMessageBox.Ok)
#            ret = msgBox.exec_()
#            if ( ret != QMessageBox.Ok):
#                return -1
            on_append_report.emit(QString( u"Проверка в режим питания %i" % dc_mode ))

            self.a1_s.a_cmd("C")
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.DS_R_PON_BASE_C))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+1))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+2))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+3))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+4))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GAP_BASE_C))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+1))
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+2))
            self.a1_s.a_cmd("S")
            s.a_fpga_write( "BANK 0")
            s.a_fpga_write( "READY_CTRL0.MODE0 0")
            s.a_fpga_write( "READY_CTRL0.MODE1 0")
            s.a_fpga_write( "READY_CTRL0.MODE2 0")
            s.a_fpga_write( "READY_CTRL0.MODE3 0")
            s.a_fpga_write( "READY_CTRL0.EN_WD_RDY 0")
            s.a_fpga_write( "READY_CTRL0.EN_PS_RDY 0")
            #s.a_fpga_write( "READY_CTRL1.PROG_RDY 1")
            
            time.sleep(0.01)
            # check
            #res = s.a_fpga_read("READY_CTRL1.RDY_RES")
            #if (res != '1'):
            #    on_append_report.emit(QString( u"channel 12 - Ошибка самотестирования сигнала средствами ВСК" ))
            #    self.a1_s.tclose()
            #    return -1;
            self.a1_s.a_cmd("S")
            res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSX_R_L_BASE_C))
            if (res != '0'):
                on_append_report.emit(QString( u"РК 12 - МКИ не детектировала сигнал исправности" ))
                self.a1_s.tclose()
                return -1;
            s.a_fpga_write( "READY_CTRL0.MODE0 1")
            s.a_fpga_write( "READY_CTRL0.MODE1 0")
            s.a_fpga_write( "READY_CTRL0.MODE2 0")
            s.a_fpga_write( "READY_CTRL0.MODE3 0")
            s.a_fpga_write( "READY_CTRL0.EN_WD_RDY 0")
            s.a_fpga_write( "READY_CTRL0.EN_PS_RDY 0")
            #s.a_fpga_write( "READY_CTRL1.PROG_RDY 1")

            time.sleep(0.01)
            # check
            #res = s.a_fpga_read("READY_CTRL1.RDY_RES")
            #if (res != '1'):
            #    on_append_report.emit(QString( u"channel 12 - Ошибка самотестирования сигнала средствами ВСК" ))
            #    self.a1_s.tclose()
            #    return -1;
            self.a1_s.a_cmd("S")
            res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_DSX_R_L_BASE_C))
            if (res != '1'):
                on_append_report.emit(QString( u"РК 12 - МКИ не детектировала отсутствие сигнала исправности" ))
                self.a1_s.tclose()
                return -1;
            on_append_report.emit(QString( u"РК 12 - исправен" ))

        self.a1_s.tclose()
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"РК 0В/Обрыв. Сигнал исправности. Проверка срабатывания."

class TestLVTTLDS_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()

        for channel in range(13,14+1):
            on_append_report.emit(QString( u"Проверка канала LVTTL %i" % channel ))
            self.a1_s.a_cmd("C")
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.DS_LV_BASE_C+channel-13))
            self.a1_s.a_cmd("S")
            s.a_fpga_write( "BANK 1")

            time.sleep(0.01)
            # check
            res = s.a_fpga_read("RK_LV.DS_LV%i" % channel)
            if (res != '1'):
                on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 не детектирует сигнал %i" % channel ))
                self.a1_s.tclose()
                return -1;
            for k_channel in range(13,14+1):
                if (channel != k_channel):
                    res = s.a_fpga_read("RK_LV.DS_LV%i" % k_channel)
                    if (res != '0'):
                        on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 детектирует ложное срабатывание сигнала %i" % k_channel ))
                        self.a1_s.tclose()
                        return -1;
            on_append_report.emit(QString( u"Канал %i - OK" % channel ))

        self.a1_s.tclose()
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"РК 0В/Обрыв. Низковольтные разовые команды. Проверка срабатывания."

class TestLVTTL_VPX_G1_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()
        # GA[0..4]
        for channel in range(0,4+1):
            on_append_report.emit(QString( u"Проверка географической адресации бит %i" % channel ))
            self.a1_s.a_cmd("C")
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GA_BASE_C+channel))
            self.a1_s.a_cmd("S")
            s.a_fpga_write( "BANK 2")

            time.sleep(0.01)
            # check
            res = s.a_fpga_read("VPX_G0_IN.GA%i" % channel)
            if (res != '1'):
                on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 не детектирует бит %i" % channel ))
                self.a1_s.tclose()
                return -1;
            for k_channel in range(0,4+1):
                if (channel != k_channel):
                    res = s.a_fpga_read("VPX_G0_IN.GA%i" % k_channel)
                    if (res != '0'):
                        on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 детектирует ложное срабатывание бита %i" % k_channel ))
                        self.a1_s.tclose()
                        return -1;
            on_append_report.emit(QString( u"Бит %i - OK" % channel ))
        # GAP
        on_append_report.emit(QString( u"Проверка флага четности географического адреса" ))
        self.a1_s.a_cmd("C")
        self.a1_s.a_cmd("W %i 1" %  (self.a1_s.GAP_BASE_C))
        self.a1_s.a_cmd("S")
        time.sleep(0.01)
        res = s.a_fpga_read("VPX_G0_IN.GAP")
        if (res != '1'):
            on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 не детектирует сигнал" ))
            self.a1_s.tclose()
            return -1;
        self.a1_s.a_cmd("C")
        self.a1_s.a_cmd("W %i 0" %  (self.a1_s.GAP_BASE_C))
        self.a1_s.a_cmd("S")
        time.sleep(0.01)
        res = s.a_fpga_read("VPX_G0_IN.GAP")
        if (res != '0'):
            on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 обнаружило ложное срабатывание сигнала" ))
            self.a1_s.tclose()
            return -1;
        on_append_report.emit(QString( u"Флаг четности географического адреса - OK"))

        # SYSCON
        on_append_report.emit(QString( u"Проверка сигнала - признака системного разъема" ))
        self.a1_s.a_cmd("C")
        self.a1_s.a_cmd("W %i 1" %  (self.a1_s.SYSCON_BASE_C))
        self.a1_s.a_cmd("S")
        time.sleep(0.01)
        res = s.a_fpga_read("VPX_G0_IN.SYSCON")
        if (res != '1'):
            on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 не детектирует сигнал" ))
            self.a1_s.tclose()
            return -1;
        self.a1_s.a_cmd("C")
        self.a1_s.a_cmd("W %i 0" %  (self.a1_s.SYSCON_BASE_C))
        self.a1_s.a_cmd("S")
        time.sleep(0.01)
        res = s.a_fpga_read("VPX_G0_IN.SYSCON")
        if (res != '0'):
            on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 обнаружило ложное срабатывание сигнала" ))
            self.a1_s.tclose()
            return -1;
        on_append_report.emit(QString( u"Сигнал признак системного разъема - OK" ))

        self.a1_s.tclose()
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"РК 0В/Обрыв. Низковольтные однонаправленные сигналы VPX. Проверка срабатывания."

class TestLVTTL_VPX_G2_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)

    def channel_fpga_read( self, s, channel ):
        if (channel == 0):
            res = s.a_fpga_read("VPX_G1_IN.NVMRO")
        if (channel == 1):
            res = s.a_fpga_read("VPX_G1_IN.MRST")
        if (channel == 2):
            res = s.a_fpga_read("VPX_G1_IN.SRST")
        if (channel == 3):
            res = s.a_fpga_read("VPX_G1_IN.GPOPM")
        return res        
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()
        s.a_fpga_write( "BANK 2")
        s.a_fpga_write( "VPX_G1_CTRL.MRTS_MODE 1")
        s.a_fpga_write( "VPX_G1_CTRL.SRTS_MODE 1")
        s.a_fpga_write( "VPX_G1_CTRL.NVMRO 0")
        s.a_fpga_write( "VPX_G1_CTRL.MRST 0")
        s.a_fpga_write( "VPX_G1_CTRL.SRST 0")
        s.a_fpga_write( "VPX_G1_CTRL.GPOPM 0")



        for channel in range(0,3+1):
            on_append_report.emit(QString( u"Проверка линии %i" % channel))
            self.a1_s.a_cmd("C")
            for i in range(0,3+1):
                self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_DIR_BASE_C+i))
                
            self.a1_s.a_cmd("W %i 1" %  (self.a1_s.REG_INOUT_WR_BASE_C+channel))
            self.a1_s.a_cmd("S")
            res = self.channel_fpga_read(s, channel)
            if (res != '1'):
                on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 не детектирует сигнал линии %i" % channel ))
                self.a1_s.tclose()
                return -1;
            for k_channel in range(0,3+1):
                if (k_channel != channel):
                    res = self.channel_fpga_read(s, k_channel)
                    if (res != '0'):
                        on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 обнаружил ложное срабатывание сигнала в линии %i" % k_channel ))
                        self.a1_s.tclose()
                        return -1;
            on_append_report.emit(QString( u"Линия %i - OK" % channel))

        self.a1_s.tclose()
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"Низковольтные сигналы VPX. Двунаправленные сигналы. Входы. Проверка срабатывания."

class TestLVTTL_VPX_G3_CO:
    salt = 0
    
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)

    def channel_fpga_write( self, s, channel, val ):
        if (channel == 0):
            res = s.a_fpga_write("VPX_G1_OUT.NVMRO %i" % val)
        if (channel == 1):
            res = s.a_fpga_write("VPX_G1_OUT.MRST %i" % val)
        if (channel == 2):
            res = s.a_fpga_write("VPX_G1_OUT.SRST %i" % val)
        if (channel == 3):
            res = s.a_fpga_write("VPX_G1_OUT.GPOPM %i" % val)
        
    def run( self, s , on_append_report ):
        
        self.a1_s.a_open()
        self.a1_s.a_cmd("C")
        for i in range(0,3+1):
            self.a1_s.a_cmd("W %i 0" %  (self.a1_s.REG_INOUT_DIR_BASE_C+i))
        self.a1_s.a_cmd("S")
        s.a_fpga_write( "BANK 2")
        s.a_fpga_write( "VPX_G1_CTRL.MRTS_MODE 1")
        s.a_fpga_write( "VPX_G1_CTRL.SRTS_MODE 1")
        s.a_fpga_write( "VPX_G1_CTRL.NVMRO 1")
        s.a_fpga_write( "VPX_G1_CTRL.MRST 1")
        s.a_fpga_write( "VPX_G1_CTRL.SRST 1")
        s.a_fpga_write( "VPX_G1_CTRL.GPOPM 1")

        for channel in range(0,3+1):
            on_append_report.emit(QString( u"Проверка линии %i" % channel))
            self.channel_fpga_write(s, channel, 1)
            for k_channel in range(0,4+1):
                if (k_channel != channel):
                    self.channel_fpga_write(s, k_channel, 0)
            self.a1_s.a_cmd("S")
            res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_REG_INOUT_RD_BASE_C+channel))
            if (res != '1'):
                on_append_report.emit(QString( u"Ошибка - МКИ не детектирует сигнал линии %i" % channel ))
                self.a1_s.tclose()
                return -1;
            for k_channel in range(0,3+1):
                if (k_channel != channel):
                    res = self.a1_s.a_read("R %i" % (self.a1_s.INPUTS_REG_INOUT_RD_BASE_C+k_channel))
                    if (res != '0'):
                        on_append_report.emit(QString( u"Ошибка - МКИ детектирует ложное срабатывание сигнала линии %i" % k_channel ))
                        self.a1_s.tclose()
                        return -1;
            on_append_report.emit(QString( u"Линия %i - OK" % channel))

        self.a1_s.tclose()
        s.a_fpga_write( "VPX_G1_CTRL.NVMRO 0")
        s.a_fpga_write( "VPX_G1_CTRL.MRST 0")
        s.a_fpga_write( "VPX_G1_CTRL.SRST 0")
        s.a_fpga_write( "VPX_G1_CTRL.GPOPM 0")
        return 1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"Низковольтные сигналы VPX. Двунаправленные сигналы. Выходы. Проверка срабатывания."

class TestXMC_JN12_JN19:
    salt = 0
    
    a2_s = A2ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        self.a2_s.a_open()
        for channel in range(12,19+1):
            on_append_report.emit(QString( u"Проверка мезонинных сигналов JN%i" % channel ))
            self.a2_s.a_cmd("C")
            self.a2_s.a_cmd("W %i 1" %  (self.a2_s.JN8F_BASE_C+channel-8))
            self.a2_s.a_cmd("S")

            time.sleep(0.01)
            # check
            res = self.a2_s.a_read("R %i" % (self.a2_s.JN8C_BASE_C+channel-8))
            if (res != '1'):
                on_append_report.emit(QString( u"Ошибка - МКИМ не детектирует JN%i" % channel ))
                self.a2_s.tclose()
                return -1;
            for k_channel in range(12,19+1):
                if (channel != k_channel):
                    res = self.a2_s.a_read("R %i" % (self.a2_s.JN8C_BASE_C + k_channel - 8))
                    if (res != '0'):
                        on_append_report.emit(QString( u"Ошибка - МКИМ детектирует ложное срабатывание бита %i" % k_channel ))
                        #self.a2_s.tclose()
                        #return -1;
            on_append_report.emit(QString( u"сигнал JN%i - OK" % channel ))

        self.a2_s.tclose()
        return 1
    def stop( self, s ):
        self.a2_s.tclose()
        return -1
    def name( self ):
        return u"Интерфейсные сигналы XMC. JN‑C(12)..JN‑C(19), JN‑F(12)..JN‑F(19). Проверка срабатывания."

class TestXMC_JN8_JN11:
    salt = 0
    
    a2_s = A2ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)

    def channel_fpga_write( self, s, channel, val ):
        if (channel == 8):
            res = s.a_fpga_write("MEZ_OUT.MRSTI_OUT %i" % val)
        if (channel == 9):
            res = s.a_fpga_write("MEZ_OUT.MRSTI_OUT %i" % (1-val))
        if (channel == 10):
            res = s.a_fpga_write("MEZ_OUT.MVMRO_OUT %i" % val)
        if (channel == 11):
            res = s.a_fpga_write("MEZ_OUT.MROOT_OUT %i" % val)

    def channel_fpga_read( self, s, channel ):
        if (channel == 8):
            res = s.a_fpga_read("MEZ_IN.MRSTO")
        if (channel == 9):
            res = s.a_fpga_read("MEZ_IN.MPRESENT")
        if (channel == 10):
            res = s.a_fpga_read("MEZ_IN.MBIST")
        if (channel == 11):
            res = s.a_fpga_read("MEZ_IN.MWAKE")
        return res  
        
    def run( self, s , on_append_report ):
        
        self.a2_s.a_open()
        s.a_fpga_write( "BANK 2")
        on_append_report.emit(QString( u"Проверка входов" ))
        for channel in range(8,11+1):
            on_append_report.emit(QString( u"Проверка мезонинных сигналов JN%i" % channel ))
            self.a2_s.a_cmd("C")
            self.a2_s.a_cmd("W %i 1" %  (self.a2_s.JN8F_BASE_C+channel-8))
            self.a2_s.a_cmd("S")

            time.sleep(0.01)
            # check
            res = self.channel_fpga_read( s, channel )
            if (res != '1'):
                on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 не детектирует JN%i" % channel ))
                self.a2_s.tclose()
                return -1;
            for k_channel in range(8,11+1):
                if (channel != k_channel):
                    res = self.channel_fpga_read( s, k_channel )
                    if (res != '0'):
                        on_append_report.emit(QString( u"Ошибка - ВИМ-3U-3 детектирует ложное срабатывание бита %i" % k_channel ))
                        #self.a2_s.tclose()
                        #return -1;
            on_append_report.emit(QString( u"сигнал JN%i - OK" % channel ))
            
        on_append_report.emit(QString( u"Проверка выходов" ))
        s.a_fpga_write("MEZ_CTRL_MRSTI.CTRL 1")
        for channel in [8,10,11]:
            on_append_report.emit(QString( u"Проверка мезонинных сигналов JN%i" % channel ))
            for i in [8,10,11]:
                self.channel_fpga_write( s, i, 0 )
            self.channel_fpga_write( s, channel, 1 )
            self.a2_s.a_cmd("S")
            time.sleep(0.01)
            # check
            res = self.a2_s.a_read("R %i" %  (self.a2_s.JN8C_BASE_C+channel-8))
            if (res != '1'):
                on_append_report.emit(QString( u"Ошибка - МКИМ не детектирует JN%i" % channel ))
                self.a2_s.tclose()
                return -1;
            if (channel == 11):
                res = self.a2_s.a_read("R %i" %  (self.a2_s.JN8C_BASE_C+1))
                if (res != '0'):
                    on_append_report.emit(QString( u"Ошибка - МКИМ не детектирует JN9" ))
                    self.a2_s.tclose()
                    return -1;
            else:
                res = self.a2_s.a_read("R %i" %  (self.a2_s.JN8C_BASE_C+1))
                if (res != '1'):
                    on_append_report.emit(QString( u"Ошибка - МКИМ не детектирует JN9" ))
                    self.a2_s.tclose()
                    return -1;
            for k_channel in [8,10,11]:
                if (channel != k_channel):
                    res = self.a2_s.a_read("R %i" %  (self.a2_s.JN8C_BASE_C+k_channel-8))
                    if (res != '0'):
                        on_append_report.emit(QString( u"Ошибка - МКИМ детектирует ложное срабатывание бита %i" % k_channel ))
                        self.a2_s.tclose()
                        return -1;
            self.channel_fpga_write( s, channel, 0 )
            on_append_report.emit(QString( u"сигнал JN%i - OK" % channel ))
        self.a2_s.tclose()
        return 1
    def stop( self, s ):
        self.a2_s.tclose()
        return -1
    def name( self ):
        return u"Интерфейсные сигналы XMC. JN‑C(8)..JN‑C(11), JN‑F(8)..JN‑F(11). Проверка срабатывания."

class TestXMC_DiffSignals:
    salt = 0

    def __init__(self):
        self.salt = random.randint(1000, 9999)
        
    def run( self, s , on_append_report ):
        
        time.sleep(1)
        res_test = -1
        
        timeout = 5 # secound
        test_start_time = time.time()
        s.tsend("ethtool enp1s0 \r")
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"Speed\: 1000Mb\/s", st )
            if (match != None):
                res_test = 1
            match = re.search( ur"Speed\: Unknown\!", st )
            if (match != None):
                res_test = -1
            match = re.search( ur"\#", st )
            if (match != None):
                return res_test
            
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        print "s=%s" % st
        return -1

    def stop( self, s ):
        self.a2_s.tclose()
        return -1
    def name( self ):
        return u"Сквозные дифференциальные сигналы XMC. Проверка прохождения сигнала 125 МГц."


class TestTimeMark:
    salt = 0
    a1_s = A1ser()
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, s , on_append_report ):
        self.a1_s.a_open()
        
        timeout = 60 # secound
        test_start_time = time.time()
        s.a_cmd("cd /tests")
        s.a_cmd("./fpga.sh write BANK 0")
        s.a_cmd("./fpga.sh write TMARK_CTRL.DBNC_EN 1")
        s.a_cmd("./fpga.sh write TMARK_CTRL.INT_EN 1")
        #on_append_report.emit(QString( u"Замкните на 1 секунду выводы AUX_CLK на блоке МКИ"))
        self.a1_s.a_cmd("O 2 1")
        self.a1_s.a_cmd("O 2 0")
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += s.tresv()
            match = re.search( ur"IRQ_t (\d+)", st )
            if (match != None):
                on_append_report.emit(QString( u"Прерывание метки времени захвачено (порядковый номер %s)" % match.group(1)))
                st = ""
                self.a1_s.tclose()
                return 1
        print "s=%s" % st
        on_append_report.emit(QString( u"Время ожидания ответа вышло"))
        self.a1_s.tclose()
        return -1
    def stop( self, s ):
        self.a1_s.tclose()
        return -1
    def name( self ):
        return u"Проверка Входа метки времени"

class TestSequences:
    nom = u"0101010101" 
    mac1 = u"000000000000" 
    mac2 = u"000000000000" 
    mac3 = u"000000000000"  
    s = Tser()
    tests = {
        0: TestUbootLoad(),
        1: TestComplexNOR1NOR2(),
        2: LinuxUpload(),
        3: TestReset(),
        4: LinuxLoad(),
        5: TestPortTRS(),
        6: TestScriptsUpload(),
        7: TestSpiFPGA(),
        8: TestNAND(),
        9: TestSpiFRAM1(),
        10: TestSpiFRAM2(),
        11: TestI2CEEPROM(),
        12: TestI2CTERMO(),
        13: TestTEth(),
        14: TestEthAFDX1(),
        15: TestEthAFDX2(),
        16: TestPCIeVPX(),
        17: TestI2CVPX(),
        18: TestPCIeXMC(),
        19: TestI2CXMC(),
        20: TestRS232C_1(),
        21: TestRS232C_2(),
        22: TestTRS_RS485(),
        23: TestXMC_DiffSignals(),
        24: TestDS0_DS9_0V_CO(),
        25: TestDS15_DS22_0V_CO(),
        26: TestDS15_DS22_27V_CO(),
        27: TestDS23_DS24_0V_CO(),
        28: TestDS23_DS24_27V_CO(),
        29: TestDS12_0V_CO(),
        30: TestLVTTLDS_CO(),
        31: TestXMC_JN12_JN19(),
        32: TestXMC_JN8_JN11(),
        33: TestLVTTL_VPX_G1_CO(),
        34: TestLVTTL_VPX_G2_CO(),
        35: TestLVTTL_VPX_G3_CO(),
        36: TestTimeMark(),
    
    }

    def run( self, id, on_append_report ):
        t = self.tests.get( id, TestNULL() )
        self.s.topen()
        t.nom = self.nom
        t.mac1 = self.mac1
        t.mac2 = self.mac2
        t.mac3 = self.mac3
        
        r = t.run(self.s, on_append_report)
        self.s.tclose()
        return  r
    def stop( self, id ):
        t = self.tests.get( id, TestNULL() )
        r = t.stop(self.s)
        self.s.tclose()
        return  r
    def name( self, id ):
        t = self.tests.get( id, TestNULL() )
        return t.name()

class TestAllEEPROM:
    s = Tser()
    salt = 0
    def __init__(self):
        self.salt = random.randint(1000, 9999)
    def run( self, on_ipmi_report ):
        self.s.topen()
        self.s.tsend("cd / \r")
        time.sleep(1)
        self.s.tsend("ifconfig eth0 192.168.30.2 \r")
        time.sleep(3)
        self.s.tsend("ping -c 4 -W 1 192.168.30.1 \r")
        time.sleep(3)
        self.s.tsend("rm -rf /tests \r")
        time.sleep(1)
        self.s.tsend("mkdir ./tests \r")
        time.sleep(1)
        self.s.tsend("cd ./tests \r")
        time.sleep(1)
        self.s.tsend("wget http://192.168.30.1/utils/fmap1.xml \r")
        time.sleep(1)
        self.s.tsend("wget http://192.168.30.1/utils/fpga.sh \r")
        time.sleep(1)
        self.s.tsend("wget http://192.168.30.1/utils/test_i2c_eeprom.sh \r")
        time.sleep(1) 
        self.s.tsend("wget http://192.168.30.1/utils/eeprom.bin \r")
        time.sleep(1)
        self.s.tsend("chmod +x *.sh \r")
        time.sleep(1)
        self.s.tsend("mkdir ./sw_fpga \r")
        time.sleep(1)
        self.s.tsend("cd ./sw_fpga \r")
        time.sleep(1)
        self.s.tsend("wget http://192.168.30.1/utils/sw_fpga/fpga \r")
        time.sleep(1)
        self.s.tsend("chmod +x fpga \r")
        time.sleep(1)
        self.s.tsend("sync \r")
        time.sleep(3)
        
        on_ipmi_report.emit(QString( u"Тестовые скрипты записаны."))
        
        timeout = 600 # secound
        test_start_time = time.time()
        self.s.tsend("cd /tests \r")
        self.s.tsend("./test_i2c_eeprom.sh %i \r" % self.salt)
        st = ""
        while ((time.time() - test_start_time) < timeout):
            st += self.s.tresv()
            match = re.search( ur"result\(%i\)=(OK|ERROR)" % self.salt, st )
            if (match != None):
                if (match.group(1) == "OK"):
                    self.s.tclose()
                    return 1
                else:
                    on_ipmi_report.emit(QString( u"Тест завершился неудачей."))
                    self.s.tclose()
                    return -1
        on_ipmi_report.emit(QString( u"Время ожидания ответа вышло."))
        self.s.tclose()
        return -1

class WriteEEPROM:
    
    s = Tser()

    def run( self, on_ipmi_report ):
        self.s.topen()
        self.s.tsend("cd /tests \r")
        time.sleep(1)
        self.s.tsend("./fpga.sh write I2C_CTRL.EN_INT 1 \r")
        time.sleep(1)
        self.s.tsend("./fpga.sh write I2C_CTRL.EN_XMC 0 \r")
        time.sleep(1)
        self.s.tsend("./fpga.sh write I2C_CTRL.EN_VPX 0 \r")
        time.sleep(2)
        timeout = 10 # secound

        test_start_time = time.time()
        st = ""
        eror = 0
        self.s.tsend("dd if=/tests/eeprom.bin of=/sys/bus/i2c/devices/0-0050/eeprom  \r")
        time.sleep(1)
        while ((time.time() - test_start_time) < timeout):
            st += self.s.tresv()
            match = re.search( ur"256 bytes", st )
            if (match != None):
                on_ipmi_report.emit(QString( u"Запись завершена"))
                eror = 1
                break
        if eror == 0:
            on_ipmi_report.emit(QString( u"Время ожидания ответа вышло"))
            self.s.tclose()
            return -1
    
        test_start_time = time.time()
        st = ""
        eror = 0
        self.s.tsend("dd if=/sys/bus/i2c/devices/0-0050/eeprom of=/tests/eeprom_out.bin bs=256 count=1 \r")
        time.sleep(1)     
        while ((time.time() - test_start_time) < timeout):
            st += self.s.tresv()
            match = re.search( ur"256 bytes", st )
            if (match != None):
                on_ipmi_report.emit(QString( u"Чтение завершено"))
                eror = 1
                break
        if eror == 0:
            on_ipmi_report.emit(QString( u"Время ожидания ответа вышло"))
            self.s.tclose()
            return -1
    
        test_start_time = time.time()
        st = ""
        self.s.tsend("diff -qs /tests/eeprom.bin /tests/eeprom_out.bin \r")
        time.sleep(1)    
        while ((time.time() - test_start_time) < timeout):
            st += self.s.tresv()
            match = re.search( ur"are identical", st )
            if (match != None):
                on_ipmi_report.emit(QString( u"Проверка завершена"))
                self.s.tclose()
                return 1         
        on_ipmi_report.emit(QString( u"Время ожидания ответа вышло"))
        self.s.tclose()
        return -1
    

    
