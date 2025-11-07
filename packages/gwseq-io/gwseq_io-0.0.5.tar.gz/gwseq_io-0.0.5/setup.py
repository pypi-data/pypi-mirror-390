from glob import glob
from pybind11 import get_include
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup


ext_modules = [
    Pybind11Extension(
        "gwseq_io",
        sources=[
            "gwseq_io/binding.cpp",
        ],
        include_dirs=[
            "gwseq_io/",
            get_include(),
        ],
        libraries=["curl", "z"],
        language="c++",
        cxx_std=17,
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    data_files=[(
        "gwseq_io",
            glob("gwseq_io/**/*.c", recursive=True) +
            glob("gwseq_io/**/*.h", recursive=True) +
            glob("gwseq_io/**/*.cpp", recursive=True) +
            glob("gwseq_io/**/*.hpp", recursive=True)
        )
    ],
)
