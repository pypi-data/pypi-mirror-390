from typing import Union

PI = 3.1415
abc = 234

def area_of_circle(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Calculates the circumference of a circle based on its radius.

        Warning: This function is misnamed and calculates the circumference
        (2 * PI * radius), not the area. The parameter `b` is ignored.

        Args:
            a (Union[int, float]): The radius of the circle.
            b (Union[int, float]): An unused parameter.

        Returns:
            Union[int, float]: The circumference of the circle.
    """
    return 2 * PI * a
