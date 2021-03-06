.. spiper documentation master file, created by
   sphinx-quickstart on Mon Mar  9 23:15:33 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. check https://docs.python.org/2/_sources/

****************************************************************************************************************************
:mod:`spiper`: Utilities to make a pipeline, with singularity integration and caching ability 
****************************************************************************************************************************


.. _Contents

.. toctree::
   :maxdepth: 2
   :numbered:
   
   install/index.rst
   examples/index.rst
   lib/index.rst
   indexes.rst
   license.rst
   CHANGELOG.md

Overview
===================

Pipeline construction is a long-standing problem in bioinformatics. Writing pipelines
quickly in a portable, reproducible and human-readable pipeline is always a 
challenging task. To address these issues, I wrote :obj:`spiper` after reading
about many other pipeline management packages. The major features making :obj:`spiper`
different are

* **Distributed file monitoring instead of a global file index**   (compared to gnu-make, snakemake)
* **Importable and documentable pipelines since they are python functions** (similar to ruffus/luigi)
* **Hierarchical execution as inherited from python functions**
* **No support for job-scheduling at the moment** (contribution welcome!)
* :ref:`example-workflow-filesync`
* :ref:`example-remote-code`
* **Declaring pipeline/function-level dependency.**
* The :obj:`spiper` syntax is very close to WDL syntax. It should be possible to auto-generate 
WDL code and submit to a cromwell server.

Quickstart
=================

.. code-block:: bash

    ## install 0.0.5
    pip3 install spiper@https://github.com/shouldsee/spiper/tarball/0.0.5 --user

.. literalinclude:: examples/003_remote_bash.sh.log
  :language: bash




:Author: Feng Geng
:Email: shouldsee.gem@gmail.com

