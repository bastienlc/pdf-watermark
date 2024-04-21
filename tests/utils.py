import numpy as np
from pdf2image import convert_from_path


def assert_pdfs_are_close(path_1: str, path_2: str, epsilon: float = 1e-10):
    """This function checks that two PDFs are close enough. We chose to convert the PDFs to images and then compare their L1 norms, because other techniques (hashing for instance) might break easily."""
    images_1 = convert_from_path(path_1)
    images_2 = convert_from_path(path_2)

    for im1, im2 in zip(images_1, images_2):
        assert np.sum(np.abs(np.array(im1) - np.array(im2))) < epsilon
