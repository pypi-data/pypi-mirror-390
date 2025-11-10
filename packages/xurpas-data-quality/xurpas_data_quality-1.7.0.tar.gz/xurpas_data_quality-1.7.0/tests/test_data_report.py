import pytest
import yaml
import os
import pandas as pd

import xurpas_data_quality

""" sample config data """

@pytest.fixture
def sample_df():
    data = {
        'column_1': [1, 2, 3],
        'column_2': ['A', 'B', 'C']
    }
    return pd.DataFrame(data)

@pytest.fixture
def config_file(tmp_path_factory):
    sample_config = {
        'report_name': "Config Quality Report",
        'file_path': "config_test_report.html",
        'minimal': False,
    }

    fn = tmp_path_factory.mktemp("data") / "config.yaml"
    with open(fn, 'w') as file:
        yaml.dump(sample_config,file)

@pytest.fixture
def config_file(tmpdir):
    sample_config = {
        'report_name': "Config Quality Report",
        'file_path': "config_test_report.html",
        'minimal': False,
    }
    config_path = os.path.join(tmpdir, 'empty.yaml')
    with open(config_path, 'w') as file:
        file.write("""
            colors:
            base_colors:
                - "#17A2B8"
                - "#28A745"
                - "#0D6EFD"
                - "#DC3545"
                - "#FFC107"

            report_name: "Data Quality Report"
            file_path: "report.html"
            minimal: True""")

    yield config_path

@pytest.fixture
def empty_config_file(tmpdir):
    # Create an empty YAML file
    empty_config_path = os.path.join(tmpdir, 'empty.yaml')
    with open(empty_config_path, 'w') as file:
        pass  # Empty file

    yield empty_config_path

    # Clean up: remove the temporary file
    os.remove(empty_config_path)

class TestConfigClass:
    def test_wrong_config_name(self,sample_df, capsys):
        report = xurpas_data_quality.DataReport(df=sample_df, config_file="confafadsfasf.yaml")
        captured = capsys.readouterr()
        assert "does not exist! continuing with generating report without it" in captured.out

    def test_empty_config_file(self, sample_df, capsys, empty_config_file):
        # Use the fixture to get the file path
        report = xurpas_data_quality.DataReport(df=sample_df, config_file=empty_config_file)
        captured = capsys.readouterr()
        assert "is empty! proceeding with report generation." in captured.out

    def test_config_file(self, sample_df, config_file):
        assert True