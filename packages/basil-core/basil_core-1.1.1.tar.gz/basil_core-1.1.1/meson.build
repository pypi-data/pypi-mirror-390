project('basil_core',
    'c',
    version: '1.1.1',
    default_options: ['warning_level=2', 'optimization=3', 'c_std=c99'],
    meson_version: '>=0.64.0',
)

py = import('python').find_installation(pure: false)
numpy_dep = dependency('numpy')

# Include directories
inc_dirs = [
    'src/basil_core/array_tools',
    'src/basil_core/astro',
    'src/basil_core/astro/coordinates',
    'src/basil_core/astro/orbit',
    'src/basil_core/stats',
    'src/basil_core/c_utils',
]

incdir = include_directories(inc_dirs)

# Install Python package
subdir('src/basil_core')
