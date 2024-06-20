from unittest import TestCase, mock

from . import mock_requests
from . import test_path
import bojrecsys

class DataManagerTest(TestCase):

    @mock.patch('bojrecsys.pipeline.data_downloader.requests', mock_requests)
    def test_data_manager(self):
        kwargs = {
            'raw_path': test_path.RAW_PATH,
            'preproc_path': test_path.PREPROC_PATH,
            'model_path': test_path.MODEL_PATH,
        }
        loader, dumper, checker = bojrecsys.Loader(**kwargs), bojrecsys.Dumper(**kwargs), bojrecsys.Checker(**kwargs)
        downloader = bojrecsys.DataDownloader(call_sleep_sec=0.1)
        manager = bojrecsys.DataManager(downloader=downloader, loader=loader, dumper=dumper, checker=checker)
        manager.download_problem_info(problem_ids=list(range(1000, 10000)))
        manager.download_user_info()
        manager.download_top_100_problems()
