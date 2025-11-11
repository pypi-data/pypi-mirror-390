################################################################################
# Tools for handling Shavitt graphs (as VTK graph objects)
################################################################################
# License: GPL v3.0
# © 2025, Ignacio Fdez. Galván
################################################################################

import numpy as np
from vtk import VTK_ID_TYPE, VTK_INT
from vtk.util.numpy_support import numpy_to_vtk


# Labels for step vectors
stepname = ['0', 'u', 'd', '2']

# Step order for the lexicographic sort
stepsort = [stepname.index(i) for i in ['2', 'u', 'd', '0']]


# Create a graph containing all possible CSFs with a number of levels
def create_graph(graph, levels):
  # Add all vertices and coordinates
  points = graph.GetPoints()
  for l in range(levels+1):
    for row in range(l+1):
      for x in range(l-row+1):
        graph.AddVertex()
        # Set the coordinates
        n_o = l         # number of orbitals
        n_e = l-row+x   # number of electrons
        S = (l-row-x)/2 # spin quantum number
        points.InsertNextPoint(n_e, n_o, S)

  # Add all edges and types
  types = graph.GetEdgeData().GetScalars()
  v = 0
  for l in range(levels):
    n = (l+1)*(l+2)//2
    for row in range(l+1):
      m = l-row+2
      for x in range(l-row+1):
        # Edge of type u
        graph.AddEdge(v, v+n+row)
        types.InsertNextValue(stepname.index('u'))
        # Edge of type 2
        graph.AddEdge(v, v+n+row+1)
        types.InsertNextValue(stepname.index('2'))
        # Edge of type 0
        graph.AddEdge(v, v+n+row+m)
        types.InsertNextValue(stepname.index('0'))
        # Edge of type d
        if x < l-row:
          graph.AddEdge(v, v+n+row+m+1)
          types.InsertNextValue(stepname.index('d'))
        v += 1


# Apply occupation and spin restrictions to a full graph,
# also setting tail and head vertices
# The restrictions should be in the form of a list of num_orb+1 length,
# where each element is either None (no restriction) or a tuple
# of allowed occupations and (twice) spins at that level, e.g.
#   4-in-4 singlet:
#     [None, None, None, ([4], [0])]
#   with at least 2 electrons in the first 2 orbitals:
#     [None, ([2,3,4], [0,1,2,3,4]), None, ([4], [0])]
def restrict(graph, restrictions):
  # Only single-headed graphs allowed
  target = restrictions[-1]
  assert len(target[0]) == len(target[1]) == 1
  remove = True
  while remove:
    remove = []
    for v in range(graph.GetNumberOfVertices()):
      x, y, z = graph.GetPoints().GetPoint(v)
      n_e = round(x)
      n_o = round(y)
      b = round(2*z)
      if graph.GetOutDegree(v) == 0:
        # Only the selected head node is allowed to have no outgoing edges
        if n_o == len(restrictions)-1 and n_e == target[0][0] and b == target[1][0]:
          graph.head = v
        else:
          remove.append(v)
      elif len(restrictions) > n_o and restrictions[n_o]:
        # Remove vertices not complying with the restrictions at this level
        if n_e not in restrictions[n_o][0] or b not in restrictions[n_o][1]:
          remove.append(v)
      if graph.GetInDegree(v) == 0:
        # Only the root (tail) node is allowed to have no ingoing edges
        if n_o == 0 and n_e == 0 and b == 0:
          graph.tail = v
        else:
          remove.append(v)
    if remove:
      remove = list(set(remove))
      graph.RemoveVertices(numpy_to_vtk(remove, array_type=VTK_ID_TYPE))


# Set vertex and edge data for counting and sorting CSFs
# Return the total CSF count
def set_counts(graph):
  # Count CSFs going through each vertex,
  # note this is done from the head down, to allow lexicographic sorting
  csf_count_array = np.zeros(graph.GetNumberOfVertices(), dtype=int)
  csf_count_array[graph.head] = 1
  # Go through all vertices, level by level
  vertices = [graph.head]
  while vertices:
    # New vertices for next level will be appended here
    new = []
    for v in vertices:
      # For each vertex, add its count value to all parent vertices
      this = csf_count_array[v]
      for i in range(graph.GetInDegree(v)):
        e = int(str(graph.GetInEdge(v, i)))
        nv = graph.GetSourceVertex(e)
        csf_count_array[nv] += this
        new.append(nv)
    vertices = set(new)

  # Assign values to the edges to allow quick CSF<->index conversion
  count_array = np.zeros((graph.GetNumberOfEdges(), 2), dtype=int)
  step_array = graph.GetEdgeData().GetScalars()
  # Go through all vertices, level by level
  vertices = [graph.tail]
  while vertices:
    # New vertices for next level will be appended here
    new = []
    for v in vertices:
      edges = [-1 for i in stepname]
      for i in range(graph.GetOutDegree(v)):
        e = int(str(graph.GetOutEdge(v, i)))
        edges[step_array.GetValue(e)] = e
      # For each vertex, go through its outward edges in the sort order.
      n = 0
      for i in stepsort:
        e = edges[i]
        if e < 0:
          continue
        nv = graph.GetTargetVertex(e)
        new.append(nv)
        # Assign lower and upper partial indices for the CSFs using this edge
        count_array[e,0] = n
        count_array[e,1] = n+csf_count_array[nv]-1
        n += csf_count_array[nv]
    vertices = set(new)

  # Set data to VTK object
  csf_count = numpy_to_vtk(csf_count_array, array_type=VTK_INT)
  csf_count.SetName('count')
  graph.GetVertexData().AddArray(csf_count)
  count = numpy_to_vtk(count_array, array_type=VTK_INT)
  count.SetName('count')
  graph.GetEdgeData().AddArray(count)

  # Return the total CSF count
  return csf_count_array[graph.tail]


# Find the index of a CSF (in lexicographic order)
def csf_to_index(graph, csf):
  if not csf:
    return 0
  idx = 1

  count_array = graph.GetEdgeData().GetArray('count')
  step_array = graph.GetEdgeData().GetScalars()
  v = graph.tail
  # For each step, add the lower count value assigned to the edge
  for t in csf:
    for i in range(graph.GetOutDegree(v)):
      e = int(str(graph.GetOutEdge(v, i)))
      if stepname[step_array.GetValue(e)] == t:
        idx += round(count_array.GetTuple(e)[0])
        break
    else:
      # If the edge does not exist, the CSF does not belong here
      return 0
    v = graph.GetTargetVertex(e)
  if v != graph.head:
    return 0

  return idx


# Find the CSF corresponding to the index (in lexicographic order)
def index_to_csf(graph, idx):
  csf = ''
  if idx == 0:
    return csf

  count_array = graph.GetEdgeData().GetArray('count')
  step_array = graph.GetEdgeData().GetScalars()
  v = graph.tail
  while True:
    # For each step, find the edge containing the index
    for i in range(graph.GetOutDegree(v)):
      e = int(str(graph.GetOutEdge(v, i)))
      count = count_array.GetTuple(e)
      if count[0] < idx <= count[1]+1:
        # Add the step to the CSF string,
        # shift the index and update the vertex
        csf += stepname[step_array.GetValue(e)]
        idx -= count[0]
        v = graph.GetTargetVertex(e)
        break
    else:
      # No edge found (end of graph), finish
      return csf
