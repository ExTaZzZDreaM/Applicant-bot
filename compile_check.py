import py_compile,glob
for f in glob.glob('app/*.py'):
    py_compile.compile(f, doraise=True)
print('compiled')
