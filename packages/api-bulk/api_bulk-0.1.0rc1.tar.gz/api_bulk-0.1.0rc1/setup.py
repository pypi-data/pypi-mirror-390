from setuptools import setup, find_packages

setup(
    author= "Norathee Lert",
    description="different api bulk tools",
    name="api_bulk",
    version="0.1.0rc1",
    packages=find_packages(),
    license="MIT",
    install_requires=["pandas",
        "os_toolkit>=0.1.1",
        "py_string_tool>=0.1.3",
        "python_wizard>=0.1.1",
        "play_audio_file>=0.1.0"

                      ],

    # example
    # install_requires=['pandas>=1.0',
    # 'scipy==1.1',
    # 'matplotlib>=2.2.1,<3'],
    

)