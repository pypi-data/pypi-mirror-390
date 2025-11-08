import platform, ctypes, importlib.resources


# import portaudio binary on MacOS
if platform.system() == "Darwin":
   try:
      with importlib.resources.path("CreativePython.bin", "libportaudio.2.dylib") as libpath:
         ctypes.CDLL(str(libpath))
   except Exception:
      pass