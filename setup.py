from setuptools import setup

setup(name='ModelicaEngine',
      version='0.1',
      description= 'OpenModelica interact code',
      author= 'Xingning SA',
      author_email= 'ssyxs3@nottingham.edu.cn',
      license='UNNC',
      url='https://github.com/XingningSA/OpenModelica_engine_py.git',
      packages=['ModelicaEngine'],
      install_requires=['scipy', 'pandas', 'modelica-builder']
)  
