# basil_core.astro.coordinates
py.install_sources([
    '__init__.py',
    'coordinates.py',
], subdir: 'basil_core/astro/coordinates')

py.extension_module('_coordinates',
    sources: ['_coordinates.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/astro/coordinates',
    install: true,
)
py.extension_module('_spin',
    sources: ['_spin.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/astro/coordinates',
    install: true,
)
py.extension_module('_tides',
    sources: ['_tides.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/astro/coordinates',
    install: true,
)
