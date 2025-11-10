import setuptools

def readme():
    try:
        with open('README.md', encoding='utf-8') as f:
            return f.read()
    except (IOError, FileNotFoundError):
        return 'XL-GUI - A community-maintained fork of PySimpleGUI'

setuptools.setup(
    name="xl-gui",
    version="4.60.5",
    author="XL1126",
    author_email="258233740@qq.com",
    description="A freely available version of PySimpleGUI 4.60.5, published for continued community use after official support ended",
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords="GUI UI tkinter simple easy beginner graphics",
    url="https://github.com/XL1126/XL-GUI",
    packages=['PySimpleGUI'], 
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7", 
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Topic :: Multimedia :: Graphics",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    entry_points={
        'gui_scripts': [
            'psgissue=PySimpleGUI.PySimpleGUI:main_open_github_issue',
            'psgmain=PySimpleGUI.PySimpleGUI:_main_entry_point',
            'psgupgrade=PySimpleGUI.PySimpleGUI:_upgrade_entry_point', 
            'psghelp=PySimpleGUI.PySimpleGUI:main_sdk_help',
            'psgver=PySimpleGUI.PySimpleGUI:main_get_debug_data',
            'psgsettings=PySimpleGUI.PySimpleGUI:main_global_pysimplegui_settings',
        ],
    },
)