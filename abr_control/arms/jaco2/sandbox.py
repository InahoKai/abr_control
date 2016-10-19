import numpy as np

import abr_control

# initialize our robot config for neural controllers
robot_config = abr_control.arms.jaco2.config.robot_config()
# instantiate the REACH controller for the ur5 robot
ctrlr = abr_control.controllers.osc_robust.controller(robot_config)
# create our VREP interface for the ur5
interface = abr_control.interfaces.vrep.interface(robot_config)
interface.connect()

# create a target
target_xyz = [0, 0, 0]
#target_state = np.hstack([target_xyz, np.zeros(3)])

# set up lists for tracking data
q_path = []
dq_path = []
ee_path = []
target_path = []

# set seed so we can repeat the target set for
# various experiment conditions
np.random.seed(3)

for ii in range(3):
    np.random.random()

try:
    num_targets = 0
    while num_targets < 30:
        # get arm feedback from VREP
        feedback = interface.get_feedback()
        hand_xyz = robot_config.T('EE', feedback['q'])
        # generate a control signal
        u = ctrlr.control(
            q=feedback['q'],
            dq=feedback['dq'],
            target_state=np.hstack([target_xyz, np.zeros(3)]))

        # apply the control signal, step the sim forward
        print('error: ', np.sqrt(np.sum((target_xyz - hand_xyz)**2)))
        interface.apply_u(u)

        # randomly change target location once hand is within
        # 5mm of the target
        if (num_targets == 0 or
            np.sqrt(np.sum((target_xyz - hand_xyz)**2)) < .005):
            target_xyz = [np.random.random() - .5,
                          np.random.random() - .5,
                          np.random.random() * .2 + .6]
            # update the position of the target sphere in VREP
            interface.set_target(target_xyz)
            num_targets += 1
            print('Reaching to target %i' % num_targets)

        # track data
        q_path.append(np.copy(feedback['q']))
        dq_path.append(np.copy(feedback['dq']))
        ee_path.append(np.copy(hand_xyz))
        target_path.append(np.copy(target_xyz))

    # num_targets = 0
    # while num_targets < 30:
    #     # get arm feedback from VREP
    #     feedback = interface.get_feedback()
    #     # generate a control signal
    #     u = ctrlr.control(q=feedback['q'],
    #                     dq=feedback['dq'],
    #                     target_xyz=target_xyz)
    #     hand_xyz = robot_config.T('EE', feedback['q'])
    #     # apply the control signal, step the sim forward
    #     print('error: ', np.sqrt(np.sum((target_xyz - hand_xyz)**2)))
    #     interface.apply_u(u)
    #
    #     # randomly change target location once hand is within
    #     # 5mm of the target
    #     if (num_targets == 0 or
    #         np.sqrt(np.sum((target_xyz - hand_xyz)**2)) < .005):
    #         target_xyz = [np.random.random() - .5,
    #                       np.random.random() - .5,
    #                       np.random.random() * .2 + .6]
    #         # update the position of the target sphere in VREP
    #         interface.set_target(target_xyz)
    #         num_targets += 1
    #         print('Reaching to target %i' % num_targets)
    #
    #     # track data
    #     q_path.append(np.copy(feedback['q']))
    #     dq_path.append(np.copy(feedback['dq']))
    #     ee_path.append(np.copy(hand_xyz))
    #     target_path.append(np.copy(target_xyz))


finally:
    # stop and reset the VREP simulation
    interface.disconnect()
    # generate a 3D plot of the trajectory taken
    abr_control.utils.plotting.plot_trajectory(
        ee_path=ee_path,
        target_path=target_path)

    import matplotlib.pyplot as plt
    plt.plot(np.sqrt(np.sum((np.array(target_path) -
                             np.array(ee_path))**2, axis=1)))
    plt.ylabel('Error (m)')
    plt.xlabel('Time (ms)')
    plt.show()
