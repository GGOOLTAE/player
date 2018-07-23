from PySide import QtGui, QtCore
from PySide.phonon import Phonon
import sys, os
import RPi.GPIO as GPIO
from random import randint

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    


class PemutarMusik(QtGui.QMainWindow) :
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.penampungFile = []
        self.sedangDiputar = False
        self.indeks = 0
        self.posisiTeks = 0
        self.indeksTadi=-1
        self.indeksHapusWarna = -1
        self.volumeYgLalu = 0.5
        self.klikDariTabel = False

        self.inisialisasiMedia()
        self.buatTabel()
        self.buatTombol()
        self.buatSlider()
        self.buatTeks()
        self.layout()
        self.susunSlider()
        self.susunTombol()
        self.rangkai()

        self.connect(self.pemutar, QtCore.SIGNAL('stateChanged(Phonon::State, Phonon::State)'), self.statusBerubah)
        self.connect(self.pemutar, QtCore.SIGNAL('finished()'), self.putarMusik)

        self.pemutar.setTickInterval(1000)
        self.connect(self.pemutar, QtCore.SIGNAL('tick(qint64)'), self.perbaruiWaktu)
        GPIO.add_event_detect(20, GPIO.FALLING, callback=self.my_callback, bouncetime=300)        
        # self.connect(self.pemutar, QtCore.SIGNAL('aboutToFinished()'), print('a'))

    def my_callback(self,channel):
        self.putarAtauPause()
        
    def inisialisasiMedia(self):
        self.suara = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.suara.volumeChanged.connect(self.ubahNilaiVolume)
        self.pemutar = Phonon.MediaObject(self)

        Phonon.createPath(self.pemutar, self.suara)

    def ubahNilaiVolume(self, nilai):
        self.nilaiVolume.setText(str(int(nilai*100//1))+"%")

    def buatTabel(self):
        title = ['Title', 'Size' ,'Directory']
        data = self.penampungFile

        # besarnya kolom
        colcnt = len(title)
        rowcnt = len(data)

        self.tabel = QtGui.QTableWidget(rowcnt, colcnt)

        self.connect(self.tabel, QtCore.SIGNAL('cellDoubleClicked(int, int)'), self.klikTabel)
        self.connect(self.tabel, QtCore.SIGNAL('cellPressed(int, int)'), self.klik)
        # self.connect(self.tabel, QtCore.SIGNAL('currentCellChanged(int, int, int, int)'), self.pilihanBerubah)

        # judul vertikal
        vheader = QtGui.QHeaderView(QtCore.Qt.Orientation.Vertical)
        vheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tabel.setVerticalHeader(vheader)

        # judul horizontal
        hheader = QtGui.QHeaderView(QtCore.Qt.Orientation.Horizontal)
        hheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tabel.setHorizontalHeader(hheader)
        self.tabel.setHorizontalHeaderLabels(title)

        self.updateTabel()

    def buatTombol(self):
        self.tombolStopPlay = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaPlay), "Play/Pause",  self, triggered=self.putarAtauPause)
        self.tombolNext = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaSkipForward), "Lagu selanjutnya",  self, triggered = self.perintahNext)
        self.tombolPrevious = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaSkipBackward), "Lagu Sebelumnya",  self, triggered = self.perintahPrevious)
        self.tombolMaju = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaSeekForward), "Maju 5 Detik",  self, triggered=self.perintahMaju)
        self.tombolMundur = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaSeekBackward), "Mundur 5 Detik",  self, triggered=self.perintahMundur)
        self.tombolStop = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaStop), "Stop Musik",  self, triggered=self.perintahStop)
        self.tombolBukaFile = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_FileIcon), "Cari file mp3", self, triggered=self.dataDariFile)
        self.tombolBukaFolder = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon), "Cari folder Mp3", self, triggered=self.dataDariFolder)
        self.tombolHapus = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_DialogDiscardButton), "Hapus Musik", self, triggered=self.perintahHapus)
        self.tombolLagi = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_BrowserReload), "Ulangi setelah selesai", self, checkable=True)
        self.tombolAcak = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_CommandLink), "Putar Acak", self, checkable=True)

        self.tombolWeb = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_ComputerIcon), "Pergi Ke Web", self, triggered=self.perintahWeb)

    def buatSlider(self):
        self.posisi = Phonon.SeekSlider(self)
        self.volume = Phonon.VolumeSlider(self)

        self.volume.setAudioOutput(self.suara)
        self.posisi.setMediaObject(self.pemutar)

    def perintahWeb(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('Http://mn-belajarpython.blogspot.co.id'))

    def closeEvent(self, event):
        self.destroy()

    def buatTeks(self):
        self.indikator = QtGui.QLabel(''' mn-belajarpython.blogspot.co.id ''')
        self.waktuPutar = QtGui.QLabel("00:00")
        self.waktuTotal = QtGui.QLabel("00:00")
        self.nilaiVolume = QtGui.QLabel('100%')

    def layout(self):
        widgetTengah = QtGui.QWidget()
        self.layoutUtama = QtGui.QVBoxLayout(widgetTengah)
        self.layoutTombol = QtGui.QToolBar()
        self.layoutSlider = QtGui.QGridLayout()

        self.layoutTombol.setMovable(False)
        self.layoutUtama.setSpacing(0)
        self.setCentralWidget(widgetTengah)

    def susunTombol(self):
        self.layoutTombol.addAction(self.tombolStopPlay)
        self.layoutTombol.addAction(self.tombolPrevious)
        self.layoutTombol.addAction(self.tombolMundur)
        self.layoutTombol.addAction(self.tombolStop)
        self.layoutTombol.addAction(self.tombolMaju)
        self.layoutTombol.addAction(self.tombolNext)
        self.layoutTombol.addSeparator()
        self.layoutTombol.addAction(self.tombolBukaFile)
        self.layoutTombol.addAction(self.tombolBukaFolder)
        self.layoutTombol.addSeparator()
        self.layoutTombol.addAction(self.tombolLagi)
        self.layoutTombol.addAction(self.tombolAcak)
        self.layoutTombol.addSeparator()
        self.layoutTombol.addAction(self.tombolWeb)
        self.layoutTombol.addAction(self.tombolHapus)
        self.layoutTombol.addSeparator()
        self.layoutTombol.addWidget(QtGui.QLabel('   '))
        self.layoutTombol.addWidget(self.indikator)

        self.tombolMundur.setEnabled(False)
        self.tombolMaju.setEnabled(False)
        self.tombolStop.setEnabled(False)
        self.tombolNext.setEnabled(False)
        self.tombolPrevious.setEnabled(False)
        self.tombolLagi.setChecked(True)

    def susunSlider(self):
        self.layoutSlider.setColumnStretch(1,1)
        self.layoutSlider.addWidget(self.waktuPutar,0,0)
        self.layoutSlider.addWidget(self.posisi,0,1)
        self.layoutSlider.addWidget(self.waktuTotal,0,2)
        self.layoutSlider.addWidget(self.volume,0,3)
        self.layoutSlider.addWidget(self.nilaiVolume, 0 ,4)

    def rangkai(self):
        self.layoutUtama.addWidget(self.tabel)
        self.layoutUtama.addLayout(self.layoutSlider)

        self.addToolBar( QtCore.Qt.BottomToolBarArea ,self.layoutTombol)

    def updateTabel(self):
        for i in range(self.tabel.rowCount()):
            self.tabel.removeRow(0)
        for i in range(len(self.penampungFile)):
            self.tabel.insertRow(i)
            namaFile = os.path.basename(self.penampungFile[i][0])
            lokasi = str(self.penampungFile[i][1])
            ukuran = QtCore.QFileInfo(self.penampungFile[i][0]).size()

            namaFile = QtGui.QTableWidgetItem(namaFile)
            ukuran = QtGui.QTableWidgetItem(str(ukuran//1000)+" KB")
            durasi = QtGui.QTableWidgetItem(str(lokasi))

            namaFile.setFlags(namaFile.flags() ^ QtCore.Qt.ItemIsEditable)
            ukuran.setFlags(ukuran.flags() ^ QtCore.Qt.ItemIsEditable)
            durasi.setFlags(durasi.flags() ^ QtCore.Qt.ItemIsEditable)

            self.tabel.setItem(i,0,namaFile)
            self.tabel.setItem(i, 1, ukuran)
            self.tabel.setItem(i,2,durasi)
        if self.penampungFile:
            self.ubahWarna()

    def perintahHapus(self):
        terpilih = self.tabel.selectedIndexes()
        if terpilih :
            reply = QtGui.QMessageBox.question(self, 'Konfimasi',
                                                   "apakah anda ingi menghapus item yang terpilih dari daftar putar?", QtGui.QMessageBox.Yes |
                                                   QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            baris=[]
            for i in terpilih :
                if i.row() not in baris :
                    baris.append(i.row())

            for i in baris:
                data = self.tabel.item(i, 0).text()
                if reply == QtGui.QMessageBox.Yes:
                    cocok = False
                    for j in range(len(self.penampungFile)):
                        if os.path.basename(self.penampungFile[j][0]) == data:
                            cocok = True
                            break
                    if cocok:
                        nama = self.penampungFile.pop(j)[0]
                        if self.pemutar.currentSource().fileName() == nama :
                            if self.indeks:
                                self.indeks -=1
                            if self.sedangDiputar :
                                self.putarMusik()
                            else:
                                self.putarMusik()
                                self.perintahStop()
            self.updateTabel()

            if len(self.penampungFile) <= 1 :
                self.tombolNext.setEnabled(False)
                self.tombolPrevious.setEnabled(False)
        else:

            messagebox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Gagal Menghapus", "Silahkan pilih satu atau beberpa file pada tabel\n"
                                                  "untuk menghapusnya dari daftar putar.",
                                          buttons=QtGui.QMessageBox.Ok,
                                          parent=self)
            messagebox.setDefaultButton(QtGui.QMessageBox.Cancel)
            exe = messagebox.exec_()

    def dataDariFile(self):
        dialog = QtGui.QFileDialog(self)                        # memanggil objekFileDialog
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)      # memanggil objek dengan semua tipe file
        dialog.setFilters(["*.mp3", "*.*"])
        if dialog.exec_() == QtGui.QDialog.Accepted:
            path = dialog.selectedFiles()
            for i in path :
                lokasi=QtCore.QFileInfo(i).absolutePath()
                tipe=QtCore.QFileInfo(i).suffix()
                if tipe.lower() == 'mp3' :
                    self.masukanFile([i,lokasi])
                    ada = True
            if ada == False:
                QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Gagal Menambah Musik",
                                  "File yang anda pilih bukan file musik",

                                   "Silahkan pilih folder yang berisi file MP3.").exec_()
            elif self.sedangDiputar == False:
                self.putarMusik()

    def dataDariFolder(self):
        folder = QtGui.QFileDialog.getExistingDirectory(self, "Tentukan Folder", QtCore.QDir.currentPath())
        f = folder

        if  folder:
            folder = QtCore.QDir(folder)
            file = folder.entryList(QtCore.QDir.Files | QtCore.QDir.NoSymLinks)

            ada = False
            for i in file :
                tipe = QtCore.QFileInfo(f+i).suffix()
                if tipe.lower() == 'mp3':
                    self.masukanFile([f+"/"+i, f])
                    ada = True
            if ada == False:
                QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Gagal Menambah Musik",
                                               "File Musik tidak ditemukan pada folder :"+f+""
                                               "Silahkan pilih folder yang berisi file MP3.").exec_()

            elif self.sedangDiputar == False:
                pass
                self.putarMusik()
                self.perintahStop()


    def putarAtauPause(self):
        if self.penampungFile :
            if self.sedangDiputar :
                self.pemutar.pause()
                self.tombolStopPlay.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaPlay))
            else :
                self.tombolStopPlay.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaPause))
                self.pemutar.play()

        else:
            self.dataDariFile()

    def masukanFile(self, data):
        if data not in self.penampungFile :
            self.penampungFile.append(data)

        if len(self.penampungFile) > 1 :
            self.tombolNext.setEnabled(True)
            self.tombolPrevious.setEnabled(True)
        self.updateTabel()

    def dapatkanData(self):
        if len(self.penampungFile) :
            if self.tombolAcak.isChecked() and self.klikDariTabel==False:
                acak = randint(0, len(self.penampungFile)-1)
                while (self.indeks-1 == acak) and len(self.penampungFile)>1 :
                    acak = randint(0, len(self.penampungFile)-1)
                self.indeks = acak
                self.indeks +=1
                return self.penampungFile[self.indeks-1][0]
            else:
                self.klikDariTabel = False
                if self.indeks < len(self.penampungFile) :
                    self.indeks += 1
                    return self.penampungFile[self.indeks-1][0]
                else :
                    if self.tombolLagi.isChecked() :
                        self.indeks = 1
                        return self.penampungFile[self.indeks-1][0]
                    else:
                        self.indeks = 0
                        return  None
        else:
            return None

    def klik(self, baris, kolom):
        self.tabel.selectRow(baris)
        self.tombolHapus.setEnabled(True)

    # def pilihanBerubah(self, baris, kolom, a, b):
    #     self.tabel.selectRow(baris)
    #     print('baris : ', baris)

    def klikTabel(self, baris, kolom):
        self.tabel.selectRow(baris)
        # if self.radio1.isChecked() :
        data = self.tabel.item(baris, 0).text()
        for i in range(len(self.penampungFile)) :
            if os.path.basename(self.penampungFile[i][0]) == data :
                self.indeks=i
                self.klikDariTabel = True
                self.putarMusik()

    def putarMusik(self):
        data = self.dapatkanData()
        if data :
            self.ubahWarna()

            self.pemutar.setCurrentSource(data)
            self.pemutar.play()
            self.tombolStopPlay.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaPause))
            self.namaYangDiPutar = os.path.basename(self.penampungFile[self.indeks-1][0])+"____________________"
        else:
            self.perintahStop()

    def ubahWarna(self):
        if self.indeksHapusWarna >= 0 and self.indeksHapusWarna < self.tabel.rowCount():
            self.tabel.item(self.indeksHapusWarna, 0).setBackground(QtGui.QColor(255, 255, 255))
            self.tabel.item(self.indeksHapusWarna, 1).setBackground(QtGui.QColor(255, 255, 255))
            self.tabel.item(self.indeksHapusWarna, 2).setBackground(QtGui.QColor(255, 255, 255))
        if self.indeks != 0 :
            self.tabel.item(self.indeks - 1, 0).setBackground(QtGui.QColor(85, 170, 255))
            self.tabel.item(self.indeks - 1, 1).setBackground(QtGui.QColor(85, 170, 255))
            self.tabel.item(self.indeks - 1, 2).setBackground(QtGui.QColor(85, 170, 255))
            self.indeksHapusWarna = self.indeks - 1

    def perintahStop(self):
        self.tombolStopPlay.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaPlay))
        self.pemutar.stop()

    def perintahMundur(self):
        waktuPutar = self.pemutar.currentTime()
        if waktuPutar > 5000 :
            self.pemutar.seek(waktuPutar-5000)

    def perintahMaju(self):
        waktuPutar = self.pemutar.currentTime()
        total = self.pemutar.totalTime()
        if total-5000>waktuPutar :
            self.pemutar.seek(waktuPutar+5000)

    def perintahNext(self):
        self.putarMusik()

    def jalankanTeks(self):
        teks =''

        for j in range(27):
            if (self.posisiTeks + j) < len(self.namaYangDiPutar):
                teks += self.namaYangDiPutar[self.posisiTeks + j]
            else:
                teks += self.namaYangDiPutar[(self.posisiTeks + j) - len(self.namaYangDiPutar)]

        self.indikator.setText(''' %s '''%teks)

    def perbaruiWaktu(self, waktu):
        if self.posisiTeks >= len(self.namaYangDiPutar) :
            self.posisiTeks = 0

        self.jalankanTeks()
        self.posisiTeks+=1

        displayTime = QtCore.QTime((waktu/(1000*60*60))% 60, (waktu / 60000) % 60, (waktu / 1000) % 60)
        self.waktuPutar.setText(displayTime.toString('mm:ss'))

        total = self.pemutar.totalTime()
        if total != -1 :
            displayTime = QtCore.QTime((total / (1000 * 60 * 60)) % 60, (total / 60000) % 60, (total / 1000) % 60)
            self.waktuTotal.setText(displayTime.toString('mm:ss'))
        else :
            self.waktuTotal.setText('00:00')

    def perintahPrevious(self):
        if self.tombolAcak.isChecked()==False:
            if self.indeks <= 1 :
                self.indeks = len(self.penampungFile)-1
            else:
                self.indeks -= 2
        self.putarMusik()


    def statusBerubah(self, statusBaru, oldState):
        if statusBaru == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, self.tr("Fatal Error"), self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, self.tr("Error"), self.mediaObject.errorString())

        elif statusBaru == Phonon.PlayingState:
            self.sedangDiputar = True

            self.tombolMundur.setEnabled(True)
            self.tombolMaju.setEnabled(True)
            self.tombolStop.setEnabled(True)

        elif statusBaru == Phonon.StoppedState:
            self.sedangDiputar = False

            if not self.penampungFile:
                self.indikator.setText(''' mn-belajarpython.blogspot.co.id ''')

            self.tombolMundur.setEnabled(False)
            self.tombolMaju.setEnabled(False)
            self.tombolStop.setEnabled(False)

        elif statusBaru == Phonon.PausedState:
            self.sedangDiputar = False

            self.tombolMundur.setEnabled(True)
            self.tombolMaju.setEnabled(True)
            self.tombolStop.setEnabled(False)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = PemutarMusik()
    window.setWindowTitle("Music Player")
    window.show()
    
    sys.exit(app.exec_())

#    try:
#        print("Waiting f or falling edge on port 21")
#        GPIO.wait_for_edge(21, GPIO.RISING)
#        print("Falling edge detected. Here endeth the second lesson.")

#    except KeyboardInterrupt:
#        print('k')
#        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    

