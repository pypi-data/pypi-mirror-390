from conftest import pass_after_timeout
import pytest
from fileformats.generic import File
from pydra.tasks.fastsurfer.v2_2 import Fastsurfer


@pytest.mark.xfail
@pass_after_timeout(seconds=10)
def test_fastsurfer_1():
    task = Fastsurfer()
    task.inputs.subjects_dir = None
    task.inputs.subject_id = None
    task.inputs.T1_files = File.sample()
    task.inputs.fs_license = File.sample()
    task.inputs.seg = File.sample()
    task.inputs.weights_sag = File.sample()
    task.inputs.weights_ax = File.sample()
    task.inputs.weights_cor = File.sample()
    task.inputs.seg_log = File.sample()
    task.inputs.clean_seg = None
    task.inputs.run_viewagg_on = File.sample()
    task.inputs.no_cuda = None
    task.inputs.batch = None
    task.inputs.fstess = None
    task.inputs.fsqsphere = None
    task.inputs.fsaparc = None
    task.inputs.no_surfreg = None
    task.inputs.parallel = None
    task.inputs.threads = None
    task.inputs.py = None
    task.inputs.seg_only = None
    task.inputs.surf_only = None
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task()
    print("RESULT: ", res)
