# Add moderngl to blender's python module.
def install_lib(libname):
    from subprocess import call
    pp = bpy.app.binary_path_python
    call([pp, "-m", "ensurepip", "--user"])
    call([pp, "-m", "pip", "install", "--user", libname])