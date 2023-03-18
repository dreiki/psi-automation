import os

def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        print("The file does not exist")

def test_print():
    print("testing")