################################################################################
# Iditarod: A Shavitt graph visualizer
################################################################################
# License: GPL v3.0
# © 2025, Ignacio Fdez. Galván
################################################################################

import vtk
from vtk.util.numpy_support import numpy_to_vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import numpy as np
import re
import os.path

from iditarod import *

class MainWindow(QMainWindow):

  # Change of n_e and 2S for each step vector
  step = {'0': (0, 0), 'u': (1, 1), 'd': (1, -1), '2': (2, 0)}

  def __init__(self, parent = None):
    QMainWindow.__init__(self, parent)
    self.init_defaults()
    self.init_ui()

    icon = QPixmap()
    icon.load(os.path.join(os.path.dirname(__file__), 'images', 'icon.png'))
    icon = QIcon(icon)
    qApp = QApplication.instance()
    qApp.setWindowIcon(icon)

    self.init_vtk()
    self.show()

  def init_defaults(self):
    self.levels = 6
    self.electrons = 6
    self.spin = 0
    self.nras1 = 0
    self.nhole1 = 0
    self.nras3 = 0
    self.nelec3 = 0
    self.restrict = {}
    self.representation = 'symmetric'
    self.operator = {'S': 0, 'to': (), 'from': ()}

  def init_ui(self):
    uic.loadUi(os.path.join(os.path.dirname(__file__), 'ui', 'MainWindow.ui'), self)

    to_block = [self.numorb, self.numel, self.mult, self.ras1, self.hole1, self.ras3, self.elec3, self.rep]
    for w in to_block:
      w.blockSignals(True)

    self.numorb.setValue(self.levels)
    self.numel.setValue(self.electrons)
    self.mult.setValue(round(2*self.spin)+1)
    self.ras1.setMaximum(self.levels)
    self.ras1.setValue(self.nras1)
    self.hole1.setMaximum(2*self.nras1)
    self.hole1.setValue(self.nhole1)
    self.ras3.setMaximum(self.levels)
    self.ras3.setValue(self.nras3)
    self.elec3.setMaximum(2*self.nras3)
    self.elec3.setValue(self.nelec3)
    self.rep.setCurrentText(self.representation)

    for w in to_block:
      w.blockSignals(False)

    self.setCentralWidget(self.centralwidget)

  def init_vtk(self):
    self.ren = vtk.vtkRenderer()
    self.ren.UseDepthPeelingOn()
    self.ren.SetMaximumNumberOfPeels(20)
    self.ren.UseFXAAOn()
    self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
    self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
    self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    # Lookup table for edge colors
    self.colors = vtk.vtkNamedColors()
    self.lookupTable = vtk.vtkLookupTable()
    self.lookupTable.SetNumberOfTableValues(4)
    self.lookupTable.SetTableValue(0, self.colors.GetColor4d('salmon'))
    self.lookupTable.SetTableValue(1, self.colors.GetColor4d('palegoldenrod'))
    self.lookupTable.SetTableValue(2, self.colors.GetColor4d('plum'))
    self.lookupTable.SetTableValue(3, self.colors.GetColor4d('paleturquoise'))
    self.lookupTable.SetTableRange(0, 3)
    self.lookupTable.Build()

    # Create planes
    points = vtk.vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(0, 0, 1)
    points2 = vtk.vtkPoints()
    points2.DeepCopy(points)
    points3 = vtk.vtkPoints()
    points3.DeepCopy(points)
    triangle = vtk.vtkTriangle()
    triangle.GetPointIds().SetId(0, 0)
    triangle.GetPointIds().SetId(1, 1)
    triangle.GetPointIds().SetId(2, 2)
    triangles = vtk.vtkCellArray()
    triangles.InsertNextCell(triangle)
    quad = vtk.vtkPolygon()
    quad.GetPointIds().SetNumberOfIds(4)
    quad.GetPointIds().SetId(0, 0)
    quad.GetPointIds().SetId(1, 1)
    quad.GetPointIds().SetId(2, 2)
    quad.GetPointIds().SetId(3, 3)
    quads = vtk.vtkCellArray()
    quads.InsertNextCell(quad)
    #self.numelPlane = vtk.vtkPlaneSource()
    self.numelPlane = vtk.vtkPolyData()
    self.numelPlane.SetPoints(points)
    self.numelPlane.SetPolys(quads)
    #self.numorbPlane = vtk.vtkPlaneSource()
    self.numorbPlane = vtk.vtkPolyData()
    self.numorbPlane.SetPoints(points2)
    self.numorbPlane.SetPolys(triangles)
    #self.multPlane = vtk.vtkPlaneSource()
    self.multPlane = vtk.vtkPolyData()
    self.multPlane.SetPoints(points3)
    self.multPlane.SetPolys(triangles)

    # Create the basic grid graph
    points = vtk.vtkPoints()
    types = vtk.vtkUnsignedCharArray()
    types.SetName('types')
    self.gridGraph = vtk.vtkMutableDirectedGraph()
    self.gridGraph.SetPoints(points)
    self.gridGraph.GetEdgeData().SetScalars(types)
    self.gridPoly = vtk.vtkGraphToPolyData()
    self.gridPoly.SetInputData(self.gridGraph)

    # Create the wfn graph (selected n_e and S)
    self.wfnGraph = vtk.vtkMutableDirectedGraph()
    self.wfnPoly = vtk.vtkGraphToPolyData()
    self.wfnPoly.SetInputData(self.wfnGraph)

    # Create the CSF graph
    self.csfGraph = vtk.vtkMutableDirectedGraph()
    self.csfPoly = vtk.vtkGraphToPolyData()
    self.csfPoly.SetInputData(self.csfGraph)

    # Create the coupling graph
    self.coupGraph = vtk.vtkMutableDirectedGraph()
    self.coupPoly = vtk.vtkGraphToPolyData()
    self.coupPoly.SetInputData(self.coupGraph)

    # Create transformations
    self.transform = vtk.vtkTransform()
    self.gridTransform = vtk.vtkTransformFilter()
    self.gridTransform.SetTransform(self.transform)
    self.gridTransform.SetInputConnection(self.gridPoly.GetOutputPort())
    self.wfnTransform = vtk.vtkTransformFilter()
    self.wfnTransform.SetTransform(self.transform)
    self.wfnTransform.SetInputConnection(self.wfnPoly.GetOutputPort())
    self.csfTransform = vtk.vtkTransformFilter()
    self.csfTransform.SetTransform(self.transform)
    self.csfTransform.SetInputConnection(self.csfPoly.GetOutputPort())
    self.coupTransform = vtk.vtkTransformFilter()
    self.coupTransform.SetTransform(self.transform)
    self.coupTransform.SetInputConnection(self.coupPoly.GetOutputPort())
    self.numelTransform = vtk.vtkTransformFilter()
    self.numelTransform.SetTransform(self.transform)
    self.numelTransform.SetInputData(self.numelPlane)
    self.numorbTransform = vtk.vtkTransformFilter()
    self.numorbTransform.SetTransform(self.transform)
    self.numorbTransform.SetInputData(self.numorbPlane)
    self.multTransform = vtk.vtkTransformFilter()
    self.multTransform.SetTransform(self.transform)
    self.multTransform.SetInputData(self.multPlane)

    # Create filters
    self.ball = vtk.vtkSphereSource()
    self.ball.SetRadius(0.1)
    self.ball.SetThetaResolution(12)
    self.ball.SetPhiResolution(12)
    self.wfnBalls = vtk.vtkGlyph3D()
    self.wfnBalls.ScalingOff()
    self.wfnBalls.SetSourceConnection(self.ball.GetOutputPort())
    self.wfnBalls.SetInputConnection(self.wfnTransform.GetOutputPort())
    self.wfnTubes = vtk.vtkTubeFilter()
    self.wfnTubes.SetInputConnection(self.wfnTransform.GetOutputPort())
    self.wfnTubes.SetRadius(0.05)
    self.wfnTubes.SetNumberOfSides(6)
    self.csfTubes = vtk.vtkTubeFilter()
    self.csfTubes.SetInputConnection(self.csfTransform.GetOutputPort())
    self.csfTubes.SetRadius(0.08)
    self.csfTubes.SetNumberOfSides(12)
    self.coupTubes = vtk.vtkTubeFilter()
    self.coupTubes.SetInputConnection(self.coupTransform.GetOutputPort())
    self.coupTubes.SetRadius(0.07)
    self.coupTubes.SetNumberOfSides(12)

    # Create mappers
    self.gridMapper = vtk.vtkPolyDataMapper()
    self.gridMapper.SetInputConnection(self.gridTransform.GetOutputPort())
    self.gridMapper.ScalarVisibilityOff()
    self.wfnBallsMapper = vtk.vtkPolyDataMapper()
    self.wfnBallsMapper.SetInputConnection(self.wfnBalls.GetOutputPort())
    self.wfnBallsMapper.ScalarVisibilityOff()
    self.wfnTubesMapper = vtk.vtkPolyDataMapper()
    self.wfnTubesMapper.SetInputConnection(self.wfnTubes.GetOutputPort())
    self.wfnTubesMapper.SetLookupTable(self.lookupTable)
    self.wfnTubesMapper.UseLookupTableScalarRangeOn()
    self.wfnTubesMapper.SetColorModeToMapScalars()
    self.csfMapper = vtk.vtkPolyDataMapper()
    self.csfMapper.SetInputConnection(self.csfTubes.GetOutputPort())
    self.csfMapper.ScalarVisibilityOff()
    self.coupMapper = vtk.vtkPolyDataMapper()
    self.coupMapper.SetInputConnection(self.coupTubes.GetOutputPort())
    self.coupMapper.ScalarVisibilityOff()
    self.numelMapper = vtk.vtkPolyDataMapper()
    self.numelMapper.SetInputConnection(self.numelTransform.GetOutputPort())
    self.numorbMapper = vtk.vtkPolyDataMapper()
    self.numorbMapper.SetInputConnection(self.numorbTransform.GetOutputPort())
    self.multMapper = vtk.vtkPolyDataMapper()
    self.multMapper.SetInputConnection(self.multTransform.GetOutputPort())

    # Add actors
    self.gridActor = vtk.vtkActor()
    self.gridActor.SetMapper(self.gridMapper)
    self.gridActor.GetProperty().SetLineWidth(2)
    self.gridActor.GetProperty().SetColor(self.colors.GetColor3d('silver'))
    self.gridActor.GetProperty().SetOpacity(0.3)
    self.wfnBallsActor = vtk.vtkActor()
    self.wfnBallsActor.SetMapper(self.wfnBallsMapper)
    self.wfnBallsActor.GetProperty().SetColor(self.colors.GetColor3d('hot_pink'))
    self.wfnTubesActor = vtk.vtkActor()
    self.wfnTubesActor.SetMapper(self.wfnTubesMapper)
    self.csfActor = vtk.vtkActor()
    self.csfActor.SetMapper(self.csfMapper)
    self.csfActor.GetProperty().SetColor(self.colors.GetColor3d('white'))
    self.csfActor.GetProperty().SetAmbient(0.8)
    self.csfActor.GetProperty().SetOpacity(0.4)
    self.coupActor = vtk.vtkActor()
    self.coupActor.SetMapper(self.coupMapper)
    self.coupActor.GetProperty().SetColor(self.colors.GetColor3d('red'))
    self.coupActor.GetProperty().SetAmbient(0.8)
    self.coupActor.GetProperty().SetOpacity(0.4)
    self.numelActor = vtk.vtkActor()
    self.numelActor.SetMapper(self.numelMapper)
    self.numelActor.GetProperty().SetColor(self.colors.GetColor3d('paleturquoise'))
    self.numelActor.GetProperty().SetAmbient(1)
    self.numelActor.GetProperty().SetOpacity(0.3)
    self.numorbActor = vtk.vtkActor()
    self.numorbActor.SetMapper(self.numorbMapper)
    self.numorbActor.GetProperty().SetColor(self.colors.GetColor3d('salmon'))
    self.numorbActor.GetProperty().SetAmbient(1)
    self.numorbActor.GetProperty().SetOpacity(0.3)
    self.multActor = vtk.vtkActor()
    self.multActor.SetMapper(self.multMapper)
    self.multActor.GetProperty().SetColor(self.colors.GetColor3d('palegoldenrod'))
    self.multActor.GetProperty().SetAmbient(1)
    self.multActor.GetProperty().SetOpacity(0.3)

    self.ren.AddActor(self.gridActor)
    self.ren.AddActor(self.wfnBallsActor)
    self.ren.AddActor(self.wfnTubesActor)
    self.ren.AddActor(self.csfActor)
    self.ren.AddActor(self.coupActor)

    self.numorb_changed(self.numorb.value())
    self.numel_changed(self.numel.value())
    self.mult_changed(self.mult.value())
    self.rep_changed()

    self.iren.Initialize()
    self.iren.Start()

  def vtk_update(self):
    self.vtkWidget.GetRenderWindow().Render()

  def numorb_changed(self, value):
    self.levels = value
    self.select_numorb.setMaximum(value)
    self.ras1.setMaximum(self.levels)
    self.ras3.setMaximum(self.levels-self.nras1)
    assert 1 <= self.levels <= 35
    self.numel.setMaximum(2*self.levels)
    self.select_numel.setMaximum(2*self.levels)
    self.select_mult.setMaximum(value+1)

    remove = list(range(self.gridGraph.GetNumberOfVertices()))
    if remove:
      self.gridGraph.RemoveVertices(numpy_to_vtk(remove, array_type=vtk.VTK_ID_TYPE))

    create_graph(self.gridGraph, self.levels)

    self.gridPoly.Update()
    self.ren.ResetCamera()
    self.update_wfn()

  def numel_changed(self, value):
    self.electrons = value
    maxmult = min(self.electrons, 2*self.levels-self.electrons)+1
    self.mult.setMaximum(maxmult)
    self.operator_mult.setMaximum(maxmult)
    self.update_wfn()

  def mult_changed(self, value):
    self.spin = (value-1)/2
    n = min(self.electrons, 2*self.levels-self.electrons)
    self.update_wfn()

  def ras1_changed(self, value):
    self.nras1 = value
    self.ras3.setMaximum(self.levels-self.nras1)
    self.hole1.setMaximum(2*self.nras1)
    self.set_gas()

  def ras3_changed(self, value):
    self.nras3 = value
    self.ras1.setMaximum(self.levels-self.nras3)
    self.elec3.setMaximum(2*self.nras3)
    self.set_gas()

  def hole1_changed(self, value):
    self.nhole1 = value
    self.set_gas()

  def elec3_changed(self, value):
    self.nelec3 = value
    self.set_gas()

  def set_gas(self):
    # norb, nelec, nras1, nhole1, nras3, nelec3
    #   is equivalent to this gas setting:
    # [[nras1, 2*nras1-nhole1, 2*nras1], [norb-nras1-nras3, nelec-nelec3, nelec], [nras3, nelec, nelec]]
    #   (the last sublist can be omitted)
    n1 = 2*self.nras1-self.nhole1
    n2 = min(2*self.nras1,self.electrons)
    text = f'{self.nras1} {n1} {n2} ;'
    n1 = max(n2, self.electrons-self.nelec3)
    n2 = self.electrons
    text += f' {self.levels-self.nras1-self.nras3} {n1} {n2}'
    self.gas.setText(text)
    self.gas.editingFinished.emit()

  def gas_changed(self): 
    text = self.gas.text()
    self.restrict = {}
    if text != '':
      ngas = [[int(j) for j in i.split()] for i in text.split(';')]
      assert all([len(i) == 3 for i in ngas])
      n = [0, 0, 0]
      for g in ngas:
        assert g[1] >= n[1]
        assert g[2] >= n[2]
        assert g[2] >= g[1]
        n[0] += g[0]
        assert n[0] <= self.levels
        assert g[2] <= 2*n[0]
        assert g[2] <= self.electrons
        n[1] = g[1]
        n[2] = g[2]
      if n[0] == self.levels:
        assert g[1] == g[2] == self.electrons
      else:
        ngas.append([self.levels-n[0], self.electrons, self.electrons])
      n = 0
      for g in ngas:
        n += g[0]
        if n < self.levels:
          self.restrict[n] = (g[1], g[2])
    self.update_wfn()

  def tdm_changed(self):
    self.update_coupling()

  def operator_mult_changed(self, value):
    self.operator['S'] = (value-1)/2
    self.update_coupling()

  def operator_cre_indices_changed(self):
    self.operator['to'] = tuple(sorted([int(i) for i in self.operator_cre_indices.text().replace(',', ' ').split()]))
    self.update_coupling()

  def operator_ann_indices_changed(self):
    self.operator['from'] = tuple(sorted([int(i) for i in self.operator_ann_indices.text().replace(',', ' ').split()]))
    self.update_coupling()

  def rep_changed(self):
    self.representation = self.rep.currentText()
    # Step vectors in terms of n_e, n_o, S
    steps = np.array([[self.step['0'][0], 1.0, self.step['0'][1]/2],
                      [self.step['u'][0], 1.0, self.step['u'][1]/2],
                      [self.step['2'][0], 1.0, self.step['2'][1]/2]])
    # Transform to the desired projection
    # (0,u,2 step vectors in the absolute x,y,z axes)
    if self.representation == 'cubic':
      # Simple cubic lattice: (x, y, z) -> (n_e/2-S, n_o, n_o-n_e/2-S)
      step_0 = [ 0.0, 1.0, 1.0]
      step_u = [ 0.0, 1.0, 0.0]
      step_2 = [ 1.0, 1.0, 0.0]
      self.rep_description.setText('internal representation in a cubic grid')
    elif self.representation == 'natural':
      # Natural lattice: (x, y, z) -> (n_e, n_o, S)
      step_0 = [ 0.0, 1.0, 0.0]
      step_u = [ 1.0, 1.0, 0.5]
      step_2 = [ 2.0, 1.0, 0.0]
      self.rep_description.setText('(x,y,z) are electrons, orbitals, spin')
    elif self.representation == 'symmetric':
      # FCC lattice: (x, y, z) -> (n_e-n_o, n_o, 2S)  x+y+z even
      step_0 = [-1.0, 1.0, 0.0]
      step_u = [ 0.0, 1.0, 1.0]
      step_2 = [ 1.0, 1.0, 0.0]
      self.rep_description.setText('(x,y,z) are electron excess, orbitals, twice spin')
    elif self.representation == 'canonical':
      # Canonical lattice: (x, y, z) -> (a, b, c) -> (n_o-n_e/2-S, 2S, n_e/2-S)
      step_0 = [ 1.0, 0.0, 0.0]
      step_u = [ 0.0, 1.0, 0.0]
      step_2 = [ 0.0, 0.0, 1.0]
      self.rep_description.setText('(x,y,z) are the (a,b,c) GUGA values')
    elif self.representation == 'projected':
      # Shavitt projection: (x, y, z) -> (-2*a+eps*b, a+b+c, eps*b) -> (n_e+(1+eps)*2S-2n_o, n_o, eps*2S)
      eps = 2/(self.levels+2)
      step_0 = [ 0.0, 1.0, 0.0]
      step_u = [-eps, 1.0, eps]
      step_2 = [-2.0, 1.0, 0.0]
      self.rep_description.setText('the usual GUGA projection of Shavitt graphs')
    else:
      raise ValueError
    matrix = np.linalg.inv(steps) @ np.array([step_0, step_u, step_2])
    self.transform.SetMatrix([*matrix[:,0], 0.0, *matrix[:,1], 0.0, *matrix[:,2], 0.0, 0.0, 0.0, 0.0, 0.0])

    self.ren.ResetCamera()
    self.vtk_update()

  def csf_changed(self):
    idx = csf_to_index(self.wfnGraph, self.csf.text())
    if idx == 0:
      self.csf.setText('')
    if self.select.isEnabled():
      self.select.setValue(idx)
    self.csfGraph.DeepCopy(self.wfnGraph)
    t = self.csfGraph.GetEdgeData().GetScalars()
    remove = list(range(self.csfGraph.GetNumberOfVertices()))
    if remove:
      remove.remove(0)
    v = 0
    nv = 0
    for j in self.csf.text():
      nv = -1
      for i in range(self.csfGraph.GetOutDegree(v)):
        e = int(str(self.csfGraph.GetOutEdge(v, i)))
        if j == stepname[t.GetValue(e)]:
          nv = self.csfGraph.GetTargetVertex(e)
          remove.remove(nv)
      if nv < 0:
        break
      v = nv
    self.csfGraph.RemoveVertices(vtk.util.numpy_support.numpy_to_vtk(remove, array_type=vtk.VTK_ID_TYPE))
    self.csfPoly.Update()
    self.update_coupling()

    self.vtk_update()

  def showGrid_changed(self):
    if self.showGrid.isChecked():
      self.ren.AddActor(self.gridActor)
    else:
      self.ren.RemoveActor(self.gridActor)
    self.vtk_update()

  def showWfn_changed(self):
    if self.showWfn.isChecked():
      self.ren.AddActor(self.wfnTubesActor)
    else:
      self.ren.RemoveActor(self.wfnTubesActor)
    self.vtk_update()

  def showCoup_changed(self):
    if self.showCoup.isChecked():
      self.ren.AddActor(self.coupActor)
    else:
      self.ren.RemoveActor(self.coupActor)
    self.vtk_update()

  def select_changed(self):
    csf = index_to_csf(self.wfnGraph, self.select.value())
    self.csf.setText(csf)
    self.csf_changed()

  def select_numel_changed(self):
    val = self.select_numel.value()
    margin = 0.5
    if val < 0:
      self.ren.RemoveActor(self.numelActor)
    else:
      self.numelPlane.GetPoints().SetPoint(0, val, val/2-(1+np.sqrt(2))*margin, -margin)
      if val < self.levels:
        self.numelPlane.GetPoints().SetPoint(1, val, val-(np.sqrt(2)-1)*margin, val/2+margin)
        self.numelPlane.GetPoints().SetPoint(2, val, self.levels+margin, val/2+margin)
      else:
        self.numelPlane.GetPoints().SetPoint(1, val, self.levels+margin, (2*self.levels-val)/2+(1+np.sqrt(2))*margin)
        self.numelPlane.GetPoints().SetPoint(2, val, self.levels+margin, (2*self.levels-val)/2+(1+np.sqrt(2))*margin)
      self.numelPlane.GetPoints().SetPoint(3, val, self.levels+margin, -margin)
      self.numelPlane.Modified()
      self.ren.AddActor(self.numelActor)
    self.vtk_update()

  def select_numorb_changed(self):
    val = self.select_numorb.value()
    margin = 0.5
    if val < 0:
      self.ren.RemoveActor(self.numorbActor)
    else:
      self.numorbPlane.GetPoints().SetPoint(0, -(2+np.sqrt(5))*margin, val, -margin)
      self.numorbPlane.GetPoints().SetPoint(1, val, val, val/2+np.sqrt(5)/2*margin)
      self.numorbPlane.GetPoints().SetPoint(2, 2*val+(2+np.sqrt(5))*margin, val, -margin)
      self.numorbPlane.Modified()
      self.ren.AddActor(self.numorbActor)
    self.vtk_update()

  def select_mult_changed(self):
    val = (self.select_mult.value()-1)/2
    margin = 0.5
    if val < 0:
      self.ren.RemoveActor(self.multActor)
    else:
      self.multPlane.GetPoints().SetPoint(0, 2*val-margin, 2*val-(1+np.sqrt(5))/2*margin, val)
      self.multPlane.GetPoints().SetPoint(1, 2*(self.levels-val)+(2+np.sqrt(5))*margin, self.levels+margin, val)
      self.multPlane.GetPoints().SetPoint(2, 2*val-margin, self.levels+margin, val)
      self.multPlane.Modified()
      self.ren.AddActor(self.multActor)
    self.vtk_update()

  def update_wfn(self):
    self.wfnGraph.DeepCopy(self.gridGraph)
    try:
      restrictions = [None for i in range(self.levels+1)]
      restrictions[0] = ([0], [0])
      for i,j in self.restrict.items():
        restrictions[i] = (list(range(j[0], j[1]+1)), list(range(j[1]+1)))
      if restrictions[-1] is None:
        restrictions[-1] = ([self.electrons], [round(2*self.spin)])
      restrict(self.wfnGraph, restrictions)
    except AttributeError:
      pass

    self.wfnPoly.Update()
    self.vtk_update()

    c_v = self.wfnGraph.GetNumberOfVertices()
    c_e = self.wfnGraph.GetNumberOfEdges()
    if c_v == 0:
      self.count.setText('No such wave function')
      self.select.setEnabled(False)
      self.csf_changed()
      return

    total_csf = set_counts(self.wfnGraph)

    self.ren.ResetCamera()
    self.csf_changed()

    if total_csf <= 2147483647:
      self.select.setMaximum(total_csf)
      self.select.setEnabled(True)
      self.selectnum.setMaximum(total_csf)
      self.selectnum.setEnabled(True)
    else:
      self.select.setEnabled(False)
      self.selectnum.setEnabled(False)

    text = '{:,}'.format(total_csf).replace(',', ' ')
    if text == '1':
      text += ' CSF'
    else:
      text += ' CSFs'
    if c_v == 1:
      text += f', {c_v} vertex'
    else:
      text += f', {c_v} vertices'
    if c_e == 1:
      text += f', {c_e} edge'
    elif c_e > 0:
      text += f', {c_e} edges'
    self.count.setText(text)

  def update_coupling(self):
    csf = self.csf.text()
    occ = [0]
    ref_b = [0]
    for i in csf:
      occ.append(occ[-1]+self.step[i][0])
      ref_b.append(ref_b[-1]+self.step[i][1])
    occ = np.array(occ)
    ref_b = np.array(ref_b)
    dif_b = np.array([0 for i in occ])

    if csf:
      num_op = np.array([0 for i in occ])
      delta_occ = np.array([0 for i in occ])
      for i in self.operator['from']:
        if i > len(occ)-1:
          csf = False
          break
        num_op[i] += 1
        delta_occ[i:] -= 1
      for i in self.operator['to']:
        if i > len(occ)-1:
          csf = False
          break
        num_op[i] += 1
        delta_occ[i:] += 1
      if sum(num_op) < round(2*self.operator['S']) or sum(num_op)%2 != round(2*self.operator['S'])%2 or sum(num_op) == 0:
        csf = False
      delta_b = [[0, sum(num_op[:i+1])] for i in range(self.levels+1)]
      delta_b[-1][0] = delta_b[-1][1] = round(2*self.operator['S'])
      for i in range(self.levels-1, 0, -1):
        delta_b[i][1] = min(delta_b[i][1], delta_b[i+1][1]+num_op[i+1])
        delta_b[i][0] = max(delta_b[i][1]%2, delta_b[i+1][0]-num_op[i+1])

    if self.tdm.isChecked():
      self.coupGraph.DeepCopy(self.gridGraph)
    else:
      self.coupGraph.DeepCopy(self.wfnGraph)
    remove = list(range(self.coupGraph.GetNumberOfVertices()))
    if csf:
      for v in range(self.coupGraph.GetNumberOfVertices()):
        x, y, z = self.coupGraph.GetPoints().GetPoint(v)
        n_e = round(x)
        n_o = round(y)
        b = round(2*z)
        if n_e == occ[n_o]+delta_occ[n_o]:
          if ref_b[n_o]+b >= delta_b[n_o][0] and abs(ref_b[n_o]-b) <= delta_b[n_o][1]:
            remove.remove(v)
    self.coupGraph.RemoveVertices(vtk.util.numpy_support.numpy_to_vtk(remove, array_type=vtk.VTK_ID_TYPE))

    remove = True
    while remove:
      remove = []
      for v in range(self.coupGraph.GetNumberOfVertices()):
        x, y, z = self.coupGraph.GetPoints().GetPoint(v)
        n_e = round(x)
        n_o = round(y)
        b = round(2*z)
        if self.coupGraph.GetOutDegree(v) == 0:
          if n_o == self.levels:
            pass
          else:
            remove.append(v)
        if n_o in self.restrict:
          if not self.restrict[n_o][0] <= n_e <= self.restrict[n_o][1]:
            remove.append(v)
        if self.coupGraph.GetInDegree(v) == 0:
          if n_o == 0 and n_e == 0 and b == 0:
            pass
          else:
            remove.append(v)
      if remove:
        remove = list(set(remove))
        self.coupGraph.RemoveVertices(numpy_to_vtk(remove, array_type=vtk.VTK_ID_TYPE))

    self.coupPoly.Update()

    self.vtk_update()

  def set_from_csf(self):
    n_o = 0
    n_e = 0
    b = 0
    csf = self.csf.text()
    if len(csf) < 1:
      return
    for i in csf:
      try:
        n_o += 1
        n_e += self.step[i][0]
        b += self.step[i][1]
      except IndexError:
        return
    self.numorb.setValue(n_o)
    self.numel.setValue(n_e)
    self.mult.setValue(b+1)
    self.ras1.setValue(0)
    self.hole1.setValue(0)
    self.ras3.setValue(0)
    self.elec3.setValue(0)
    self.csf_changed()
