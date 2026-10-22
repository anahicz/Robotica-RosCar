"""Publica la odometría nativa del carro en /odom y su transformación en /tf.

La fuente sigue siendo /odom_raw. Este adaptador conserva la pose, las
velocidades, las covarianzas, los marcos y el tiempo del mensaje recibido.
No calcula correcciones de rueda ni combina mediciones de la IMU.
"""

import math

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from tf2_ros import TransformBroadcaster


class OdomAdapter(Node):
    """Conecta la salida del fabricante con los tópicos requeridos en RC-0."""

    def __init__(self):
        super().__init__('odom_adapter')
        self.declare_parameter('input_topic', '/odom_raw')
        self.declare_parameter('output_topic', '/odom')
        self.declare_parameter('publish_tf', True)

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        self._publish_tf = self.get_parameter('publish_tf').value

        # Comparar los nombres resueltos evita un bucle de republicación,
        # incluso si alguien aplica remapeos al lanzar el nodo.
        if self.resolve_topic_name(input_topic) == self.resolve_topic_name(output_topic):
            raise ValueError('input_topic y output_topic deben ser diferentes.')

        self._publisher = self.create_publisher(Odometry, output_topic, 10)
        self._tf_broadcaster = TransformBroadcaster(self) if self._publish_tf else None
        self._received_first_message = False

        # Best effort puede recibir sensores publicados como best effort o reliable.
        self._subscription = self.create_subscription(
            Odometry, input_topic, self._on_odometry, qos_profile_sensor_data
        )
        self.get_logger().info(
            f'Esperando {input_topic}; salida {output_topic}; TF={self._publish_tf}.'
        )

    def _on_odometry(self, message):
        """Reutiliza la medición y publica el mismo movimiento como TF."""
        parent_frame = message.header.frame_id
        child_frame = message.child_frame_id
        position = message.pose.pose.position
        orientation = message.pose.pose.orientation

        # TF necesita dos marcos distintos y una pose numérica válida.
        if not parent_frame or not child_frame or parent_frame == child_frame:
            self.get_logger().warning(
                'Odometría descartada: faltan marcos o ambos son iguales.',
                throttle_duration_sec=5.0,
            )
            return

        values = (
            position.x, position.y, position.z,
            orientation.x, orientation.y, orientation.z, orientation.w,
        )
        norm_squared = sum(value * value for value in values[3:])
        if not all(math.isfinite(value) for value in values) or abs(norm_squared - 1.0) > 0.01:
            self.get_logger().warning(
                'Odometría descartada: pose no finita o cuaternión no unitario.',
                throttle_duration_sec=5.0,
            )
            return

        self._publisher.publish(message)

        if self._tf_broadcaster is not None:
            transform = TransformStamped()
            transform.header = message.header
            transform.child_frame_id = child_frame
            transform.transform.translation.x = position.x
            transform.transform.translation.y = position.y
            transform.transform.translation.z = position.z
            transform.transform.rotation = orientation
            self._tf_broadcaster.sendTransform(transform)

        if not self._received_first_message:
            self.get_logger().info(
                f'Primera odometría recibida. Marcos: {parent_frame} -> {child_frame}.'
            )
            self._received_first_message = True


def main(args=None):
    """Inicializa ROS 2 y permite cerrar el nodo con Ctrl+C."""
    rclpy.init(args=args)
    node = None
    try:
        node = OdomAdapter()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
