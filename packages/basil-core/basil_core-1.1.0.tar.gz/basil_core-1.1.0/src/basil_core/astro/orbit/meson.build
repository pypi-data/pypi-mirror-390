# basil_core.astro.orbit
py.install_sources([
    '__init__.py',
    'decay.py',
    'ecc_root_finder.py',
    'orbit.py',
], subdir: 'basil_core/astro/orbit')

py.extension_module('_decay',
    sources: ['_decay.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/astro/orbit',
    install: true,
)
py.extension_module('_kepler',
    sources: ['_kepler.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/astro/orbit',
    install: true,
)
py.extension_module('_DWD_RLOF',
    sources: ['_DWD_RLOF.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/astro/orbit',
    install: true,
)
py.extension_module('_GW',
    sources: ['_GW.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/astro/orbit',
    install: true,
)
