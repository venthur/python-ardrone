%module idct

%include typemaps.i

%typemap(in) unsigned short *out (unsigned short temp[64]){
    $1 = &temp;
}
%typemap(argout) unsigned short *out{
    PyObject *o = PyList_New(64);
    int i;
    for(i = 0; i < 64; i++)
    {
        PyList_SetItem(o, i, PyInt_FromLong($1[i]));
    }
    $result = o;
}

%typemap(in) const short *in (short temp[64]) {
  int i;
  if (!PySequence_Check($input)) {
    PyErr_SetString(PyExc_ValueError, "Expected a sequence");
    return NULL;
  }
  if (PySequence_Length($input) != 64) {
    PyErr_SetString(PyExc_ValueError, "Size mismatch. Expected 64 elements");
    return NULL;
  }
  for (i = 0; i < 64; i++) {
    PyObject *o = PySequence_GetItem($input,i);
    if (PyNumber_Check(o)) {
      temp[i] = (short) PyInt_AsLong(o);
    } else {
      PyErr_SetString(PyExc_ValueError, "Sequence elements must be numbers");
      return NULL;
    }
  }
  $1 = temp;
}

%typemap(in) const short *y (short temp[256]) {
  int i;
  if (!PySequence_Check($input)) {
    PyErr_SetString(PyExc_ValueError, "Expected a sequence");
    return NULL;
  }
  if (PySequence_Length($input) != 256) {
    PyErr_SetString(PyExc_ValueError, "Size mismatch. Expected 256 elements");
    return NULL;
  }
  for (i = 0; i < 256; i++) {
    PyObject *o = PySequence_GetItem($input,i);
    if (PyNumber_Check(o)) {
      temp[i] = (short) PyInt_AsLong(o);
    } else {
      PyErr_SetString(PyExc_ValueError, "Sequence elements must be numbers");
      return NULL;
    }
  }
  $1 = temp;
}

%typemap(in) const short *cb (short temp[64]) {
  int i;
  if (!PySequence_Check($input)) {
    PyErr_SetString(PyExc_ValueError, "Expected a sequence");
    return NULL;
  }
  if (PySequence_Length($input) != 64) {
    PyErr_SetString(PyExc_ValueError, "Size mismatch. Expected 64 elements");
    return NULL;
  }
  for (i = 0; i < 64; i++) {
    PyObject *o = PySequence_GetItem($input,i);
    if (PyNumber_Check(o)) {
      temp[i] = (short) PyInt_AsLong(o);
    } else {
      PyErr_SetString(PyExc_ValueError, "Sequence elements must be numbers");
      return NULL;
    }
  }
  $1 = temp;
}

%typemap(in) const short *cr (short temp[64]) {
  int i;
  if (!PySequence_Check($input)) {
    PyErr_SetString(PyExc_ValueError, "Expected a sequence");
    return NULL;
  }
  if (PySequence_Length($input) != 64) {
    PyErr_SetString(PyExc_ValueError, "Size mismatch. Expected 64 elements");
    return NULL;
  }
  for (i = 0; i < 64; i++) {
    PyObject *o = PySequence_GetItem($input,i);
    if (PyNumber_Check(o)) {
      temp[i] = (short) PyInt_AsLong(o);
    } else {
      PyErr_SetString(PyExc_ValueError, "Sequence elements must be numbers");
      return NULL;
    }
  }
  $1 = temp;
}

%typemap(in) short **block (short temp[256][3]){
    $1 = &temp;
}
%typemap(argout) short **block{
    PyObject *o = PyList_New(256);
    int i;
    for(i = 0; i < 256; i++)
    {
        PyObject *o2 = PyList_New(3);
        PyList_SetItem(o2, 0, PyInt_FromLong($1[i][0]));
        PyList_SetItem(o2, 1, PyInt_FromLong($1[i][1]));
        PyList_SetItem(o2, 2, PyInt_FromLong($1[i][2]));
        PyList_SetItem(o, i, o2);
    }
    $result = o;
}


%{
extern void idct(const short* in, unsigned short *out);
extern void ybr2rgb(const short *y, const short *cb, const short *cr, short **block);
%}


extern void idct(const short* in, unsigned short *out);
extern void ybr2rgb(const short *y, const short *cb, const short *cr, short **block);

