import sys
import subprocess
import urllib.request
import pickle
from functools import partial
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
        self.history = {'urls':[], 'titles':{}}
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

    def append_history(self, title, url):
        if url in self.history['urls']:
            self.history['urls'].remove(url)
            del self.history['titles'][url]
        if len(self.history['urls']) > 10:
            del self.history['titles'][self.history['urls'][0]]
            self.history['urls'] = self.history['urls'][1:]
        self.history['urls'].append(url)
        self.history['titles'][url] = title
        self.update_history_menu()

    def update_history_menu(self):
        self.historyMenu.clear()
        last = None
        for url in self.history['urls']:
            title = self.history['titles'][url]
            action = QtGui.QAction(title, self, triggered=partial(self.play, title, url))
            self.historyMenu.insertAction(last, action)
            last = action

    def play(self, title, url):
        subprocess.run(['you-get', '-p', 'mpv', url], stdout=subprocess.PIPE)
        self.append_history(title, url)

    def get_title(self, url):
        site, title = (None, None)
        p = subprocess.run(['you-get','-i',url], stdout=subprocess.PIPE)
        for line in p.stdout.splitlines():
            try:
                line = line.decode('utf-8')
            except:
                try:
                    line = line.decode('gbk')
                except:
                    pass
            if line.lower().startswith('site:'):
                site = line[5:].strip()
                
            if line.lower().startswith('title:'):
                title = line[6:].strip()
        return '@'.join([title,site])   

    def onClipChanged(self):
        if(QtGui.QApplication.clipboard().mimeData().hasText()):
            text = QtGui.QApplication.clipboard().text()
            if self.enableAction.isChecked():
                try:
                    urllib.request.urlopen(text)
                    title = self.get_title(text)
                    if QtGui.QSystemTrayIcon.supportsMessages():
                        self.tray.showMessage('Now Playing ...', title)
                    self.play(title, text)
                except Exception as e:
                    print(e)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    frame = YouGetPlay(None)
    frame.tray.show()
    app.clipboard().dataChanged.connect(frame.onClipChanged)
    sys.exit(app.exec_())
