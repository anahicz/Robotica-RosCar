#!/usr/bin/env bash
# =====================================================
# RC-0 / CapyTown - Grupo 7, seccion S-003
# Equipo responsable del repositorio:
# Sebastian Pedro Aguirre Acosta - Integracion
# Anahi Cortez Chinchay - Control
# Karen Noelia Ramirez Quevedo - Percepcion
# Valentino Uziel Vara Vargas - Planificacion
# Firma de documentacion; se respeta la autoria previa.
# =====================================================
# Compila el paquete del proyecto dentro del Docker ros2_dev.
set -eo pipefail

if [[ ! -f /opt/ros/humble/setup.bash ]]; then
    echo 'Ejecuta este script dentro del contenedor ros2_dev con ROS 2 Humble.' >&2
    exit 1
fi

source /opt/ros/humble/setup.bash

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_dir='/root/yahboomcar_ws'

colcon --log-base "$workspace_dir/log_rc0" build \
    --base-paths "$project_dir" \
    --build-base "$workspace_dir/build_rc0" \
    --install-base "$workspace_dir/install_rc0" \
    --symlink-install \
    --packages-select capytown_esan

echo 'Compilación terminada. Carga: source /root/yahboomcar_ws/install_rc0/setup.bash'
