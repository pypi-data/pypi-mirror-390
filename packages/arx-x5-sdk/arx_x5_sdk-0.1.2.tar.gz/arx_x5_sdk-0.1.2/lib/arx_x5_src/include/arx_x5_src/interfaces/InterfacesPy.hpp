#pragma once

#include "arx_x5_src/interfaces/InterfacesThread.hpp"

namespace arx::x5
{
    class InterfacesPy
    {
    public:
        InterfacesPy(const std::string& urdf_path, const std::string &name, int type);
        ~InterfacesPy();

        bool get_joint_names(); // useless
        bool go_home();
        bool gravity_compensation();

        bool set_arm_status(int state);

        bool set_joint_positions(std::vector<double> pos); // useless
        bool set_joint_velocities();                       // useless
        bool set_ee_pose(std::vector<double> pose);

        bool set_catch(double pos);

        /// @brief Get joint positions
        /// @return 7-dimensional vector
        std::vector<double> get_joint_positions();

        /// @brief Get joint velocities
        /// @return 7-dimensional vector
        std::vector<double> get_joint_velocities();

        /// @brief Get joint currents
        /// @return 7-dimensional vector
        std::vector<double> get_joint_currents();

        /// @brief Get end effector pose
        /// @return 7-dimensional vector composed of 3D vector + quaternion
        std::vector<double> get_ee_pose();

        /// @brief Get end effector pose xyzrpy
        /// @return 6-dimensional vector composed of xyzrpy
        std::vector<double> get_ee_pose_xyzrpy();
        void arx_x(double arx1, double arx2, double arx3);

    private:
        class impl;
        std::unique_ptr<impl> pimpl;
    };
}

namespace arx::solve
{
    Eigen::Isometry3d Xyzrpy2Isometry(double input[6]);
    std::vector<double> Isometry2Xyzrpy(Eigen::Isometry3d pose);
}
