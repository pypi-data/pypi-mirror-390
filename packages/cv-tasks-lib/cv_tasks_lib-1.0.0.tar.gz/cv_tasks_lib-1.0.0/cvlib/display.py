"""
cvlib - Computer Vision Library
Display exact source code of all 9 original tasks
"""


def show_task_1():
    """Display Task 1 code"""
    code = """#1 Image Handling and Processing


from skimage import data, io, color, transform, filters
import matplotlib.pyplot as plt

# 1. Load inbuilt image
img = data.astronaut()  # RGB image

# 2. Display original image
plt.imshow(img)
plt.title("Original Image")
plt.axis('off')
plt.show()

# 3. Resize image
# Note: resize returns float image in range [0, 1]
img_resized = transform.resize(img, (200, 200))

# 4. Convert to grayscale
# Note: rgb2gray returns float image in range [0, 1]
img_gray = color.rgb2gray(img)

# 5. Apply Gaussian filter
# Note: gaussian also returns a float image
img_blur = filters.gaussian(img, sigma=2, channel_axis=-1) # Explicitly handle color channels

# 6. Display processed images
plt.figure(figsize=(10,4))

plt.subplot(1,3,1)
plt.imshow(img_resized)
plt.title("Resized")
plt.axis('off')

plt.subplot(1,3,2)
plt.imshow(img_gray, cmap='gray')
plt.title("Grayscale")
plt.axis('off')

plt.subplot(1,3,3)
plt.imshow(img_blur)
plt.title("Blurred")
plt.axis('off')

plt.tight_layout() # Added for better spacing
plt.show()"""
    
    print("=" * 80)
    print("TASK 1: IMAGE HANDLING AND PROCESSING")
    print("=" * 80)
    print(code)
    print("\n")


def show_task_2():
    """Display Task 2 code"""
    code = """#2 Geometric Transformation 


from skimage import data, transform, io, color
import matplotlib.pyplot as plt
import numpy as np

# Load inbuilt image
img = data.astronaut()  # RGB image
img_gray = color.rgb2gray(img)  # Optional grayscale for some transformations

# 1. Translation
tform_translate = transform.AffineTransform(translation=(50, 30))
img_translated = transform.warp(img, tform_translate)

# 2. Rotation
tform_rotate = transform.AffineTransform(rotation=np.deg2rad(45))
img_rotated = transform.warp(img, tform_rotate)

# 3. Scaling
tform_scale = transform.AffineTransform(scale=(0.5, 0.5))
img_scaled = transform.warp(img, tform_scale)

# 4. Reflection (horizontal flip)
tform_reflect = transform.AffineTransform(scale=(-1, 1), translation=(img.shape[1], 0))
img_reflected = transform.warp(img, tform_reflect)

# 5. Shearing
tform_shear = transform.AffineTransform(shear=np.deg2rad(20))
img_sheared = transform.warp(img, tform_shear)

# Display results
plt.figure(figsize=(12, 8))

plt.subplot(2, 3, 1)
plt.imshow(img)
plt.title("Original")
plt.axis('off')

plt.subplot(2, 3, 2)
plt.imshow(img_translated)
plt.title("Translated")
plt.axis('off')

plt.subplot(2, 3, 3)
plt.imshow(img_rotated)
plt.title("Rotated")
plt.axis('off')

plt.subplot(2, 3, 4)
plt.imshow(img_scaled)
plt.title("Scaled")
plt.axis('off')

plt.subplot(2, 3, 5)
plt.imshow(img_reflected)
plt.title("Reflected")
plt.axis('off')

plt.subplot(2, 3, 6)
plt.imshow(img_sheared)
plt.title("Sheared")
plt.axis('off')

plt.tight_layout()
plt.show()"""
    
    print("=" * 80)
    print("TASK 2: GEOMETRIC TRANSFORMATION")
    print("=" * 80)
    print(code)
    print("\n")


def show_task_3():
    """Display Task 3 code"""
    code = """#3 Compute Homography Matrix 


import numpy as np
import matplotlib.pyplot as plt
from skimage import data, transform, color

# Load inbuilt image
img = data.astronaut()   # RGB image
img_gray = color.rgb2gray(img)

# Define four source points (corners of a region in the original image)
src = np.array([[50, 50], [200, 50], [50, 200], [200, 200]], dtype=np.float32)

# Define four destination points (new perspective)
dst = np.array([[10, 100], [220, 50], [80, 250], [250, 220]], dtype=np.float32)

# 1. Compute Homography (using skimage's ProjectiveTransform)
tform = transform.ProjectiveTransform()
tform.estimate(src, dst)

# 2. Apply perspective warp
img_warped = transform.warp(img, tform, output_shape=img.shape)

# Display original and warped images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(img)
plt.title("Original")
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(img_warped)
plt.title("Warped Image")
plt.axis('off')

plt.show()

# Print Homography Matrix
print("Homography Matrix:\\n", tform.params)"""
    
    print("=" * 80)
    print("TASK 3: COMPUTE HOMOGRAPHY MATRIX")
    print("=" * 80)
    print(code)
    print("\n")


