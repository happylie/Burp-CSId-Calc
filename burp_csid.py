# -*- coding: utf-8 -*-
import math
from burp import ITab
from burp import IBurpExtender
from java.awt import BorderLayout
from java.awt import FlowLayout
from java.awt import Font
from java.awt import Dimension
from java.awt import Component
from javax.swing import JTextArea
from javax.swing import Box
from javax.swing import JPanel
from javax.swing import BoxLayout
from javax.swing import JButton
from javax.swing import JTextField
from javax.swing import JLabel
from javax.swing import SwingConstants
from javax.swing.border import EmptyBorder


class BurpExtender(IBurpExtender, ITab):

    def registerExtenderCallbacks(self, callbacks):
        print('Loading...')
        self.helpers = callbacks.getHelpers()
        self.callbacks = callbacks
        self.callbacks.setExtensionName('CSId Calc')
        self.callbacks.addSuiteTab(self)
        print('CSId Calc Extension Loaded!!!')

    def getTabCaption(self):
        return "CSId Calc"

    def getUiComponent(self):
        self.main_panel = JPanel(BorderLayout(5, 5))
        self.main_panel.setBorder(EmptyBorder(20, 20, 20, 20))

        self.action_panel = JPanel(FlowLayout(FlowLayout.LEADING, 10, 10))
        self.sid_label = JLabel('Session ID : ', SwingConstants.LEFT)
        self.sid_label.setFont(Font('Monaco', Font.BOLD, 14))
        self.action_panel.add(self.sid_label, BorderLayout.LINE_START)
        self.sid_input = JTextField('', 50)
        self.action_panel.add(self.sid_input)
        self.calc_button = JButton('Calc', actionPerformed=self.set_result)
        self.action_panel.add(self.calc_button)
        self.clear_button = JButton('Clear', actionPerformed=self.set_clear_text)
        self.action_panel.add(self.clear_button)
        self.main_panel.add(self.action_panel, BorderLayout.PAGE_START)

        self.result_panel = JPanel(FlowLayout(FlowLayout.LEADING, 10, 10))
        self.result_panel.layout = BoxLayout(self.result_panel, BoxLayout.PAGE_AXIS)
        self.result_panel.add(Box.createRigidArea(Dimension(0, 10)))
        self.result_text = JTextArea()
        self.result_text.setEditable(False)
        self.result_text.setAlignmentX(Component.LEFT_ALIGNMENT)
        self.result_panel.add(self.result_text, BorderLayout.CENTER)
        self.main_panel.add(self.result_panel)

        return self.main_panel

    def set_clear_text(self, event):
        self.sid_input.setText('')
        self.result_text.setText('')

    def set_result(self, event):
        sid = self.sid_input.getText()
        if sid:
            ce = CheckEntropy(sid)
            self.result_text.append(ce.get_check())
            self.sid_input.setText('')
        else:
            ret = """
            [+] Result : 
            Not Input Session ID Value
            
            """
            self.result_text.append(ret)


class CheckCharacters:
    """
    # Lower Case : 26
    # Upper Case : 26
    # Lower & Upper Case : 52
    # Arabic numerals : 10
    # Lower Case & Arabic numerals : 36
    # Upper Case & Arabic numerals : 36
    # Lower & Upper Case & Arabic numerals : 62
    """

    def __init__(self, sid):
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
        self.arabic_numerals = '0123456789'
        self.sid = sid

    def __get_lowercase(self):
        for c in self.sid:
            if c in self.alphabet:
                return 26
        return 0

    def __get_uppercase(self):
        for c in self.sid:
            if c in self.alphabet.upper():
                return 26
        return 0

    def __get_numer(self):
        for c in self.sid:
            if c in self.arabic_numerals:
                return 10
        return 0

    def str_length(self):
        lc = self.__get_lowercase()
        up = self.__get_uppercase()
        n = self.__get_numer()
        return lc+up+n


class CheckEntropy:
    def __init__(self, session_id):
        self.sid = session_id.strip()
        self.cc = CheckCharacters(self.sid)

    def __get_check_entropy(self):
        sid_char_len = len(self.sid)
        sid_len = self.cc.str_length()
        sid_strength = round((math.log(sid_len ** sid_char_len) / math.log(2)), 1)
        sid_result = 'Good'
        if int(sid_strength) < 128:
            sid_result = 'Vulnerable(At least 128 Bits)'
        return sid_char_len, sid_len, sid_strength, sid_result

    def get_check(self):
        try:
            data = self.__get_check_entropy()
            ret = """
            [+] Result : 
            ### Session ID Check Entropy ###
            + Session ID : {sid}
            + String Length : {sid_len}
            + Characters : {sid_char_len} Type
            + Strength : {sid_strength} Bits
            + Result : {sid_result}
            
            """.format(sid=self.sid, sid_len=data[0], sid_char_len=data[1], sid_strength=data[2], sid_result=data[3])
            return ret
        except Exception as err:
            print("Check Error:: {err}".format(err=err))
