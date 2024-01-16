# import libraries
import matplotlib.pyplot as plt
import numpy as np
import cv2
import camera

def display_image_with_points(img, points):
    """
    Displays an image with points superimposed on it.

    :param image: the image
    :type :numpy array
    :param points: the list of points
    :type :list of lists [[x1, y1], [x2, y2], ...]
    """
    # plot the image and the points
    plt.figure(figsize=(20,20))
    N = len(points)
    colors = np.random.rand(N)
    plt.scatter(points[:, 0], points[:, 1], c=colors, s=100)
    plt.imshow(img)
    plt.show()


# function to do the interactive clicking and saving
def interactive_clicking_and_saving(image, image_points):
    """
    Displays an image and allows the user to click on it to save the points.

    :param image: the image
    :type :numpy array
    """
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    # define the mouse click event handler
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            image_points.append([x, y])
            cv2.circle(image, (x, y), 10, (0, 0, 255), -1)
            cv2.imshow("image", image)
    
    # display the image
    
    cv2.imshow("image", image)
    cv2.setMouseCallback("image", click_event)

    # Wait for the user to close the window 
    cv2.waitKey(0)

    cv2.destroyAllWindows()

    # return the points
    return np.array(image_points, dtype=np.float32).reshape(-1, 2)

def triangulate(camera1_coords, camera1, camera2_coords, camera2):
    """
    This function takes in two arrays of points from 2 different cameras and finds the original points
    : param camera1_coords: The (u,v) coordinates of the points in camera 1
    : type: numpy array of shape (m, 2)
    : param camera1: The camera object of camera 1
    : type: camera object (see camera.py)
    : param camera2_coords: The (u,v) coordinates of the points in camera 2
    : type: numpy array of shape (m, 2)
    : param camera2: The camera object of camera 2
    : type: camera object (see camera.py)
    : return: A numpy array of shape (m, 3) of the (x,y,z) coordinates of the original points
    """

    # Put the rotation and translation side by side and then multiply with camera matrix
    camera1_P = camera1.new_camera_matrix @ np.hstack((camera1.rotation_matrix,camera1.translation_vectors)) # shape (3, 4)
    camera2_P = camera2.new_camera_matrix @ np.hstack((camera2.rotation_matrix,camera2.translation_vectors)) # shape (3, 4)

    pt2d_CxPx2 = np.array([camera1_coords, camera2_coords]) # shape (m, 2, 2)
    P_Cx3x4 = np.array([camera1_P, camera2_P]) # shape (2, 3, 4)
    Nc, Np, _ = pt2d_CxPx2.shape

    # P0 - xP2
    x = P_Cx3x4[:,0,:][:,None,:] - np.einsum('ij,ik->ijk', pt2d_CxPx2[:,:,0], P_Cx3x4[:,2,:])
    # P1 - yP2
    y = P_Cx3x4[:,1,:][:,None,:] - np.einsum('ij,ik->ijk', pt2d_CxPx2[:,:,1], P_Cx3x4[:,2,:])

    Ab = np.concatenate([x, y])
    Ab = np.swapaxes(Ab, 0, 1)
    assert Ab.shape == (Np, Nc*2, 4)

    A = Ab[:,:,:3]
    b = - Ab[:,:,3]
    AtA = np.linalg.pinv(A)

    X = np.einsum('ijk,ik->ij', AtA, b)
    return X


def visualize_triangulated_points(triangulated_points, world_points):
    """
    Visualizes the triangulated points.
    :param triangulated_points: The triangulated points.
    :type triangulated_points: numpy array of shape (N, 3)
    :param world_points: The world points.
    :type world_points: numpy array of shape (N, 3)
    """
    plt.figure(figsize=(20,20),dpi=100)
    ax = plt.axes(projection='3d')
    X = np.array(triangulated_points)[:,0]
    Y = np.array(triangulated_points)[:,1]
    Z = np.array(triangulated_points)[:,2]
    max_range = np.array([X.max()-X.min(), Y.max()-Y.min(), Z.max()-Z.min()]).max() / 2.0

    mid_x = (X.max()+X.min()) * 0.5
    mid_y = (Y.max()+Y.min()) * 0.5
    mid_z = (Z.max()+Z.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    ax.scatter3D(world_points[:,0], world_points[:,1], world_points[:,2], c='g', label='World Points')
    ax.scatter3D(X, Y, Z, c='r', label='Triangulated Points')
    plt.legend()
    plt.show()