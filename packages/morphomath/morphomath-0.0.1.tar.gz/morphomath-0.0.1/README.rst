.. rst syntax: https://deusyss.developpez.com/tutoriels/Python/SphinxDoc/
.. version conv: https://peps.python.org/pep-0440/
.. icons: https://specifications.freedesktop.org/icon-naming-spec/latest/ar01s04.html or https://www.pythonguis.com/faq/built-in-qicons-pyqt/

.. image:: https://img.shields.io/badge/License-GPL-green.svg
    :alt: [license GPL]
    :target: https://opensource.org/license/gpl-3-0

.. image:: https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue
    :alt: [versions]
    :target: https://framagit.org/robinechuca/morphomath/-/blob/main/run_tests.sh

.. image:: https://static.pepy.tech/badge/morphomath
    :alt: [downloads]
    :target: https://www.pepy.tech/projects/morphomath

.. image:: https://readthedocs.org/projects/morphomath/badge/?version=latest
    :alt: [documentation]
    :target: https://morphomath.readthedocs.io/latest/

Useful links:
`Binary Installers <https://pypi.org/project/morphomath>`_ |
`Source Repository <https://framagit.org/robinechuca/morphomath>`_ |
`Online Documentation <https://morphomath.readthedocs.io/stable>`_ |


Description
===========

This module enables efficient **morphological erosion and dilatation**.
It uses the **kernel subdivision** algorithm **implemented in C**, with **multithreading**.

.. image:: https://framagit.org/robinechuca/morphomath/-/raw/main/example.png
    :width: 400
    :alt: Example of kernel decomposition


Features
========

#. Works for any tensor dimension, 2d for images, 3d for videos...
#. The morphological structuring element decomposition logarithmically reduces temporal complexity.
#. Functions can be parallelized to take advantage of all the CPU threads, in exchange of higher edge effects.
#. Functions can be compiled dynamically in C to reduce side-effects and overhead, in exchange for a longer loading time.


Examples
========

.. code:: python

    import morphomath, cv2
    img = cv2.imread("image.png", cv2.IMREAD_GRAYSCALE)
    dilate = morphomath.Dilatation([[0, 1, 0], [0, 1, 0], [1, 1, 1]]).decomposed()
    print(dilate)
    cv2.imwrite("result.png", dilate(img))


Before

.. image:: https://framagit.org/robinechuca/morphomath/-/raw/main/image.png
    :alt: input

After

.. image:: https://framagit.org/robinechuca/morphomath/-/raw/main/result.png
    :alt: result
