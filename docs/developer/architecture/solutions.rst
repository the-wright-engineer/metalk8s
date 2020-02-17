Solutions
=========

Context
-------

As for now, if we want to deploy applications on a MetalK8s cluster,
it's achievable by applying manifest through ``kubectl apply -f manifest.yaml``
or using helm with charts.

These approaches work, but for an offline environment, the user must first
pre-populate the MetalK8s registry with the container images listed in these
manifests/charts.
Moreover, there is no control on what's deployed, so it is difficult to
enforce certain practices or provide tooling to ease deployment or
lifecycle management of these applications.

To solve this, MetalK8s introduces the concept of Solutions.

What is a Solution ?

It's a packaged Kubernetes application, archived as an ISO disk image,
containing:

* A set of OCI images to inject in MetalK8s image registry
* An Operator to deploy on the cluster
* A UI for managing and monitoring the application

Requirements
------------

* Everything must work offline.
* Solutions must still be available after a reboot.
* Check archives integrity and validity.
* Deploy Solutions (operator & UI manifests).
* Handle multiple Solutions with different versions.
* Guidelines for Solutions developers.
* Robustness against invalid format.

User Stories
------------

Solution import
~~~~~~~~~~~~~~~

As a cluster admin, I want to be able to import a Solution archive using a CLI
tool, to make the Solution available for deployment.

Environment creation/deletion/inspection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a cluster admin, I want to be able to create/delete/inspect an Environment
using the CLI.

Solution deployment
~~~~~~~~~~~~~~~~~~~

As a solution admin, I want to be able to deploy a Solution through its
UI, without any specific knowledge about Kubernetes.

Solution upgrade/downgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~

As a solution admin, I want to be able to easily upgrade or downgrade a
Solution using its UI without any specific knowledge about Kubernetes.

Solution deletion
~~~~~~~~~~~~~~~~~

.. todo:: Open question:
          do we want the user to be able to delete its solution ?
          no ?
          yes, but with some safety nest ?
          Only with a tool from the CLI ?
          If not, do we want to at least document the manual procedure ?

Solution development
~~~~~~~~~~~~~~~~~~~~

As a developer, I want to have guidelines to follow to develop a Solution.

Solution packaging
~~~~~~~~~~~~~~~~~~

As a developer, I want to have documentation to know how to package a Solution.

Solution validation
~~~~~~~~~~~~~~~~~~~

As a developer, I want to be able to know that a packaged Solution
follows the requirements and is valid using a CLI tool.

Design Choices
--------------

Solution configuration
~~~~~~~~~~~~~~~~~~~~~~

We will use a ``SolutionsConfiguration`` object, stored in
``/etc/metalk8s/solutions.yaml``, to declare which Solutions are available
to the cluster, from the bootstrap node.

Here is how it will look::

    apiVersion: metalk8s.scality.com/v1alpha1
    kind: SolutionsConfiguration
    solutions:
      - /solutions/storage_1.0.0.iso
      - /solutions/storage_latest.iso
      - /other_solutions/computing.iso

There is no explicit information about what an archive contains.
Instead, we want the archive itself to contain such information and to
discover it at import time.

This configuration file will be read by a Salt external pillar module,
which will permit the consumption of it by Salt modules and states.

Archive format
~~~~~~~~~~~~~~

Solution archives must use the `ISO-9660:1988`_ format, including `Rock Ridge`_
and Joliet_ directory records. The character encoding must be UTF-8_. The
conformance level is expected to be at most 3, meaning:

- Directory identifiers may not exceed 31 characters (bytes) in length
- File name + ``'.'`` + file name extension may not exceed 30 characters
  (bytes) in length
- Files are allowed to consist of multiple sections

The generated archive should specify a volume ID, set to
``{project_name} {version}``.

.. _`ISO-9660:1988`: https://www.iso.org/obp/ui/#iso:std:iso:9660:ed-1:v1:en
.. _`Rock Ridge`: https://en.wikipedia.org/wiki/Rock_Ridge
.. _Joliet: https://en.wikipedia.org/wiki/Joliet_(file_system)
.. _UTF-8: https://tools.ietf.org/html/rfc3629

OCI Images registry
~~~~~~~~~~~~~~~~~~~

Every container images from Solution archive will be exposed as a single
repository through MetalK8s registry. The name of this repository will be
computed from the product information ``<NAME>-<VERSION>``.

Solution environment
~~~~~~~~~~~~~~~~~~~~

Solutions will be deployed into an ``Environment``, which is basically a
namespace or a group of namespaces with a specific label
``solutions.metalk8s.scality.com/environment``. It allows to run multiple
instances of a Solution, with different versions, on the same cluster, without
collision between them.

Solution management
~~~~~~~~~~~~~~~~~~~

We will provide CLI and UI to import, unimport and handle the whole lifecycle
of a Solution. These tools are wrapper around Salt formulas.

Interaction diagram
~~~~~~~~~~~~~~~~~~~

We include a detailed interaction sequence diagram for describing how MetalK8s
will handle user input when deploying / upgrading Solutions.

.. uml:: solutions.uml

Rejected design choices
~~~~~~~~~~~~~~~~~~~~~~~

Solutions vs CNAB
~~~~~~~~~~~~~~~~~

The Cloud Native Application Bundle (CNAB_) is a standard packaging format
for multi-component distributed applications. It basically offers what MetalK8s
Solution does, but with the need of an extra container with almost full access
to the Kubernetes cluster and that’s the reason why we did choose to not use
it.

We also want to enforce some practices (Operator, UI, ...) in Solutions
and this is not easily doable using it.

Moreover, CNAB_ is a pretty young project and has not yet been adopted by a
lot of people, so it's hard to predict its future.

.. _CNAB: https://cnab.io

Implementation Details
----------------------

.. todo:: Try to details more / see if there is missing stuff.

Iteration 1
~~~~~~~~~~~

* Solution example.
* Tooling to import/unimport Solution (simple shell script).
* Salt formulas to manage Solution (deployment and lifecycle).
* MetalK8s UI to manage Solution.
* Solution automated tests (deployment, upgrade/downgrade, deletion, ...).

Iteration 2
~~~~~~~~~~~

* MetalK8s CLI to manage Solutions (supersedes import script & wraps Salt
  call).
* Integration into monitoring tools (Grafana dashboards, Alerting, ...).
* Integration with the identity provider (Dex).
* Tooling to validate integrity & validity of Solution ISO
  (checksum, layout, valid manifests, ...).

Documentation
-------------

In the Operational Guide:

* Document how to import a Solution.
* Document how to deploy a Solution.
* Document how to upgrade/downgrade a Solution.
* Document how to delete a Solution.

In the Developer Guide:

* Document how to monitor a Solution (ServiceMonitor, Service, ...).
* Document how to build a Solution (layout, how to package, ...).

Test Plan
---------

First of all, we must develop a Solution example to be able to tests the whole
feature.

Then, we need to develop automated tests to ensure feature is working as
expected. The tests will have to cover the following points:

* Solution installation and lifecycle (upgrade/downgrade).
* Solution can be plugged to MetalK8s cluster services
  (monitoring, alerting, ...).
* Solution can be managed through its UI.
