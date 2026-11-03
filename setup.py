# =====================================================
# RC-0 / CapyTown - Grupo 7, seccion S-003
# Equipo responsable del repositorio:
# Sebastian Pedro Aguirre Acosta - Integracion
# Anahi Cortez Chinchay - Control
# Karen Noelia Ramirez Quevedo - Percepcion
# Valentino Uziel Vara Vargas - Planificacion
# Firma de documentacion; se respeta la autoria previa.
# =====================================================
"""Registro del paquete Python y de sus archivos de arranque en ROS 2."""

from glob import glob
import os

from setuptools import find_packages, setup


PACKAGE_NAME = 'capytown_esan'

setup(
    name=PACKAGE_NAME,
    version='0.1.0',
    packages=find_packages(exclude=('tests',)),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + PACKAGE_NAME]),
        ('share/' + PACKAGE_NAME, ['package.xml']),
        (os.path.join('share', PACKAGE_NAME, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', PACKAGE_NAME, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='anahicz',
    maintainer_email='25101008@UE.EDU.PE',
    description='Herramientas de arranque para RC-0 del proyecto CapyTown.',
    license='TODO',
    entry_points={
        'console_scripts': [
            'odom_adapter = capytown_esan.odom_adapter:main',
        ],
    },
)
