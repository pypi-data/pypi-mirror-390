[![Upload Python Package](https://github.com/ankit48365/decoraid/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ankit48365/decoraid/actions/workflows/python-publish.yml)
![Latest Release](https://img.shields.io/badge/release-v0.0.21-blue)

decoraid stands for Decorator Aid :) -->

    pip install decoraid
    decoraid --example  or decoraid --help

sample usage: -->

wrap the decorator around the function you want to test, provide the name of the package and the path to the virtual environment

    from decoraid.cpdec import check_package
    
    venv_path = "C:/projects/git/xxxx/.venv/" 
    
    
    @check_package("pandas", venv_path)
    
    def test_pandas():
    
        print('test_cpdec')
    
    if __name__ == "__main__":
    
        test_pandas()

Versioning :

    0.0.1+ --> cpdec decorator added
    
    0.0.2+ --> trace decorator was added


