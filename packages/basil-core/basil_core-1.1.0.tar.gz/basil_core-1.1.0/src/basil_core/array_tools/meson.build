# basil_core.array_tools
py.install_sources([
    '__init__.py',
    'indexer.py',
], subdir: 'basil_core/array_tools')

py.extension_module('_indexer',
    sources: ['_indexer.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'basil_core/array_tools',
    install: true,
)
