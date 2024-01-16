# This file has the definition of the Camera class

import cv2
import matplotlib.pyplot as plt
import numpy as np
import utils
import pickle

class Camera:
    def __init__(self,name):
        self.name = name
        self.camera_matrix = None
        self.distortion_coefficients = None
        self.calibration_rotation_vectors = None
        self.calibration_translation_vectors = None
        self.new_camera_matrix = None
        self.roi = None
        self.rotation_matrix = None
        self.translation_vectors = None

    def calibrate(self, pixel_coordinates, world_coordinates, imgpath):
        """
        Calibrate the camera using pixel and world coordinates
        :param pixel_coordinates: Pixel coordinates of the calibration points in the format [[x1,y1],[x2,y2],...]
        :type: List of lists
        :param world_coordinates: World coordinates of the calibration points in the format [[x1,y1,z1],[x2,y2,z2],...]
        :type: List of lists
        :param imgpath: Path to the image used for calibration
        :type: String
        :return: None
        """
        image = cv2.imread(imgpath)
        # Convert the pixel coordinates to the format required by cv2.calibrateCamera
        pixel_coordinates_temp = []
        pixel_coordinates_temp.append(pixel_coordinates)
        world_coordinates_temp=[]
        world_coordinates_temp.append(world_coordinates)
        # Calibrate the camera
        ret, self.camera_matrix, self.distortion_coefficients, self.calibration_rotation_vectors, self.calibration_translation_vectors = cv2.calibrateCamera(world_coordinates_temp,pixel_coordinates_temp, (image.shape[1], image.shape[0]), None, None)
        # Project through the camera matrix to get the pixel coordinates of the calibration points
        for i in range(len(world_coordinates_temp)):
            imgpoints2, _ = cv2.projectPoints(world_coordinates_temp[i], self.calibration_rotation_vectors[i], self.calibration_translation_vectors[i], self.camera_matrix, self.distortion_coefficients)
        # Save the camera object as a pickle file
        pickle.dump(self, open(f'{imgpath[:-4]}_camera_object.pkl', 'wb'))
        utils.display_image_with_points(image, imgpoints2[:,0,:])


    def undistort(self, imgpath, points):
        """
        Undistort the image using the camera matrix and distortion coefficients
        :param imgpath: Path to the image to be undistorted
        :type: String
        :param points: Pixel coordinates of the points to be undistorted in the format [[x1,y1],[x2,y2],...]
        :type: List of lists
        :return: None
        """
        img = cv2.imread(imgpath)
        self.new_camera_matrix, self.roi = cv2.getOptimalNewCameraMatrix(self.camera_matrix, self.distortion_coefficients, (img.shape[1], img.shape[0]), 1, (img.shape[1], img.shape[0]))
        undistorted_img = cv2.undistort(img, self.camera_matrix, self.distortion_coefficients, None, self.new_camera_matrix)
        undistorted_img = cv2.cvtColor(undistorted_img, cv2.COLOR_BGR2RGB)
        plt.savefig(f'{imgpath[:-4]}_undistorted.png')
        undistorted_img_points = cv2.undistortPoints(points, self.camera_matrix, self.distortion_coefficients, None, self.new_camera_matrix)
        np.savetxt(f'{imgpath[:-4]}_undistorted_image_points.txt', undistorted_img_points[:,0,:])
        # Save the camera object as a pickle file
        pickle.dump(self, open(f'{imgpath[:-4]}_camera_object.pkl', 'wb'))
        utils.display_image_with_points(undistorted_img, undistorted_img_points[:,0,:])

    def set_rotation_and_translation_vectors(self, world_points, image_points):
        """
        Returns the rotation and translation vectors for the given world and image points.
        :param world_points: The world points.
        :type world_points: numpy array of shape (N, 3)
        :param image_points: The image points.
        :type image_points: numpy array of shape (N, 2)
        :param camera_matrix: The camera matrix.
        :type camera_matrix: numpy array of shape (3, 3)
        :return: None
        """
        _, rvec, tvec = cv2.solvePnP(world_points, image_points, self.new_camera_matrix, None)
        # Since rvec is a rotation vector, we need to convert it to a rotation matrix.
        self.rotation_matrix, _ = cv2.Rodrigues(rvec)
        self.translation_vectors = tvec
   
    


        
        


