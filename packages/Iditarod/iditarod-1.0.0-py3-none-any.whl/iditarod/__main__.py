import sys
from iditarod import QApplication
from iditarod.iditarod import MainWindow

def main():
  app = QApplication(sys.argv)
  window = MainWindow()
  sys.exit(app.exec_())

if __name__ == "__main__":
  main()
