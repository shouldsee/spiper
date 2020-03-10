.. _install-index:

******************************************************
Installation
******************************************************


Dependencies
====================================

This package is tested to be compatible with python3.5 and python3.7. Please create a github PR if you
want another version to be added. Python2 is not supported.

Essentail
--------------------------
  * Python 3.5 / Python 3.7
  * pip >= 18.1

Optional
---------------------------
  * singularity >= 3.5.3 to use :obj:`singular_pipe.shell.LoggedSingularityCommand`. 
  * `graphviz dot executable <https://www.graphviz.org/download/>`_  to use :obj:`singular_pipe.graph.plot_simple_graph`

Installation
==============================

Install with pip
------------------------------

Find the version you want to install. For example, to install version 0.0.3, use

.. code-block:: bash

	pip3 install singular_pipe@https://github.com/shouldsee/singular_pipe/tarball/0.0.3 --user