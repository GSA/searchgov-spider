from pathlib import Path
import subprocess
import time

import pytest

from scrapyd_client import ScrapydClient


class TestScrapyd:
    def test_scrapyd_is_not_running(self):
        assert subprocess.getoutput("ps aux | grep scrapyd | grep -v pytest | grep -v grep") == ""

    def test_scrapyd_version(self, script_runner):
        result = script_runner.run(["scrapyd", "--version"])
        assert result.returncode == 0
        assert result.stdout == "Scrapyd 1.5.0\n"
        assert result.stderr == ""

    @pytest.fixture(scope="class", name="temp_egg_dir")
    def fixture_temp_egg_dir(self, tmp_path_factory):
        yield tmp_path_factory.mktemp("eggs")

    @pytest.fixture(scope="class", name="scrapyd_cwd")
    def fixture_scrapyd_cwd(self) -> Path:
        return Path(__file__).parent.parent.parent / "search_gov_crawler"

    @pytest.fixture(scope="class", name="scrapyd_process")
    def fixture_scrapyd_process(self, scrapyd_cwd):
        with subprocess.Popen(["scrapyd"], cwd=scrapyd_cwd) as scrapyd_process:
            time.sleep(1)
            yield scrapyd_process
            scrapyd_process.kill()
            Path(scrapyd_cwd / "twistd.pid").unlink(missing_ok=True)

    @pytest.fixture(scope="class", name="scrapyd_client")
    def fixture_scrapyd_client(self, scrapyd_process) -> ScrapydClient:  # pylint: disable=unused-argument
        return ScrapydClient()

    def test_scrapyd_list_projects(self, scrapyd_client):
        assert scrapyd_client.projects() == ["search_gov_spiders", "default"]

    def test_scrapyd_list_spiders(self, scrapyd_client):
        assert scrapyd_client.spiders(project="search_gov_spiders") == ["domain_spider", "domain_spider_js"]

    @pytest.fixture(scope="class", name="temp_egg_file")
    def fixture_temp_egg_file(self, temp_egg_dir):
        yield str(temp_egg_dir / "integration_testing.egg")

    @pytest.mark.usefixtures("scrapyd_process")
    def test_scrapyd_deploy_build_egg(self, script_runner, scrapyd_cwd, temp_egg_file):
        result = script_runner.run(
            ["scrapyd-deploy", "local", "--build-egg", temp_egg_file],
            cwd=scrapyd_cwd,
        )
        assert result.returncode == 0
        assert result.stderr == f"Writing egg to {temp_egg_file}\n"