def show_task_4():
    """Display Task 4 code"""
    code = """#4 Perspective Transformation 



import numpy as np
import matplotlib.pyplot as plt
from skimage import data, transform, color

# Load sample image
img = data.astronaut()  # RGB image

# Define four source points (corners of a region in original image)
src = np.array([[50, 50], [200, 50], [50, 200], [200, 200]], dtype=np.float32)

# Define four destination points (desired perspective)
dst = np.array([[10, 100], [220, 50], [80, 250], [250, 220]], dtype=np.float32)

# Compute perspective transformation (homography)
tform = transform.ProjectiveTransform()
tform.estimate(src, dst)

# Apply the perspective warp
img_warped = transform.warp(img, tform, output_shape=img.shape)

# Display original and transformed images
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(img)
plt.title("Original Image")
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(img_warped)
plt.title("Perspective Transformed Image")
plt.axis('off')

plt.show()

# Print the 3x3 Homography matrix
print("Perspective Transformation Matrix:\\n", tform.params)"""
    
    print("=" * 80)
    print("TASK 4: PERSPECTIVE TRANSFORMATION")
    print("=" * 80)
    print(code)
    print("\n")


def show_task_5():
    """Display Task 5 code"""
    code = """import cv2
import numpy as np
import matplotlib.pyplot as plt

def create_grid_image(size=400):
    img = np.ones((size, size), dtype=np.uint8) * 255
    for i in range(0, size, 40):
        cv2.line(img, (i, 0), (i, size), 0, 1)
        cv2.line(img, (0, i), (size, i), 0, 1)
    cv2.putText(img, "Grid Pattern", (120, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
    return img

def apply_barrel_distortion(img, k1=0.3, k2=0.1):
    h, w = img.shape[:2]
    
    mtx = np.array([
        [w/2, 0, w/2],
        [0, w/2, h/2],
        [0, 0, 1]
    ], dtype=np.float32)
    
    dist_coeffs = np.array([k1, k2, 0, 0], dtype=np.float32)
    
    distorted = cv2.undistort(img, mtx, dist_coeffs)
    return distorted, mtx, dist_coeffs

h, w = 400, 400
img = create_grid_image(400)

print("Original image shape:", img.shape)

distorted, mtx, dist = apply_barrel_distortion(img, k1=0.3, k2=0.1)

print("Camera Matrix:\\n", mtx)
print("Distortion Coefficients:\\n", dist)

newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
undistorted = cv2.undistort(distorted, mtx, dist, None, newcameramtx)

plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.imshow(img, cmap='gray')
plt.title("Original (No Distortion)")
plt.axis('off')

plt.subplot(1, 3, 2)
plt.imshow(distorted, cmap='gray')
plt.title("With Barrel Distortion (Curved)")
plt.axis('off')

plt.subplot(1, 3, 3)
plt.imshow(undistorted, cmap='gray')
plt.title("Undistorted (Corrected)")
plt.axis('off')

plt.tight_layout()
plt.savefig("camera_calibration_comparison.png", dpi=100, bbox_inches='tight')
plt.show()

print("Saved: camera_calibration_comparison.png")"""
    
    print("=" * 80)
    print("TASK 5: CAMERA CALIBRATION")
    print("=" * 80)
    print(code)
    print("\n")


def show_task_6():
    """Display Task 6 code"""
    code = """import cv2
import numpy as np
from sklearn.datasets import load_sample_images

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

def main():
    sample_images = load_sample_images()
    images = sample_images.images
    
    img1 = images[0]
    img2 = images[1]
    
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
    pts1 = []
    pts2 = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
            pts1.append(kp1[m.queryIdx].pt)
            pts2.append(kp2[m.trainIdx].pt)

    if len(good) < 8:
        print("Not enough matches. Found:", len(good))
        return

    pts1 = np.int32(pts1)
    pts2 = np.int32(pts2)

    F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC)
    print("Fundamental Matrix:\\n", F)

    pts1_in = pts1[mask.ravel() == 1]
    pts2_in = pts2[mask.ravel() == 1]

    lines1 = cv2.computeCorrespondEpilines(pts2_in.reshape(-1, 1, 2), 2, F)
    lines1 = lines1.reshape(-1, 3)

    img_epi1, img_epi2 = draw_epipolar_lines(img1, img2, lines1, pts1_in, pts2_in)

    cv2.imwrite("matches_v2.jpg", cv2.drawMatches(img1, kp1, img2, kp2, good, None, flags=2))
    cv2.imwrite("epilines_left_v2.jpg", img_epi1)
    cv2.imwrite("epilines_right_v2.jpg", img_epi2)
    np.save("fundamental_matrix_v2.npy", F)

    print("Saved: matches_v2.jpg, epilines_left_v2.jpg, epilines_right_v2.jpg, fundamental_matrix_v2.npy")

if __name__ == "__main__":
    main()"""
    
    print("=" * 80)
    print("TASK 6: COMPUTE FUNDAMENTAL MATRIX")
    print("=" * 80)
    print(code)
    print("\n")


