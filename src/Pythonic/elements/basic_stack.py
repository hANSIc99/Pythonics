from elementmaster import ElementMaster, alphabet
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSignal, QVariant
from PyQt5.QtGui import  QPixmap, QPainter, QColor, QIntValidator
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QWidget, QComboBox, QCheckBox, QFileDialog, QPushButton, QStackedWidget, QLineEdit)
from record_function import Record, Function
from elementeditor import ElementEditor
from PyQt5.QtCore import QCoreApplication as QC
import logging
from time import sleep
from datetime import datetime
from elementmaster import alphabet
import os.path

class ExecStack(ElementMaster):

    pixmap_path = 'images/ExecStack.png'
    child_pos = (False, False)

    def __init__(self, row, column):
        self.row = row
        self.column = column

        # filename, read_mode, write_mode, b_array_limits, n_array_limits, log_state
        filename = None
        read_mode = 0
        write_mode = 0
        b_array_limits = False
        n_array_limits = None
        log_state = False
        self.config = (filename, read_mode, write_mode,
                b_array_limits, n_array_limits, log_state)
        super().__init__(self.row, self.column, QPixmap(self.pixmap_path), True, self.config)
        super().edit_sig.connect(self.edit)
        logging.debug('ExecStack called at row {}, column {}'.format(row, column))

        self.addFunction(StackFunction)

    def __setstate__(self, state):
        logging.debug('__setstate__() called ExecStack')
        self.row, self.column, self.config = state
        super().__init__(self.row, self.column, QPixmap(self.pixmap_path), True, self.config)
        super().edit_sig.connect(self.edit)
        self.addFunction(StackFunction)

    def __getstate__(self):
        logging.debug('__getstate__() called ExecStack')
        return (self.row, self.column, self.config)

    def openEditor(self):
        logging.debug('openEditor() called ExecStack')

    def edit(self):
        logging.debug('edit() called ExecStack')

        # filename, read_mode, write_mode, array_limits, log_state
        self.filename, self.read_mode, self.write_mode, self.b_array_limits, \
            self.n_array_limits, log_state = self.config

        self.returnEditLayout = QVBoxLayout()

        self.returnEdit = ElementEditor(self)
        self.returnEdit.setWindowTitle(QC.translate('', 'Stack'))

        self.top_text = QLabel()
        self.top_text.setText(QC.translate('', 'Stack ...'))

        self.filename_text = QLabel()
        if self.filename:
            self.filename_text.setText(self.filename)
        """
        else:
            self.filename_text.setText(QC.translate('', 'Filename'))
        """

        self.file_button = QPushButton(QC.translate('', 'Choose file'))
        self.file_button.clicked.connect(self.ChooseFileDialog)

        #self.variable_box = QStackedWidget()
        self.writeInput()
        self.readInput()
        self.loadLastConfig()


        self.mode_text = QLabel()
        self.mode_text.setText(QC.translate('', 'Select mode:'))

        self.help_text = QWidget()
        self.help_text_layout = QVBoxLayout(self.help_text)

        # Option: Fixed size
        self.help_text_1 = QLabel()
        # Liste
        self.help_text_1.setText(QC.translate('', 'On input: Write / Read')) 


        # Input: Liste
        self.help_text_2 = QLabel()
        self.help_text_2.setText(QC.translate('', 'Insert /Append'))

        # Option: Remove output
        # Output: Liste: First Out /  Last Out / all Out 
        self.help_text_3 = QLabel()
        self.help_text_3.setText(QC.translate('', 'Help Text 3'))

        self.help_text_layout.addWidget(self.help_text_1)
        self.help_text_layout.addWidget(self.help_text_2)
        self.help_text_layout.addWidget(self.help_text_3)


        self.confirm_button = QPushButton(QC.translate('', 'Ok'))

        # hier logging option einfügen
        self.log_line = QWidget()
        self.ask_for_logging = QLabel()
        self.ask_for_logging.setText(QC.translate('', 'Log output?'))
        self.log_checkbox = QCheckBox()
        self.log_line_layout = QHBoxLayout(self.log_line)
        self.log_line_layout.addWidget(self.ask_for_logging)
        self.log_line_layout.addWidget(self.log_checkbox)
        self.log_line_layout.addStretch(1)


        if log_state:
            self.log_checkbox.setChecked(True)

        self.confirm_button.clicked.connect(self.returnEdit.closeEvent)
        self.returnEdit.window_closed.connect(self.edit_done)
        self.returnEditLayout.addWidget(self.top_text)
        self.returnEditLayout.addWidget(self.filename_text)
        self.returnEditLayout.addWidget(self.file_button)
        self.returnEditLayout.addWidget(self.mode_text)
        self.returnEditLayout.addWidget(self.write_input)
        self.returnEditLayout.addWidget(self.read_input)
        self.returnEditLayout.addWidget(self.help_text)
        self.returnEditLayout.addStretch(1)
        self.returnEditLayout.addWidget(self.log_line)
        self.returnEditLayout.addWidget(self.confirm_button)
        self.returnEdit.setLayout(self.returnEditLayout)
        self.returnEdit.show()

    def loadLastConfig(self):

        self.select_read_mode.setCurrentIndex(self.read_mode)
        self.select_write_mode.setCurrentIndex(self.write_mode)

        if self.b_array_limits:
            self.enableArrLimits()
            self.array_limits_cbox.setChecked(True)
            if self.n_array_limits:
                self.max_array_elements.setText(str(self.n_array_limits))

        else:
            self.diableArrLimits()
            self.array_limits_cbox.setChecked(False)


    def ChooseFileDialog(self, event):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, \
                QC.translate('', 'Choose file'),"","All Files (*);;Text Files (*.txt)", \
                options=options)
        if fileName:
            logging.debug('ChooseFileDialog() called with filename: {}'.format(fileName))
            self.filename = fileName
            self.filename_text.setText(self.filename)

    def writeInput(self):

        self.write_input = QWidget()
        self.write_layout = QVBoxLayout(self.write_input)

        self.write_input_line = QWidget()
        self.write_input_layout = QHBoxLayout(self.write_input_line)

        self.array_config = QWidget()
        self.array_config_layout = QHBoxLayout(self.array_config)

        self.outpub_behaviour = QWidget()
        self.output_behaviour_layout = QHBoxLayout()

        self.write_txt = QLabel()
        self.write_txt.setText(QC.translate('', 'Do this with input:'))

        self.select_write_mode = QComboBox()
        self.select_write_mode.addItem(QC.translate('', 'Nothing'), QVariant('none'))
        self.select_write_mode.addItem(QC.translate('', 'Insert'), QVariant('i'))
        self.select_write_mode.addItem(QC.translate('', 'Append'), QVariant('a'))

        # maximum array size
        self.array_limits_cbox = QCheckBox()
        self.array_limits_cbox.stateChanged.connect(self.toggleArrayLimits)

        

        self.array_limit_txt = QLabel()
        self.array_limit_txt.setText(QC.translate('', 'Max. array elements:'))

        self.max_array_elements = QLineEdit()
        self.max_array_elements.setValidator(QIntValidator(1, 999))
        self.max_array_elements.setPlaceholderText(QC.translate('', 'Default value: 20'))


        self.array_config_layout.addWidget(self.array_limits_cbox)
        self.array_config_layout.addWidget(self.array_limit_txt)
        self.array_config_layout.addWidget(self.max_array_elements)



        self.write_input_layout.addWidget(self.write_txt)
        self.write_input_layout.addWidget(self.select_write_mode)
        #self.write_layout.addWidget(self.array_limits)

        self.write_layout.addWidget(self.write_input_line)
        self.write_layout.addWidget(self.array_config)

        #self.variable_box.addWidget(self.write_input)

    def toggleArrayLimits(self, event):

        #einzeln aufrufen beim laden der config

        if self.array_limits_cbox.isChecked():
            self.enableArrLimits()
        else:
            self.diableArrLimits()
            
    def enableArrLimits(self):

        self.max_array_elements.setEnabled(True)
        self.max_array_elements.setPlaceholderText(QC.translate('', 'Default value: 20'))

    def diableArrLimits(self):

        self.max_array_elements.setEnabled(False)
        self.max_array_elements.setPlaceholderText(QC.translate('', 'Unlimited'))


    def readInput(self):

        self.read_input = QWidget()
        self.read_layout = QHBoxLayout(self.read_input)

        self.read_txt = QLabel()
        self.read_txt.setText(QC.translate('', 'Do this when triggered:'))

        self.select_read_mode = QComboBox()
        self.select_read_mode.addItem(QC.translate('', 'Nothing'), QVariant('none'))
        self.select_read_mode.addItem(QC.translate('', 'Pass through'), QVariant('pass'))
        self.select_read_mode.addItem(QC.translate('', 'First out'), QVariant('fo'))
        self.select_read_mode.addItem(QC.translate('', 'Last out'), QVariant('lo'))
        self.select_read_mode.addItem(QC.translate('', 'All out'), QVariant('all'))


        self.read_layout.addWidget(self.read_txt)
        self.read_layout.addWidget(self.select_read_mode)


    def edit_done(self):
        logging.debug('edit_done() called ExecStack' )

        if self.max_array_elements.text() == '':
            n_array_limits = None        
        else:
            n_array_limits = int(self.max_array_elements.text())

        log_state = self.log_checkbox.isChecked()
        write_mode = self.select_write_mode.currentIndex()
        read_mode = self.select_read_mode.currentIndex()
        b_array_limits = self.array_limits_cbox.isChecked()
        n_array_limits
        filename = self.filename
        # filename, read_mode, write_mode, b_array_limits, n_array_limits, log_state
        self.config = (filename, read_mode, write_mode, b_array_limits, n_array_limits, log_state)
        self.addFunction(StackFunction)

class StackFunction(Function):

    def __init__(self, config, b_debug, row, column):
        super().__init__(config, b_debug, row, column)

    def execute(self, record):

        # filename, read_mode, write_mode, b_array_limits, n_array_limits, log_state
        filename, read_mode, write_mode, b_array_limits, n_array_limits, log_state = self.config

        if not filename:
            raise OSError(QC.translate('', 'Filename not specified'))

        
        if not n_array_limits:
            n_array_limits = 20


        if write_mode == 0: # Nothing
            record = 'Nothing'
        elif write_mode == 1: # Insert
            record = 'Insert'
        elif write_mode == 3: # Append
            record = 'Append'

        if read_mode == 0: # Nothing
            record += ' Nothing'
        elif read_mode == 1: # Pass through
            record += ' pass throug'
        elif read_mode == 2: # First Out
            record += ' first out'
        elif read_mode == 3: # Last out
            record += ' last out'
        elif read_mode == 4: # Last out
            record += ' all out'

        log_txt = '{{BASIC STACK}}           Return to {}|{} {} {}'.format(
                filename, write_mode, b_array_limits, n_array_limits)

        result = Record(self.getPos(), (self.row +1, self.column), record,
                log=log_state, log_txt=log_txt)
        return result

