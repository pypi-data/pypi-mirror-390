import numpy as np

__all__ = [
    'polygon_area',
    'polygon_signed_area',
    'calculate_polygon_centroid',
]

def polygon_area(vertices):
    """
    Measure the area of a polygon's vertices.

    Parameters
    ----------
    vertices : `~numpy.ndarray`
        Vertices of the polygon.
    
    Returns
    -------
    area : `~float`
        Area of the polygon.

    """

    # Check that vertices is an array of points shaped (Nx2)
    if (not isinstance(vertices, np.ndarray) or vertices.shape[-1] != 2):
        raise ValueError(f'Invalid shape: {vertices.shape}. '
                         + 'Last dimension has to be 2: (..., 2).')

    x = vertices[:, 0]
    y = vertices[:, 1]

    x_next = np.roll(x, -1)
    y_next = np.roll(y, -1)
    area = 0.5 * abs(np.sum(x * y_next - x_next * y))

    return area


def polygon_signed_area(vertices):
    """
    Compute the signed area of a polygon.

    Positive area indicates counterclockwise vertex order,
    negative area indicates clockwise order.

    Parameters
    ----------
    vertices : `~numpy.ndarray` of shape (N, 2)
        Vertices of the polygon.
    
    Returns
    -------
    signed_area : `~float`
        Signed area of the polygon.

    """

    # Check that vertices is an array of points shaped (Nx2)
    if (not isinstance(vertices, np.ndarray) or vertices.shape[-1] != 2):
        raise ValueError(f'Invalid shape: {vertices.shape}. '
                         + 'Last dimension has to be 2: (..., 2).')

    x = vertices[:, 0]
    y = vertices[:, 1]
    x_next = np.roll(x, -1)
    y_next = np.roll(y, -1)
    signed_area = 0.5 * np.sum(x * y_next - y * x_next)
    
    return signed_area


def calculate_polygon_centroid(vertices):
    """
    Return the centroid of a polygon.

    Parameters
    ----------
    vertices : `~numpy.ndarray`
        Vertices of the polygon.
    
    Returns
    -------
    centroid : `~numpy.ndarray`
        Centroid of the polygon.

    """

    # Check that vertices is an array of points shaped (Nx2)
    if (not isinstance(vertices, np.ndarray) or vertices.shape[-1] != 2):
        raise ValueError(f'Invalid shape: {vertices.shape}. '
                         + 'Last dimension has to be 2: (..., 2).')

    x = vertices[:, 0]
    y = vertices[:, 1]
    signed_area = polygon_signed_area(vertices)

    # Prevent division by zero
    if np.isclose(signed_area, 0):
        raise ValueError("The polygon's area is zero; cannot determine centroid.")
    
    x_next = np.roll(x, -1)
    y_next = np.roll(y, -1)
    factor = (x * y_next - y * x_next )
    centroid_x = np.sum((x + x_next) * factor) / (6 * signed_area)
    centroid_y = np.sum((y + y_next) * factor) / (6 * signed_area)
    centroid = np.array([centroid_x, centroid_y])

    return centroid
