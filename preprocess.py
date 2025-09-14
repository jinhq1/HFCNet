## Example: A simple example to obtain distsance map and boundary map
import numpy as np
import os
import cv2
from osgeo import gdal
import scipy.ndimage as sn
import scipy.spatial

def bicenter_weighted(matrix):
    row_weights = np.ones((matrix.shape[0], 1))
    col_weights = np.ones((1, matrix.shape[1]))
    row_weights /= row_weights.sum()
    col_weights /= col_weights.sum()
    row_mean = np.sum(matrix * row_weights, axis=0)
    col_mean = np.sum(matrix * col_weights, axis=1)
    col_mean -= np.sum(row_mean * col_weights)
    result = matrix - row_mean
    result -= col_mean.reshape(-1, 1)
    return result

def quasi_euclidean(distance_matrix):
    num_cols = distance_matrix.shape[1]
    delta = -0.5 * bicenter_weighted(distance_matrix * distance_matrix)
    eigenvalues, eigenvectors = np.linalg.eigh(delta)
    num_components = np.count_nonzero(eigenvalues > 0)
    new_table = eigenvectors[:,-num_components:] * np.tile(np.sqrt(eigenvalues[-num_components:]), (num_cols, 1))
    result = scipy.spatial.distance_matrix(new_table, new_table)
    return result





def read_img(filename):
    dataset=gdal.Open(filename)

    im_width = dataset.RasterXSize
    im_height = dataset.RasterYSize

    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()
    im_data = dataset.ReadAsArray(0,0,im_width,im_height)

    del dataset
    return im_proj, im_geotrans, im_width, im_height, im_data


def write_img(filename, im_proj, im_geotrans, im_data):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1,im_data.shape

    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

    dataset.SetGeoTransform(im_geotrans)
    dataset.SetProjection(im_proj)

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i+1).WriteArray(im_data[i])

    del dataset



maskRoot = r"E:\PycharmProgram\SEANet_torch-main\SEANet_torch-main\test\mask"
# boundaryRoot = r"E:\Datasets\test\boun"
distRoot = r"E:\PycharmProgram\SEANet_torch-main\SEANet_torch-main\test\dist_contour"

for imgPath in os.listdir(maskRoot):
    input_path = os.path.join(maskRoot, imgPath)
    # boundaryOutPath = os.path.join(boundaryRoot, imgPath)
    distOutPath = os.path.join(distRoot, imgPath)
    im_proj, im_geotrans, im_width, im_height, im_data = read_img(input_path)
    result = cv2.distanceTransform(src=im_data, distanceType=cv2.DIST_L2, maskSize=3)
    min_value = np.min(result)
    max_value = np.max(result)
    scaled_image = ((result - min_value) / (max_value - min_value)) * 255
    result = scaled_image.astype(np.uint8)
    write_img(distOutPath, im_proj, im_geotrans, result)


    # boundary = cv2.Canny(im_data, 100, 200)     
    # write_img(boundaryOutPath, im_proj, im_geotrans, boundary)

    # boundary = cv2.Canny(im_data, 50, 200)
    # kernel = np.ones((3, 3), np.uint8)
    # boundary = cv2.dilate(boundary, kernel, iterations=1)
    # write_img(boundaryOutPath, im_proj, im_geotrans, boundary)