def show_task_7():
    """Display Task 7 code"""
    code = """import cv2
import numpy as np
from sklearn.datasets import load_sample_images

def main():
    sample_images = load_sample_images()
    images = sample_images.images
    img = images[0]
    
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)
    
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)
    cv2.imwrite("edges_v2.jpg", edges)

    lines_img = img.copy()
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(lines_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.imwrite("lines_v2.jpg", lines_img)

    gray_f = np.float32(gray)
    harris = cv2.cornerHarris(gray_f, 2, 3, 0.04)
    harris = cv2.dilate(harris, None)
    harris_img = img.copy()
    harris_img[harris > 0.01 * harris.max()] = [0, 255, 0]
    cv2.imwrite("harris_corners_v2.jpg", harris_img)

    shi_img = img.copy()
    corners = cv2.goodFeaturesToTrack(gray, maxCorners=200, qualityLevel=0.01, minDistance=10)
    if corners is not None:
        corners = np.int32(corners)
        for c in corners:
            x, y = c.ravel()
            cv2.circle(shi_img, (x, y), 4, (255, 0, 0), -1)
    cv2.imwrite("shi_tomasi_corners_v2.jpg", shi_img)

    print("Saved: edges_v2.jpg, lines_v2.jpg, harris_corners_v2.jpg, shi_tomasi_corners_v2.jpg")

if __name__ == "__main__":
    main()"""
    
    print("=" * 80)
    print("TASK 7: EDGE, LINE, CORNER DETECTION")
    print("=" * 80)
    print(code)
    print("\n")


def show_task_8():
    """Display Task 8 code"""
    code = """import cv2
import numpy as np
from sklearn.datasets import load_sample_images

def main():
    sample_images = load_sample_images()
    images = sample_images.images
    img = images[0]
    
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)
    
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)

    print("Keypoints detected:", len(keypoints))
    if descriptors is not None:
        print("Descriptor shape:", descriptors.shape)

    img_keypoints = cv2.drawKeypoints(
        img, keypoints, None,
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )

    cv2.imwrite("sift_keypoints_v2.jpg", img_keypoints)
    np.save("sift_descriptors_v2.npy", descriptors)

    print("Saved: sift_keypoints_v2.jpg, sift_descriptors_v2.npy")

if __name__ == "__main__":
    main()"""
    
    print("=" * 80)
    print("TASK 8: SIFT FEATURE DETECTION")
    print("=" * 80)
    print(code)
    print("\n")


def show_task_9():
    """Display Task 9 code"""
    code = """import cv2
import numpy as np
from sklearn.datasets import load_sample_images

def compute_hog(img):
    hog = cv2.HOGDescriptor()
    img_resized = cv2.resize(img, (64, 128))
    return hog.compute(img_resized)

def main():
    sample_images = load_sample_images()
    images = sample_images.images
    img = images[0]
    
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)
    
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()
    kp, des = sift.detectAndCompute(gray, None)
    print("SIFT Keypoints:", len(kp))

    img_kp = cv2.drawKeypoints(img, kp, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imwrite("sift_keypoints_v2.jpg", img_kp)
    if des is not None:
        np.save("sift_descriptors_v2.npy", des)

    hog = compute_hog(gray)
    np.save("hog_descriptor_v2.npy", hog)
    print("HOG Descriptor shape:", hog.shape)
    print("Saved: sift_keypoints_v2.jpg, sift_descriptors_v2.npy, hog_descriptor_v2.npy")

if __name__ == "__main__":
    main()"""
    
    print("=" * 80)
    print("TASK 9: SIFT AND HOG DESCRIPTORS")
    print("=" * 80)
    print(code)
    print("\n")


def show_all():
    """Display all task codes"""
    show_task_1()
    show_task_2()
    show_task_3()
    show_task_4()
    show_task_5()
    show_task_6()
    show_task_7()
    show_task_8()
    show_task_9()
