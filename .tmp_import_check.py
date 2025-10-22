import os, sys
print("CWD:", os.getcwd())
print("SYS.PATH[0]:", sys.path[0])
try:
    import geoobra_backend_v3.app.main as m
    print("IMPORT OK:", m.__file__)
except Exception as e:
    print("IMPORT ERROR:", repr(e))
