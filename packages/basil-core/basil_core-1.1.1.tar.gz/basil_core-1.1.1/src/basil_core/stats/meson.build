# basil_core.stats
py.install_sources([
    '__init__.py',
    'distance.py',
    'hypercube.py',
    'random.py',
    'schechter.py',
], subdir: 'basil_core/stats')

py.extension_module('_distance',
    sources: ['_distance.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/stats',
    install: true,
)
py.extension_module('_relative_entropy',
    sources: ['_relative_entropy.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/stats',
    install: true,
)
py.extension_module('_schechter',
    sources: ['_schechter.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/stats',
    install: true,
)
subdir('density')
