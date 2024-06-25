from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, OpaqueFunction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.conditions import UnlessCondition, IfCondition

# Define the noisy_controller function
def noisy_controller(context, *args, **kwargs):
    # Retrieving launch configurations
    use_python = LaunchConfiguration("use_python")
    wheel_radius = float(LaunchConfiguration("wheel_radius").perform(context))
    wheel_separation = float(LaunchConfiguration("wheel_separation").perform(context))
    wheel_radius_error = float(LaunchConfiguration("wheel_radius_error").perform(context))
    wheel_separation_error = float(LaunchConfiguration("wheel_separation_error").perform(context))

    # Node definitions for Python and C++ versions
    noisy_controller_py = Node(
        package="robitcubebot_controller",
        executable="noisy_controller.py",
        parameters=[
            {"wheel_radius": wheel_radius + wheel_radius_error,
             "wheel_separation": wheel_separation + wheel_separation_error}],
        condition=IfCondition(use_python),
    )

    noisy_controller_cpp = Node(
        package="robitcubebot_controller",
        executable="noisy_controller",
        parameters=[
            {"wheel_radius": wheel_radius + wheel_radius_error,
             "wheel_separation": wheel_separation + wheel_separation_error}],
        condition=UnlessCondition(use_python),
    )

    return [
        noisy_controller_py,
        noisy_controller_cpp,
    ]

# Define the launch description
def generate_launch_description():
    # Declare launch arguments
    use_simple_controller_arg = DeclareLaunchArgument(
        "use_simple_controller",
        default_value="True",
        description="Whether to use the simple controller.",
    )
    use_python_arg = DeclareLaunchArgument(
        "use_python",
        default_value="True",
        description="Whether to use the Python version of the controllers.",
    )
    wheel_radius_arg = DeclareLaunchArgument(
        "wheel_radius",
        default_value="0.0325",
        description="Radius of the wheels.",
    )
    wheel_separation_arg = DeclareLaunchArgument(
        "wheel_separation",
        default_value="0.212",
        description="Distance between the wheels.",
    )
    wheel_radius_error_arg = DeclareLaunchArgument(
        "wheel_radius_error",
        default_value="0.005",
        description="Error margin for wheel radius.",
    )
    wheel_separation_error_arg = DeclareLaunchArgument(
        "wheel_separation_error",
        default_value="0.02",
        description="Error margin for wheel separation.",
    )
    
    # Define launch configurations
    use_simple_controller = LaunchConfiguration("use_simple_controller")
    use_python = LaunchConfiguration("use_python")
    wheel_radius = LaunchConfiguration("wheel_radius")
    wheel_separation = LaunchConfiguration("wheel_separation")

    # Define nodes
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    wheel_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "robitcubebot_controller",  # Add package name here
            "--controller-manager",
            "/controller_manager",
        ],
        condition=UnlessCondition(use_simple_controller),
    )

    simple_controller = GroupAction(
        condition=IfCondition(use_simple_controller),
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "simple_velocity_controller",
                    "--controller-manager",
                    "/controller_manager"
                ]
            ),
            Node(
                package="robitcubebot_controller",
                executable="simple_controller.py",
                parameters=[
                    {"wheel_radius": wheel_radius,
                     "wheel_separation": wheel_separation}],
                condition=IfCondition(use_python),
            ),
            Node(
                package="robitcubebot_controller",
                executable="simple_controller",
                parameters=[
                    {"wheel_radius": wheel_radius,
                     "wheel_separation": wheel_separation}],
                condition=UnlessCondition(use_python),
            ),
        ]
    )

    noisy_controller_launch = OpaqueFunction(function=noisy_controller)

    # Return the launch description
    return LaunchDescription(
        [
            use_simple_controller_arg,
            use_python_arg,
            wheel_radius_arg,
            wheel_separation_arg,
            wheel_radius_error_arg,
            wheel_separation_error_arg,
            joint_state_broadcaster_spawner,
            wheel_controller_spawner,
            simple_controller,
            noisy_controller_launch,
        ]
    )