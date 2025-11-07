"""
Computer Vision Tasks Module
Contains all 9 tasks with implementations
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_sample_images


# Task 1: Image Handling and Processing
def image_operations(image_path=None):
    """Task 1: Perform basic image operations: resize, rotate, flip, blur"""
    if image_path is None:
        from skimage import data
        img = data.astronaut()
    else:
        img = cv2.imread(image_path)
    
    if img is None:
        print("Error loading image")
        return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    resized = cv2.resize(img, (256, 256))
    rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    flipped = cv2.flip(img, 1)
    blurred = cv2.GaussianBlur(img, (15, 15), 0)
    
    cv2.imwrite("resized.jpg", resized)
    cv2.imwrite("rotated.jpg", rotated)
    cv2.imwrite("flipped.jpg", flipped)
    cv2.imwrite("blurred.jpg", blurred)
    
    print("Task 1 - Image Operations:")
    print("Saved: resized.jpg, rotated.jpg, flipped.jpg, blurred.jpg")
    return img, resized, rotated, flipped, blurred


# Task 2: Geometric Transformations
def geometric_transforms(image_path=None):
    """Task 2: Apply geometric transformations: translation, rotation, scaling, shearing"""
    if image_path is None:
        from skimage import data
        img = data.astronaut()
    else:
        img = cv2.imread(image_path)
    
    h, w = img.shape[:2]
    
    M_translate = np.float32([[1, 0, 50], [0, 1, 25]])
    translated = cv2.warpAffine(img, M_translate, (w, h))
    
    center = (w // 2, h // 2)
    M_rotate = cv2.getRotationMatrix2D(center, 30, 1.0)
    rotated = cv2.warpAffine(img, M_rotate, (w, h))
    
    M_scale = cv2.getRotationMatrix2D(center, 0, 0.7)
    scaled = cv2.warpAffine(img, M_scale, (w, h))
    
    pts1 = np.float32([[0, 0], [w, 0], [0, h]])
    pts2 = np.float32([[0, 0], [w*0.8, h*0.2], [w*0.2, h*0.9]])
    M_shear = cv2.getAffineTransform(pts1, pts2)
    sheared = cv2.warpAffine(img, M_shear, (w, h))
    
    cv2.imwrite("translated.jpg", translated)
    cv2.imwrite("rotated_geo.jpg", rotated)
    cv2.imwrite("scaled.jpg", scaled)
    cv2.imwrite("sheared.jpg", sheared)
    
    print("Task 2 - Geometric Transformations:")
    print("Saved: translated.jpg, rotated_geo.jpg, scaled.jpg, sheared.jpg")
    return translated, rotated, scaled, sheared


# Task 3: Homography Matrix
def compute_homography(image_path=None):
    """Task 3: Compute homography matrix between two point sets"""
    if image_path is None:
        from skimage import data
        img = data.astronaut()
    else:
        img = cv2.imread(image_path)
    
    h, w = img.shape[:2]
    src = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    dst = np.array([[0, 0], [w*0.9, h*0.1], [w*0.8, h], [h*0.1, h*0.9]], dtype=np.float32)
    
    M = cv2.getPerspectiveTransform(src, dst)
    print("Task 3 - Homography Matrix:")
    print(M)
    
    np.save("homography_matrix.npy", M)
    print("Saved: homography_matrix.npy")
    return M


# Task 4: Perspective Transformation
def perspective_transform(image_path=None):
    """Task 4: Apply perspective transformation to an image"""
    if image_path is None:
        from skimage import data
        img = data.astronaut()
    else:
        img = cv2.imread(image_path)
    
    h, w = img.shape[:2]
    
    pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    pts2 = np.float32([[0, h*0.33], [w*0.9, 0], [w*0.1, h], [w, h*0.67]])
    
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(img, matrix, (w, h))
    
    cv2.imwrite("perspective_transform.jpg", result)
    print("Task 4 - Perspective Transformation:")
    print("Saved: perspective_transform.jpg")
    return result


# Task 5: Camera Calibration
def camera_calibration():
    """Task 5: Demonstrate camera calibration with barrel distortion"""
    def create_grid_image(size=400):
        img = np.ones((size, size), dtype=np.uint8) * 255
        for i in range(0, size, 40):
            cv2.line(img, (i, 0), (i, size), 0, 1)
            cv2.line(img, (0, i), (size, i), 0, 1)
        cv2.putText(img, "Grid Pattern", (120, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
        return img
    
    def apply_barrel_distortion(img, k1=0.3, k2=0.1):
        h, w = img.shape[:2]
        mtx = np.array([[w/2, 0, w/2], [0, w/2, h/2], [0, 0, 1]], dtype=np.float32)
        dist_coeffs = np.array([k1, k2, 0, 0], dtype=np.float32)
        distorted = cv2.undistort(img, mtx, dist_coeffs)
        return distorted, mtx, dist_coeffs
    
    h, w = 400, 400
    img = create_grid_image(400)
    distorted, mtx, dist = apply_barrel_distortion(img, k1=0.3, k2=0.1)
    
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    undistorted = cv2.undistort(distorted, mtx, dist, None, newcameramtx)
    
    print("Task 5 - Camera Calibration:")
    print("Camera Matrix:\n", mtx)
    print("Distortion Coefficients:\n", dist)
    
    cv2.imwrite("distorted.jpg", distorted)
    cv2.imwrite("undistorted.jpg", undistorted)
    print("Saved: distorted.jpg, undistorted.jpg")
    
    return distorted, undistorted


# Task 6: Fundamental Matrix
def fundamental_matrix():
    """Task 6: Compute fundamental matrix from stereo image pair"""
    def draw_epipolar_lines(img1, img2, lines, pts1, pts2):
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        img1_color = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
        img2_color = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
        r, c = img1.shape[:2]
        
        for rline, pt1, pt2 in zip(lines, pts1, pts2):
            color = tuple(np.random.randint(0, 255, 3).tolist())
            x0, y0 = map(int, [0, -rline[2] / rline[1]])
            x1, y1 = map(int, [c, -(rline[2] + rline[0] * c) / rline[1]])
            cv2.line(img2_color, (x0, y0), (x1, y1), color, 1)
            cv2.circle(img1_color, tuple(pt1), 5, color, -1)
            cv2.circle(img2_color, tuple(pt2), 5, color, -1)
        
        return img1_color, img2_color
    
    sample_images = load_sample_images()
    images = sample_images.images
    img1, img2 = images[0], images[1]
    
    if img1.dtype != np.uint8:
        img1 = (img1 * 255).astype(np.uint8)
    if img2.dtype != np.uint8:
        img2 = (img2 * 255).astype(np.uint8)
    
    img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2BGR)
    img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2BGR)
    
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)
    
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    
    good = []
    pts1, pts2 = [], []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
            pts1.append(kp1[m.queryIdx].pt)
            pts2.append(kp2[m.trainIdx].pt)
    
    if len(good) < 8:
        print("Task 6 - Fundamental Matrix: Not enough matches")
        return None
    
    pts1, pts2 = np.int32(pts1), np.int32(pts2)
    F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC)
    
    print("Task 6 - Fundamental Matrix:")
    print(F)
    np.save("fund_matrix.npy", F)
    print("Saved: fund_matrix.npy")
    return F


# Task 7: Edge, Line, Corner Detection
def edge_line_corner_detection():
    """Task 7: Detect edges (Canny), lines (Hough), corners (Harris, Shi-Tomasi)"""
    sample_images = load_sample_images()
    images = sample_images.images
    img = images[0]
    
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)
    
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    edges = cv2.Canny(gray, 50, 150)
    cv2.imwrite("edges.jpg", edges)
    
    lines_img = img.copy()
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(lines_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.imwrite("lines.jpg", lines_img)
    
    gray_f = np.float32(gray)
    harris = cv2.cornerHarris(gray_f, 2, 3, 0.04)
    harris = cv2.dilate(harris, None)
    harris_img = img.copy()
    harris_img[harris > 0.01 * harris.max()] = [0, 255, 0]
    cv2.imwrite("harris_corners.jpg", harris_img)
    
    shi_img = img.copy()
    corners = cv2.goodFeaturesToTrack(gray, maxCorners=200, qualityLevel=0.01, minDistance=10)
    if corners is not None:
        corners = np.int32(corners)
        for c in corners:
            x, y = c.ravel()
            cv2.circle(shi_img, (x, y), 4, (255, 0, 0), -1)
    cv2.imwrite("shi_tomasi_corners.jpg", shi_img)
    
    print("Task 7 - Edge, Line, Corner Detection:")
    print("Saved: edges.jpg, lines.jpg, harris_corners.jpg, shi_tomasi_corners.jpg")


# Task 8: SIFT Feature Detection
def sift_features():
    """Task 8: Detect SIFT keypoints and compute descriptors"""
    sample_images = load_sample_images()
    images = sample_images.images
    img = images[0]
    
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)
    
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    
    print("Task 8 - SIFT Features:")
    print("Keypoints detected:", len(keypoints))
    print("Descriptor shape:", descriptors.shape)
    
    img_keypoints = cv2.drawKeypoints(img, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imwrite("sift_keypoints.jpg", img_keypoints)
    np.save("sift_descriptors.npy", descriptors)
    print("Saved: sift_keypoints.jpg, sift_descriptors.npy")
    
    return keypoints, descriptors


# Task 9: SIFT and HOG Descriptors
def sift_hog_descriptors():
    """Task 9: Compute SIFT keypoints and HOG descriptor"""
    def compute_hog(img):
        hog = cv2.HOGDescriptor()
        img_resized = cv2.resize(img, (64, 128))
        return hog.compute(img_resized)
    
    sample_images = load_sample_images()
    images = sample_images.images
    img = images[0]
    
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)
    
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    sift = cv2.SIFT_create()
    kp, des = sift.detectAndCompute(gray, None)
    
    print("Task 9 - SIFT and HOG Descriptors:")
    print("SIFT Keypoints:", len(kp))
    
    img_kp = cv2.drawKeypoints(img, kp, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imwrite("sift_keypoints_final.jpg", img_kp)
    
    if des is not None:
        np.save("sift_descriptors_final.npy", des)
    
    hog = compute_hog(gray)
    np.save("hog_descriptor.npy", hog)
    print("HOG Descriptor shape:", hog.shape)
    print("Saved: sift_keypoints_final.jpg, sift_descriptors_final.npy, hog_descriptor.npy")
    
    return kp, des, hog
