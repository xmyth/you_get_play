import sys
import subprocess
import urllib.request

from PyQt4 import QtGui


class YouGetPlay(QtGui.QWidget):

    def __init__(self, parent):
        super(YouGetPlay, self).__init__(parent)

        self.tray = QtGui.QSystemTrayIcon(QtGui.QIcon('icon.png'), self)
        self.menu = QtGui.QMenu(self)

        exitAction = QtGui.QAction(
            "E&xit", self, shortcut="Ctrl+Q",
            statusTip="Exit the application", triggered=self.close)

        self.enableAction = QtGui.QAction(
            "&Enable", self, shortcut='Ctrl+E',
            statusTip='Enable monitor the clipboard', checkable=True)

        self.enableAction.setChecked(True)

        self.menu.addAction(self.enableAction)
        self.menu.addAction(exitAction)

        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip('you-get play')

    def play(self, url):
        p = subprocess.Popen(['you-get', '-p', 'mpv', url])
        p.wait()

    def onClipChanged(self):
        if(QtGui.QApplication.clipboard().mimeData().hasText()):
            text = QtGui.QApplication.clipboard().text()
            print(text)
            if self.enableAction.isChecked():
                try:
                    urllib.request.urlopen(text)
                    print('Playing ... ')
                    if QtGui.QSystemTrayIcon.supportsMessages():
                        self.tray.showMessage('Now Playing ...',  text)
                    self.play(text)
                    print('End')
                except Exception as e:
                    print(e)


def main():
    app = QtGui.QApplication(sys.argv)
    frame = YouGetPlay(None)
    frame.tray.show()
    app.clipboard().dataChanged.connect(frame.onClipChanged)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
