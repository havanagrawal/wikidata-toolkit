import unittest
from .create_episodes import create_episodes
from .create_seasons import create_seasons
from click.testing import CliRunner
from unittest.mock import patch

class CreateEpisodeCliTests(unittest.TestCase):
    def test_create_episodes(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test_episodes.csv', 'w') as f:
                f.write('1,1,"Test Episode Name"')
            with patch('commands.create_episodes', return_value=None) as patched_create:
                result = runner.invoke(create_episodes, ['Q1', 'Q2', 'test_episodes.csv'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.exception, None)
        patched_create.assert_called_with('Q1', 'Q2', 'test_episodes.csv', False, False)


class CreateSeasonCliTests(unittest.TestCase):
    def test_create_seasons(self):
        runner = CliRunner()
        with patch('commands.create_seasons', return_value=None) as patched_create:
            result = runner.invoke(create_seasons, ['Q79784', '10'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.exception, None)
        patched_create.assert_called_with('Q79784', 10, False, False)

    def test_create_seasons_dry(self):
        runner = CliRunner()
        with patch('commands.create_seasons', return_value=None) as patched_create:
            result = runner.invoke(create_seasons, ['Q79784', '10', '--dry'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.exception, None)
        patched_create.assert_called_with('Q79784', 10, False, True)

    def test_create_seasons_quickstatements(self):
        runner = CliRunner()
        with patch('commands.create_seasons', return_value=None) as patched_create:
            result = runner.invoke(create_seasons, ['Q79784', '10', '--quickstatements'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.exception, None)
        patched_create.assert_called_with('Q79784', 10, True, False)
