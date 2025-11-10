# tests/test_plot_paths.py
from pathlib import Path
import tempfile
import os
import matplotlib.pyplot as plt
from bioseq import visualizer as v

def _make_fig():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3], [1,2,3])
    return fig

def test_save_absolute_path(tmp_path):
    fig = _make_fig()
    out = tmp_path / "abs_dir" / "abs.png"
    out.parent.mkdir(parents=True)
    got = v.save_plot(fig, str(out))
    assert Path(got).exists()
    plt.close(fig)

def test_save_tmpdir_path(tmp_path):
    fig = _make_fig()
    out_base = tmp_path / "plots_out"
    out_relative = str(out_base / "len.png")
    got = v.save_plot(fig, out_relative)
    assert Path(got).exists()
    assert str(out_base) in str(got)  # file went into the tmp base
    plt.close(fig)

def test_save_relative_component_goes_into_results(tmp_path, monkeypatch):
    # ensure controlled base is a temp dir via env var
    tmp_results = tmp_path / "results"
    monkeypatch.setenv("BIOSEQ_OUTPUT_DIR", str(tmp_results))
    fig = _make_fig()
    # pass path with dir component that is NOT 'results' (should be placed under BIOSEQ_OUTPUT_DIR)
    got = v.save_plot(fig, "example_summary_plots/rel.png")
    assert tmp_results.exists()
    assert (tmp_results / "example_summary_plots" / "rel.png").exists()
    plt.close(fig)

