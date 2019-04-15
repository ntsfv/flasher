# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config028.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Config028(object):
    def setupUi(self, Config028):
        Config028.setObjectName("Config028")
        Config028.resize(566, 138)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Config028)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tconfig_frm_cfg = QtWidgets.QFrame(Config028)
        self.tconfig_frm_cfg.setEnabled(False)
        self.tconfig_frm_cfg.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tconfig_frm_cfg.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tconfig_frm_cfg.setObjectName("tconfig_frm_cfg")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tconfig_frm_cfg)
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl_warn0 = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_warn0.setTextFormat(QtCore.Qt.RichText)
        self.lbl_warn0.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_warn0.setObjectName("lbl_warn0")
        self.verticalLayout.addWidget(self.lbl_warn0)
        self.lbl_cfgword = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_cfgword.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_cfgword.setObjectName("lbl_cfgword")
        self.verticalLayout.addWidget(self.lbl_cfgword)
        self.verticalLayout_2.addWidget(self.tconfig_frm_cfg)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)

        self.retranslateUi(Config028)
        QtCore.QMetaObject.connectSlotsByName(Config028)

    def retranslateUi(self, Config028):
        _translate = QtCore.QCoreApplication.translate
        Config028.setWindowTitle(_translate("Config028", "Form"))
        self.lbl_warn0.setText(_translate("Config028", "<html><head/><body><p><span style=\" color:#ef2929;\">Внимание! Изменяйте состояние конфигурации с осторожностью!</span></p></body></html>"))
        self.lbl_cfgword.setText(_translate("Config028", "<html><head/><body><p><span style=\" font-weight:600;\">CFGWORD 028</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Config028 = QtWidgets.QWidget()
    ui = Ui_Config028()
    ui.setupUi(Config028)
    Config028.show()
    sys.exit(app.exec_())

