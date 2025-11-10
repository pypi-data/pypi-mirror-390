from __future__ import annotations
from typing import Dict, Tuple
import numpy as np

try:
    import SimpleITK as sitk  # type: ignore
    _HAS_SITK = True
except Exception:
    _HAS_SITK = False


def _np_to_sitk(vol: np.ndarray, spacing: Tuple[float, float, float]) -> "sitk.Image":
    img = sitk.GetImageFromArray(vol.astype(np.float32), isVector=False)
    img.SetSpacing(tuple(float(s) for s in spacing))
    # Use identity direction and zero origin; we operate in RAS canonical space
    img.SetDirection((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0))
    img.SetOrigin((0.0, 0.0, 0.0))
    return img


def rigid_register_to_reference(moving: np.ndarray,
                                moving_spacing: Tuple[float, float, float],
                                reference: np.ndarray,
                                reference_spacing: Tuple[float, float, float]) -> Tuple[np.ndarray, Dict[str, float]]:
    """Rigid 3D registration (VersorRigid3D) of moving to reference; resample into reference grid.

    Returns registered volume and a dict of transform parameters.
    """
    if not _HAS_SITK:
        raise RuntimeError("SimpleITK is required for registration but is not installed.")

    fixed = _np_to_sitk(reference, reference_spacing)
    moving_img = _np_to_sitk(moving, moving_spacing)

    # Initialize transform at centers
    initial_tx = sitk.CenteredTransformInitializer(
        fixed, moving_img, sitk.VersorRigid3DTransform(), sitk.CenteredTransformInitializerFilter.GEOMETRY
    )

    R = sitk.ImageRegistrationMethod()
    R.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    R.SetMetricSamplingStrategy(R.RANDOM)
    R.SetMetricSamplingPercentage(0.2)
    R.SetInterpolator(sitk.sitkLinear)
    R.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, convergenceMinimumValue=1e-6, convergenceWindowSize=10)
    R.SetOptimizerScalesFromPhysicalShift()
    R.SetShrinkFactorsPerLevel([4, 2, 1])
    R.SetSmoothingSigmasPerLevel([2, 1, 0])
    R.SetInitialTransform(initial_tx, inPlace=False)

    final_tx = R.Execute(fixed, moving_img)

    # Resample moving into fixed grid
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetTransform(final_tx)
    moved = resampler.Execute(moving_img)

    moved_np = sitk.GetArrayFromImage(moved).astype(np.float32)

    # Extract parameters
    m = final_tx.GetMatrix()
    t = final_tx.GetTranslation()
    tx = {
        "tx": float(t[0]),
        "ty": float(t[1]),
        "tz": float(t[2]),
        "m00": float(m[0]), "m01": float(m[1]), "m02": float(m[2]),
        "m10": float(m[3]), "m11": float(m[4]), "m12": float(m[5]),
        "m20": float(m[6]), "m21": float(m[7]), "m22": float(m[8]),
    }
    return moved_np, tx

