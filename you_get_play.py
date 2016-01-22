import sys
import subprocess
import urllib.request
import pickle
from PyQt4 import QtGui


class YouGetPlay(QtGui.QWidget):
    __HISTORY_FILENAME__ = '.player_history'

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

        self.historyMenu = QtGui.QMenu("&History")

        self.enableAction.setChecked(True)

        self.menu.addMenu(self.historyMenu)
        self.menu.addAction(self.enableAction)
        self.menu.addAction(exitAction)

        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip('you-get play')
        self.history = []
        self.load_history()

    def close(self):
        self.save_history()
        super().close()

    def load_history(self):
        try:
            with open(self.__HISTORY_FILENAME__, 'rb') as f:
                self.history = pickle.load(f)
        except:
            pass
        self.update_history_menu()

    def save_history(self):
        with open(self.__HISTORY_FILENAME__, 'wb') as f:
            pickle.dump(self.history, f, -1)

    def append_history(self, url):
        if len(self.history) > 10:
            self.history = self.history[1:]
        self.history.append(url)
        self.update_history_menu()

    def update_history_menu(self):
        self.historyMenu.clear()
        last = None
        for url in self.history:
            action = QtGui.QAction(url, self, triggered=lambda: self.play(url))
            self.historyMenu.insertAction(last, action)
            last = action

    def play(self, url):
        p = subprocess.Popen(['you-get', '-p', 'mpv', url])
        p.wait()
        if url in self.history:
            self.history.remove(url)
        self.append_history(url)

    def onClipChanged(self):
        if(QtGui.QApplication.clipboard().mimeData().hasText()):
            text = QtGui.QApplication.clipboard().text()
            print(text)
            if self.enableAction.isChecked():
                try:
                    urllib.request.urlopen(text)
                    print('Playing ... ')
                    if QtGui.QSystemTrayIcon.supportsMessages():
                        self.tray.showMessage('Now Playing ...', text)
                    self.play(text)
                    print('End')
                except Exception as e:
                    print(e)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    frame = YouGetPlay(None)
    frame.tray.show()
    app.clipboard().dataChanged.connect(frame.onClipChanged)
    sys.exit(app.exec_())
