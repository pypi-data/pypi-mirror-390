################################################################################
# Find a Qt interface to import
################################################################################
# License: GPL v3.0
# © 2019-2022, Ignacio Fdez. Galván
################################################################################

try:
  from qtpy.QtCore import Qt
  import qtpy.QtCore as QtCore
  from qtpy.QtWidgets import *
  from qtpy.QtGui import *
  from qtpy import uic
except:
  try:
    from PyQt5.QtCore import Qt
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5 import uic
  except ImportError:
    from PyQt4.QtCore import Qt
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import *
    from PyQt4 import uic
