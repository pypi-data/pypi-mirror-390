Installation
============

Prérequis
---------

* Python >= 3.8
* pip >= 21.0

Installation stable
-------------------

Installation via pip (recommandé) :

.. code-block:: bash

   pip install quantfinance

Installation depuis les sources
--------------------------------

Cloner le repository :

.. code-block:: bash

   git clone https://github.com/Mafoya1er/quantfinance.git
   cd quantfinance

Installation en mode éditable :

.. code-block:: bash

   pip install -e .

Installation avec dépendances optionnelles
-------------------------------------------

Pour l'analyse de données :

.. code-block:: bash

   pip install quantfinance[data]

Pour le développement :

.. code-block:: bash

   pip install quantfinance[dev]

Tout installer :

.. code-block:: bash

   pip install quantfinance[all]

Vérification de l'installation
-------------------------------

.. code-block:: python

   import quantfinance
   print(quantfinance.__version__)

   # Tester un import
   from quantfinance.pricing.options import BlackScholes
   print("Installation réussie!")

Configuration d'un environnement virtuel
-----------------------------------------

Avec venv (recommandé) :

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows

   pip install quantfinance

Avec conda :

.. code-block:: bash

   conda create -n quantfinance python=3.10
   conda activate quantfinance
   pip install quantfinance

Résolution de problèmes
------------------------

Erreur lors de l'installation de scipy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sur certains systèmes, scipy peut nécessiter des dépendances supplémentaires :

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt-get install python3-dev libopenblas-dev

   # macOS
   brew install openblas

   # Puis réessayer
   pip install quantfinance

Problèmes avec matplotlib
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt-get install python3-tk

   # macOS
   brew install tcl-tk

