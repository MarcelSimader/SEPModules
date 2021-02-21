#define PY_SSIZE_T_CLEAN
#include <Python.h>

/***	Performs an iteration of the rational approximation algorithm with the inputs start, upperBound and lowerBound. 'microIterations'
* sets the number of iterations to perform before checking the while-loop conditions.*/
static PyObject *iterateRationalApproximation(PyObject *self, PyObject *args) {
	int a, b, lowerA, lowerB, upperA, upperB;
	int microIterations;
	double mantissa, precision;
	
	if(!PyArg_ParseTuple(args, "iiiiiiddi", &a, &b, &lowerA, &lowerB, &upperA, &upperB, &mantissa, &precision, &microIterations)) {
		return NULL;
	}
	
	/*
	*	if result is smaller, set new left bound and do (a + rightA) / (b + rightB)
	*	else set new right bound and do (a + leftA) / (b + leftB)
	*/
	register double ab = (double) a/b;
	register int i;
	while((double) fabs(ab - mantissa) >= precision) {
		// printf("%.20f (%d / %d | %.20f) \n", (double) fabs(ab - mantissa), a, b, (double) mantissa);
		for(i = 0; i < microIterations; i++){
			if(ab == mantissa) break;
			if(ab < mantissa) {
				lowerA = a;
				lowerB = b;
				a += upperA;
				b += upperB;
			} else {
				upperA = a;
				upperB = b;
				a += lowerA;
				b += lowerB;
			}
			ab = (double) a/b;
		}
	}
	return Py_BuildValue("(ii)", a, b);
}

/**
* Returns the sign of an integer by bit operations on it. If the value of the input is 0, the value passed to 'zero' (defaults to 0) is returned.
*/
static PyObject *intSign(PyObject *self, PyObject *args, PyObject *kwargs){
	int num, zero = 0;
	char* kwList[] = {"num", "zero", NULL};
	
	if(!PyArg_ParseTupleAndKeywords(args, kwargs, "i|i", kwList, &num, &zero)){
		return NULL;
	}
	
	return !(num & num) ? PyLong_FromLong(zero) : PyLong_FromLong((num >> 31) | 1);
}
static PyMethodDef cmathsMethods[] = {
	{"iterateRationalApproximation", iterateRationalApproximation, METH_VARARGS, "Perform fast iterations of the rational approximation algorithm."},
	{"intSign", (PyCFunction)(void(*)(void))intSign, METH_VARARGS | METH_KEYWORDS, "Return sign of an integer. If integer is '0', return 'zero' arg."},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef cmathsModule = {
	PyModuleDef_HEAD_INIT,
	"SEPCMaths",
	NULL,
	-1,
	cmathsMethods
};

PyMODINIT_FUNC PyInit_SEPCMaths(void) {
	return PyModule_Create(&cmathsModule);
}