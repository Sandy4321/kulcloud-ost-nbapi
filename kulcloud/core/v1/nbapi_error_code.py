def constant(f):
    def fset(self, value):
        raise SyntaxError
    def fget(self):
        return f()
    return property(fget, fset)

class Error(object):
    @constant
    def MUL_NBAPI_ERROR(self):
        return 0
    @constant
    def ERROR_DB_NONEXIST(self):
        return 1
    @constant
    def ERROR_DB_DISCONNET(self):
        return 2
    @constant
    def ERROR_INPUT_ARGS(self):
        return 3
    
