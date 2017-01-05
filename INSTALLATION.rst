To install qcodes from the repository: 
======================================

0. Download and install git and anaconda for python 3.5. 

1. First clone the repository. Go to github, click the "clone or download" button and coppy the IP address.

2. Open the git command line. Use the "cd" command to navigate to the place you want to download the repo.

.. code:: bash

    git clone https://github.com/nicholgroup/Qcodes.git 

3. Open the ‘navigator’ app that was installed with anaconda.

4. On the left side click on “Environments”.

5. Then on the “import” icon, on the bottom.

6. Pick a name, and click on the folder icon next to file to import from.

7. Make sure you select “Pip requirement files” from the “Files of type” dialog then navigate to the qcodes folder (QCODES_INSTALL_DIR) and select basic_requirements.txt.

6. Finally click import, and wait until done.

7. The enviroment is now created, click on the green arrow to open a terminal inside it.

8. Navigate again with the terminal (or drag and drop the the folder on OsX)

9. Open a python terminal. To install matplotlib and pyqtgraph, type

.. code:: bash

	conda install matplotlib
	conda install pyqtgraph

10. You may need to update setuptools. Download the python file ez_setup.py. In the terminal, navigate to the directory. The run

.. code:: bash

	python ez_setup.py install

11. Navigate back to the repository directory, and install all of the packages with 

.. code:: bash

	pip install -e . 

It may ask you to install visual c++ install tools, which you should.