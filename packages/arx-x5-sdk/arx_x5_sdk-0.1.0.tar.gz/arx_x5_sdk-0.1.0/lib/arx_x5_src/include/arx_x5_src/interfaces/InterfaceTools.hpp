#pragma once

#include <mutex>
#include <vector>
#include <iostream>
#include <memory>

#include <Eigen/Dense>
#include <Eigen/Geometry> // Include transformation and pose processing

namespace arx::x5
{
    class InterfacesTools
    {
    public:
        InterfacesTools(int flag);
        ~InterfacesTools();
        std::vector<double> ForwardKinematicsRpy(std::vector<double> joint_pos);

    private:
        class impl;
        std::unique_ptr<impl> pimpl;
    };
}
