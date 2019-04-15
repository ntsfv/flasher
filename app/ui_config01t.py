# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config01t.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Config01T(object):
    def setupUi(self, Config01T):
        Config01T.setObjectName("Config01T")
        Config01T.resize(545, 138)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Config01T)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tconfig_frm_cfg = QtWidgets.QFrame(Config01T)
        self.tconfig_frm_cfg.setEnabled(False)
        self.tconfig_frm_cfg.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tconfig_frm_cfg.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tconfig_frm_cfg.setObjectName("tconfig_frm_cfg")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tconfig_frm_cfg)
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

        self.retranslateUi(Config01T)
        QtCore.QMetaObject.connectSlotsByName(Config01T)

    def retranslateUi(self, Config01T):
        _translate = QtCore.QCoreApplication.translate
        Config01T.setWindowTitle(_translate("Config01T", "Form"))
        self.lbl_warn0.setText(_translate("Config01T", "<html><head/><body><p><span style=\" color:#ef2929;\">Внимание! Изменяйте состояние конфигурации с осторожностью!</span></p></body></html>"))
        self.lbl_cfgword.setText(_translate("Config01T", "<html><head/><body><p><span style=\" font-weight:600;\">CFGWORD 01T</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Config01T = QtWidgets.QWidget()
    ui = Ui_Config01T()
    ui.setupUi(Config01T)
    Config01T.show()
    sys.exit(app.exec_())

