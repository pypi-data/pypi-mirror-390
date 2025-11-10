from pydra.compose import shell
import typing as ty
from pathlib import Path
from fileformats.generic import File, Directory
from fileformats.medimage import MghGz


def subject_dir_path(subjects_dir: Path):
    return Path(subjects_dir) / "FS_outputs"


def norm_img_path(subjects_dir: Path):
    return Path(subjects_dir) / "FS_outputs" / "mri" / "norm.mgz"


def aparcaseg_img_path(subjects_dir: Path):
    return Path(subjects_dir) / "FS_outputs" / "mri" / "aparc+aseg.mgz"


def brainmask_img_path(subjects_dir: Path):
    return Path(subjects_dir) / "FS_outputs" / "mri" / "brainmask.mgz"


@shell.define
class Fastsurfer(shell.Task["Fastsurfer.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pydra.tasks.fastsurfer.v2_2 import Fastsurfer

    """

    executable = "run_fastsurfer.sh"

    # Input arguments
    subjects_dir: Path = shell.arg(
        argstr="--sd {subjects_dir}",
        help="Subjects directory",
    )

    subject_id: ty.Any = shell.arg(
        argstr="--sid {subject_id}",
        help="Subject ID",
    )

    T1_files: File | None = shell.arg(
        argstr="--t1 {T1_files}",
        help="T1 full head input (not bias corrected, global path)",
        default=None,
    )

    fs_license: File = shell.arg(
        argstr="--fs_license {fs_license}",
        help="Path to FreeSurfer license key file.",
    )

    seg: File | None = shell.arg(
        argstr="--seg {seg}",
        help="Pre-computed segmentation file",
        default=None,
    )

    weights_sag: File | None = shell.arg(
        argstr="--weights_sag {weights_sag}",
        help="Pretrained weights of sagittal network",
        default=None,
    )

    weights_ax: File | None = shell.arg(
        argstr="--weights_ax {weights_ax}",
        help="Pretrained weights of axial network",
        default=None,
    )

    weights_cor: File | None = shell.arg(
        argstr="--weights_cor {weights_cor}",
        help="Pretrained weights of coronal network",
        default=None,
    )

    seg_log: File | None = shell.arg(
        argstr="--seg_log {seg_log}",
        help="Name and location for the log-file for the segmentation (FastSurferCNN).",
        default=None,
    )

    clean_seg: bool = shell.arg(
        argstr="--clean_seg",
        help="Flag to clean up FastSurferCNN segmentation",
        default=False,
    )

    run_viewagg_on: File | None = shell.arg(
        argstr="--run_viewagg_on {run_viewagg_on}",
        help="Define where the view aggregation should be run on.",
        default=None,
    )

    no_cuda: bool = shell.arg(
        argstr="--no_cuda",
        help="Flag to disable CUDA usage in FastSurferCNN (no GPU usage, inference on CPU)",
        default=False,
    )

    batch: int = shell.arg(
        argstr="--batch {batch}",
        help="Batch size for inference. default=16. Lower this to reduce memory requirement",
        default=16,
    )

    fstess: bool = shell.arg(
        argstr="--fstess",
        help="Use mri_tesselate instead of marching cube (default) for surface creation",
        default=False,
    )

    fsqsphere: bool = shell.arg(
        argstr="--fsqsphere",
        help="Use FreeSurfer default instead of novel spectral spherical projection for qsphere",
        default=False,
    )

    fsaparc: bool = shell.arg(
        argstr="--fsaparc",
        help="Use FS aparc segmentations in addition to DL prediction",
        default=False,
    )

    no_surfreg: bool = shell.arg(
        argstr="--no_surfreg",
        help="Skip creating Surface-Atlas (sphere.reg) registration with FreeSurfer\n        (for cross-subject correspondence or other mappings)",
        default=False,
    )

    parallel: bool = shell.arg(
        argstr="--parallel",
        help="Run both hemispheres in parallel",
        default=True,
    )

    threads: int = shell.arg(
        argstr="--threads {threads}",
        help="Set openMP and ITK threads to",
        default=4,
    )

    py: ty.Any = shell.arg(
        argstr="--py {py}",
        help="which python version to use. default=python3.6",
        default="python3.8",
    )

    seg_only: bool = shell.arg(
        argstr="--seg_only",
        help="only run FastSurferCNN (generate segmentation, do not surface)",
        default=False,
    )

    surf_only: bool = shell.arg(
        argstr="--surf_only",
        help="only run the surface pipeline recon_surf.",
        default=False,
    )

    allow_root: bool = shell.arg(
        argstr="--allow_root",
        help="allow running as root user",
        default=False,
    )

    class Outputs(shell.Outputs):
        subjects_dir: Directory = shell.outarg(
            argstr="--sd {subjects_dir}",
            help="Subjects directory",
            path_template="{subjects_dir}",
        )

        subjects_dir_output: Directory = shell.out(
            help="path to subject FS outputs",
            callable=subject_dir_path,
        )

        norm_img: MghGz = shell.out(
            help="norm image",
            callable=norm_img_path,
        )

        aparcaseg_img: MghGz = shell.out(
            help="aparc+aseg image",
            callable=aparcaseg_img_path,
        )

        brainmask_img: MghGz = shell.out(
            help="brainmask.mgz image",
            callable=brainmask_img_path,
        )
