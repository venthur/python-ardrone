%module idct

%include typemaps.i

%typemap(in) unsigned short out[64] (unsigned short temp[64]){
    $1 = &temp;
}
%typemap(argout) unsigned short out[64]{
    PyObject *o = PyList_New(64);
    int i;
    for(i = 0; i < 64; i++)
    {
        PyList_SetItem(o, i, PyInt_FromLong($1[i]));
    }
    $result = o;
}

%typemap(in) const short in[64] (short temp[64]) {
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


%{
extern void idct(const short in[64], unsigned short out[64]);
%}


extern void idct(const short in[64], unsigned short out[64]);

