Permissions and roles
=====================

Summary
----------

The available roles are:

- (Django super admin)
- PlatformAdmin 
- RegulatorAdmin
- RegulatorUser
- OperatorAdmin
- OperatorUser
- ObserverUser
- ObserverAdmin


Permissions 
--------------------

(Django super admin)
~~~~~~~~~~~~~~~~~~~~

The first PlatformAdmin user must be created with the Django command:

.. code-block:: bash

    $ python manage.py createsuperuser

PlatformAdmin 
~~~~~~~~~~~~~~

The PlatformAdmin can create, modify and delete
- other PlatformAdmin users (in the "Users" screen)
- Regulations
- Competent Authorities (also internally known as "Regulators")
- Observers and associated users and admins
He also can configure the ``Site`` section of the Django application.

RegulatorAdmin
~~~~~~~~~~~~~~~~
The RegulatorAdmin can create other RegulatorAdmin, or RegulatorUser for his entity. 
The RegulatorAdmin has also the responsibility to define the different incident notification workflows. 

ObserverAdmin
~~~~~~~~~~~~~~~~
The ObserverAdmin can create other ObserverAdmin, or ObserverUser for his entity. 


RegulatorUser
~~~~~~~~~~~~~~~~
The RegulatorUser can create regulated entities and create an OperatorAdmin who is the administrator of the company (operator)

OperatorAdmin
~~~~~~~~~~~~~~~~

OperatorAdmin creates OperatorUser for his company. 

OperatorUser and ObserverUser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

They have no administration role. 


