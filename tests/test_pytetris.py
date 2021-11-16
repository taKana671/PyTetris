import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import itertools
from collections import namedtuple
from pathlib import Path
from unittest import TestCase, main, mock

import numpy as np

from pytetris import (ImageFiles, SoundFiles, PyTetris, BLOCKSETS, Status, Score,
    Start, GameOver, GAMEOVER_LEFT, GAMEOVER_TOP, GAMEOVER_BOUND_TOP, Pause)


DummyBlock = namedtuple('DummyBlock', 'row, col')


class FilesSubClassTestCase(TestCase):
    """Tests for ImageFiles
    """

    def test_image_files(self):
        for image_file in ImageFiles:
            result = image_file.path
            expect = Path('images', image_file.value)
            self.assertEqual(result, expect)

    def test_sound_files(self):
        for sound_file in SoundFiles:
            result = sound_file.path
            expect = Path('sounds', sound_file.value)
            self.assertEqual(result, expect)


class PyTetrisAllBlocksClearTestCase(TestCase):
    """Tests for PyTetris.all_blocks_clear
    """

    @mock.patch('pytetris.PyTetris.create_screens')
    @mock.patch('pytetris.PyTetris.create_sounds')
    def test_all_blocks_clear(self, mock_create_sounds, mock_create_screen):
        """The all of the blocks in matrix and blocks must be deleted.
        """
        mock_block = mock.MagicMock()
        mock_kill = mock.MagicMock(return_value=None)
        mock_block.kill = mock_kill
        # matrix has 30 mock_blocks
        matrix = [[None for _ in range(5)] for _ in range(10)]
        for row in matrix:
            for i in range(len(row)):
                if i % 2 == 0:
                    row[i] = mock_block
        # blocks has 2 mock_blocks
        blocks = [None for _ in range(4)]
        for i in range(len(blocks)):
            if i % 2 == 0:
                blocks[i] = mock_block

        mock_block = mock.MagicMock()
        mock_block.kill.return_value = None
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'matrix', matrix), \
                mock.patch.object(tetris, 'blocks', blocks):
            tetris.all_blocks_clear()

        for row in itertools.chain((r for r in matrix), [blocks]):
            with self.subTest():
                self.assertTrue(all(cell is None for cell in row))

        self.assertEqual(mock_kill.call_count, 32)
        mock_create_screen.assert_called_once()
        mock_create_sounds.assert_called_once()


class PyTetrisGetBlocksetIndexTestCase(TestCase):
    """Tests for PyTetris.get_blockset_index
    """
    def test_get_blockset_index(self):
        """An index returned from get_blockset_index must be between 0 and 6.
        """
        with mock.patch('pytetris.PyTetris.create_screens'), \
                mock.patch('pytetris.PyTetris.create_sounds'):
            tetris = PyTetris(object())
            for _ in range(10):
                result = tetris.get_blockset_index()
                with self.subTest(result):
                    self.assertTrue(0 <= result <= len(BLOCKSETS) - 1)


@mock.patch('pytetris.PyTetris.create_screens')
@mock.patch('pytetris.PyTetris.create_sounds')
@mock.patch('pytetris.PyTetris.get_blockset_index')
@mock.patch('pytetris.Block')
class PyTetrisCreateBlockTestCase(TestCase):
    """Tests for PyTetris.create_block
    """

    def test_create_block_next_block_is_none(self, mock_block, mock_get_blockset_index,
                                             mock_create_sounds, mock_create_screens):
        """get_blockset_index must be called two times if next_blockset is None, and
           index must be set to 0.
        """
        mock_get_blockset_index.side_effect = [1, 2]
        mock_block.return_value = object()

        mock_next_block_display = mock.MagicMock()
        mock_set_image = mock.MagicMock()
        mock_next_block_display.set_images = mock_set_image

        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'next_blockset', None, create=True), \
                mock.patch.object(tetris, 'index', 3, create=True), \
                mock.patch.object(tetris, 'next_block_display', mock_next_block_display, create=True):
            tetris.create_block()
            self.assertEqual(tetris.index, 0)
            mock_set_image.assert_called_once_with(2)
        self.assertEqual(mock_get_blockset_index.call_count, 2)

    def test_create_block_next_block_is_not_none(self, mock_block, mock_get_blockset_index,
                                                 mock_create_sounds, mock_create_screens):
        """get_blockset_index must be called once if next_blockset is not None, and
           index must be set to 0.
        """
        mock_get_blockset_index.return_value = 1
        mock_block.return_value = object()

        mock_next_block_display = mock.MagicMock()
        mock_set_image = mock.MagicMock()
        mock_next_block_display.set_images = mock_set_image

        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'next_blockset', BLOCKSETS[0], create=True), \
                mock.patch.object(tetris, 'index', 3, create=True), \
                mock.patch.object(tetris, 'next_block_display', mock_next_block_display, create=True):
            tetris.create_block()
            self.assertEqual(tetris.index, 0)
            mock_set_image.assert_called_once_with(1)
        self.assertEqual(mock_get_blockset_index.call_count, 1)


class PyTetrisUpdateMovingBlockTestCase(TestCase):
    """Tests for PyTetris.update_moving_block
    """

    def setUp(self):
        patcher_create_block = mock.patch('pytetris.PyTetris.create_block')
        patcher_update_matrix = mock.patch('pytetris.PyTetris.update_matrix')
        patcher_judge_ground = mock.patch('pytetris.PyTetris.judge_ground')
        patcher_correct_top = mock.patch('pytetris.PyTetris.correct_top')
        patcher_move_down = mock.patch('pytetris.PyTetris.move_down')
        patcher_set_block_center = mock.patch('pytetris.PyTetris.set_block_center')
        patcher_create_screens = mock.patch('pytetris.PyTetris.create_screens')
        patcher_create_sounds = mock.patch('pytetris.PyTetris.create_sounds')
        self.mock_create_block = patcher_create_block.start()
        self.mock_update_matrix = patcher_update_matrix.start()
        self.mock_judge_ground = patcher_judge_ground.start()
        self.mock_correct_top = patcher_correct_top.start()
        self.mock_move_down = patcher_move_down.start()
        self.mock_set_block_center = patcher_set_block_center.start()
        patcher_create_screens.start()
        patcher_create_sounds.start()

    def tearDown(self):
        mock.patch.stopall()

    def test_update_moving_block_move_down(self):
        """If status is Status.Play and drop_timer is 0,
           move_down is called and drop_timer set to default.
        """
        blocks = [DummyBlock(3, 4) for _ in range(4)]
        timer_value = 40
        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'status', Status.PLAY), \
                mock.patch.object(tetris, 'drop_timer', 1, create=True), \
                mock.patch.object(tetris, 'timer_value', timer_value, create=True), \
                mock.patch.object(tetris, 'judge_timer', timer_value, create=True), \
                mock.patch.object(tetris, 'blocks', blocks):
            tetris.update_moving_block()
            self.assertEqual(tetris.drop_timer, timer_value)
            self.assertEqual(tetris.judge_timer, timer_value - 1)

        self.mock_move_down.assert_called_once()
        self.mock_correct_top.assert_not_called()
        self.mock_judge_ground.assert_not_called()
        self.mock_update_matrix.assert_not_called()
        self.mock_create_block.assert_not_called()
        self.assertEqual(self.mock_set_block_center.call_count, 4)

    def test_update_moving_block_correct_top(self):
        """If one of the blocks has row less than 0, correct_top must be called.
        """
        blocks = [DummyBlock(row, 4) for row in (-2, -1, 0, 1)]
        timer_value = 40
        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'status', Status.PLAY), \
                mock.patch.object(tetris, 'drop_timer', timer_value, create=True), \
                mock.patch.object(tetris, 'judge_timer', timer_value, create=True), \
                mock.patch.object(tetris, 'blocks', blocks):
            tetris.update_moving_block()
            self.assertEqual(tetris.drop_timer, timer_value - 1)
            self.assertEqual(tetris.judge_timer, timer_value - 1)

        self.mock_move_down.assert_not_called()
        self.mock_correct_top.assert_called_with(-2)
        self.mock_judge_ground.assert_not_called()
        self.mock_update_matrix.assert_not_called()
        self.mock_create_block.assert_not_called()
        self.assertEqual(self.mock_set_block_center.call_count, 4)

    def test_update_moving_block_judge_timer(self):
        """If judge_timer is 0, it must be set to timer_value.
        """
        blocks = [DummyBlock(row, 4) for row in range(4)]
        self.mock_judge_ground.side_effect = [False] * 4
        timer_value = 40
        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'status', Status.PLAY), \
                mock.patch.object(tetris, 'timer_value', timer_value, create=True), \
                mock.patch.object(tetris, 'drop_timer', timer_value, create=True), \
                mock.patch.object(tetris, 'judge_timer', 1, create=True), \
                mock.patch.object(tetris, 'blocks', blocks):
            tetris.update_moving_block()
            self.assertEqual(tetris.drop_timer, timer_value - 1)
            self.assertEqual(tetris.judge_timer, timer_value)

        self.assertEqual(self.mock_judge_ground.call_count, 4)
        self.assertEqual(self.mock_set_block_center.call_count, 4)
        self.mock_update_matrix.assert_not_called()
        self.mock_correct_top.assert_not_called()
        self.mock_move_down.assert_not_called()
        self.mock_create_block.assert_not_called()

    def test_update_moving_block_waiting(self):
        """If judge_ground returns True at least one time, ground_timer must be set to 50.
        """
        blocks = [DummyBlock(row, 4) for row in range(4)]
        matrix = [[None, None, None],
                  [DummyBlock(2, 0), DummyBlock(2, 1), DummyBlock(2, 2)],
                  [None, None, None]]
        self.mock_judge_ground.side_effect = [False, True, False, False]
        timer_value = 40
        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'status', Status.PLAY), \
                mock.patch.object(tetris, 'timer_value', timer_value, create=True), \
                mock.patch.object(tetris, 'drop_timer', timer_value, create=True), \
                mock.patch.object(tetris, 'judge_timer', 1, create=True), \
                mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'block_status', Status.DROPPING, create=True), \
                mock.patch.object(tetris, 'matrix', matrix):
            tetris.update_moving_block()
            self.assertEqual(tetris.drop_timer, timer_value - 1)
            self.assertEqual(tetris.judge_timer, timer_value)
            self.assertEqual(tetris.ground_timer, 50)
            self.assertEqual(tetris.block_status, Status.WAITING)
            self.assertEqual(tetris.update, tetris.update_ground_blocks)

        self.assertEqual(self.mock_judge_ground.call_count, 2)
        self.assertEqual(self.mock_set_block_center.call_count, 4)
        self.mock_update_matrix.assert_called_once()
        self.mock_move_down.assert_not_called()
        self.mock_correct_top.assert_not_called()
        self.mock_create_block.assert_not_called()

    def test_update_moving_block_gameover(self):
        """If judge_ground returns True at least one time, ground_timer must be set to 50.
        """
        blocks = [DummyBlock(row, 4) for row in range(4)]
        matrix = [[None, DummyBlock(2, 0), None],
                  [None, None, None],
                  [None, None, None]]
        self.mock_judge_ground.side_effect = [False, True, False, False]
        timer_value = 40
        mock_play = mock.MagicMock()
        mock_gameover_sound = mock.MagicMock()
        mock_gameover_sound.play = mock_play
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'status', Status.PLAY), \
                mock.patch.object(tetris, 'timer_value', timer_value, create=True), \
                mock.patch.object(tetris, 'drop_timer', timer_value, create=True), \
                mock.patch.object(tetris, 'judge_timer', 1, create=True), \
                mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'block_status', Status.DROPPING, create=True), \
                mock.patch.object(tetris, 'gameover_sound', mock_gameover_sound, create=True), \
                mock.patch.object(tetris, 'matrix', matrix):
            tetris.update_moving_block()
            self.assertEqual(tetris.drop_timer, timer_value - 1)
            self.assertEqual(tetris.judge_timer, timer_value)
            self.assertEqual(tetris.block_status, Status.DROPPING)
            self.assertEqual(tetris.status, Status.GAMEOVER)

        self.assertEqual(self.mock_judge_ground.call_count, 2)
        self.assertEqual(self.mock_set_block_center.call_count, 4)
        self.mock_update_matrix.assert_called_once()
        self.mock_move_down.assert_not_called()
        self.mock_correct_top.assert_not_called()
        mock_play.assert_called_once()
        self.mock_create_block.assert_not_called()

    def test_update_moving_block_create_block(self):
        """If blocks are grounded, create_block must be called.
        """
        blocks = [DummyBlock(row, 4) for row in range(4)]
        matrix = [[None, None, None],
                  [None, DummyBlock(2, 0), None],
                  [None, None, None]]
        self.mock_judge_ground.side_effect = [False, True, False, False]
        timer_value = 40
        mock_play = mock.MagicMock()
        mock_gameover_sound = mock.MagicMock()
        mock_gameover_sound.play = mock_play
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'status', Status.PLAY), \
                mock.patch.object(tetris, 'timer_value', timer_value, create=True), \
                mock.patch.object(tetris, 'drop_timer', timer_value, create=True), \
                mock.patch.object(tetris, 'judge_timer', 1, create=True), \
                mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'block_status', Status.DROPPING, create=True), \
                mock.patch.object(tetris, 'matrix', matrix):
            tetris.update_moving_block()
            self.assertEqual(tetris.drop_timer, 1)
            self.assertEqual(tetris.judge_timer, timer_value)
            self.assertEqual(tetris.block_status, Status.DROPPING)
            self.assertEqual(tetris.status, Status.PLAY)

        self.assertEqual(self.mock_judge_ground.call_count, 2)
        self.assertEqual(self.mock_set_block_center.call_count, 4)
        self.mock_update_matrix.assert_called_once()
        self.mock_create_block.assert_called_once()
        self.mock_move_down.assert_not_called()
        self.mock_correct_top.assert_not_called()


class PyTetrisUpdateGroundBlocksTestCase(TestCase):
    """Tests for PyTetris.update_moving_blocks
    """

    def setUp(self):
        patcher_clear_blodk = mock.patch('pytetris.PyTetris.create_block')
        patcher_move_ground_blocks = mock.patch('pytetris.PyTetris.move_ground_blocks')
        patcher_delete_blocks = mock.patch('pytetris.PyTetris.delete_blocks')
        patcher_create_screens = mock.patch('pytetris.PyTetris.create_screens')
        patcher_create_sounds = mock.patch('pytetris.PyTetris.create_sounds')
        self.mock_create_block = patcher_clear_blodk.start()
        self.mock_move_ground_blocks = patcher_move_ground_blocks.start()
        self.mock_delete_blocks = patcher_delete_blocks.start()
        patcher_create_screens.start()
        patcher_create_sounds.start()
        self.mock_break_sound = mock.MagicMock()
        self.mock_play = mock.MagicMock()
        self.mock_break_sound.play = self.mock_play

    def tearDown(self):
        mock.patch.stopall()

    def test_no_deleted_rows(self):
        """If ground_timer is 40 and deleted_rows is 0, no methods are called.
        """
        self.mock_delete_blocks.return_value = 0
        mock_score = mock.MagicMock()
        mock_add = mock.MagicMock()
        mock_score.add = mock_add
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'ground_timer', 41, create=True), \
                mock.patch.object(tetris, 'break_sound', self.mock_break_sound, create=True), \
                mock.patch.object(tetris, 'score', mock_score, create=True), \
                mock.patch.object(tetris, 'block_status', Status.WAITING, create=True):
            tetris.update_ground_blocks()
            self.assertEqual(tetris.ground_timer, 40)
            self.assertEqual(tetris.block_status, Status.WAITING)

        self.mock_delete_blocks.assert_called_once()
        self.mock_play.assert_not_called()
        mock_add.assert_not_called()
        self.mock_move_ground_blocks.assert_not_called()
        self.mock_create_block.assert_not_called()

    def test_deleted_rows_same_level(self):
        """If deleted_rows is not 0 but level is not changed, play and add methods are called.
        """
        self.mock_delete_blocks.return_value = 3
        mock_score = mock.MagicMock(level=1)
        mock_add = mock.MagicMock()
        mock_score.add = mock_add
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'ground_timer', 41, create=True), \
                mock.patch.object(tetris, 'break_sound', self.mock_break_sound, create=True), \
                mock.patch.object(tetris, 'score', mock_score, create=True), \
                mock.patch.object(tetris, 'level', 1, create=True), \
                mock.patch.object(tetris, 'block_status', Status.WAITING, create=True):
            tetris.update_ground_blocks()
            self.assertEqual(tetris.ground_timer, 40)
            self.assertEqual(tetris.block_status, Status.WAITING)

        self.mock_delete_blocks.assert_called_once()
        self.mock_play.assert_called_once()
        mock_add.assert_called_once_with(self.mock_delete_blocks.return_value)
        self.mock_move_ground_blocks.assert_not_called()
        self.mock_create_block.assert_not_called()

    def test_deleted_rows_not_same_level(self):
        """If deleted_rows is not 0 and level is changed, play and add methods are called.
        """
        self.mock_delete_blocks.return_value = 3
        mock_score = mock.MagicMock(level=2)
        mock_add = mock.MagicMock()
        mock_score.add = mock_add
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'ground_timer', 41, create=True), \
                mock.patch.object(tetris, 'timer_value', 20, create=True), \
                mock.patch.object(tetris, 'break_sound', self.mock_break_sound, create=True), \
                mock.patch.object(tetris, 'score', mock_score, create=True), \
                mock.patch.object(tetris, 'level', 1, create=True), \
                mock.patch.object(tetris, 'block_status', Status.WAITING, create=True):
            tetris.update_ground_blocks()
            self.assertEqual(tetris.ground_timer, 40)
            self.assertEqual(tetris.timer_value, 18)
            self.assertEqual(tetris.level, 2)
            self.assertEqual(tetris.block_status, Status.WAITING)

        self.mock_delete_blocks.assert_called_once()
        self.mock_play.assert_called_once()
        mock_add.assert_called_once_with(self.mock_delete_blocks.return_value)
        self.mock_move_ground_blocks.assert_not_called()
        self.mock_create_block.assert_not_called()

    def test_move_ground_blocks(self):
        """If ground_timer is 20, move_ground_blocks must be called.
        """
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'ground_timer', 21, create=True):
            tetris.update_ground_blocks()

        self.mock_delete_blocks.assert_not_called()
        self.mock_move_ground_blocks.assert_called_once()
        self.mock_create_block.assert_not_called()

    def test_create_block(self):
        """If ground_timer is 0, create_block must be called.
        """
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'ground_timer', 1, create=True), \
                mock.patch.object(tetris, 'drop_timer', 20, create=True), \
                mock.patch.object(tetris, 'block_status', Status.WAITING, create=True), \
                mock.patch.object(tetris, 'update', tetris.update_ground_blocks, create=True):
            tetris.update_ground_blocks()
            self.assertEqual(tetris.ground_timer, 0)
            self.assertEqual(tetris.drop_timer, 1)
            self.assertEqual(tetris.block_status, Status.DROPPING)
            self.assertEqual(tetris.update, tetris.update_moving_block)

        self.mock_delete_blocks.assert_not_called()
        self.mock_move_ground_blocks.assert_not_called()
        self.mock_create_block.assert_called_once()


@mock.patch('pytetris.PyTetris.create_screens')
@mock.patch('pytetris.PyTetris.create_sounds')
class PyTetrisDeleteBlocksTestCase(TestCase):
    """Tests for PyTetris.delete_blocks
    """

    def test_no_deleted_rows(self, mock_create_sounds, mock_create_screens):
        tetris = PyTetris(object())
        result = tetris.delete_blocks()

        self.assertEqual(result, 0)

    def test_deleted_rows(self, mock_create_sounds, mock_create_screens):
        mock_block = mock.MagicMock()
        mock_kill = mock.MagicMock()
        mock_block.kill = mock_kill
        matrix = [[None, None, None],
                  [mock_block, mock_block, mock_block],
                  [mock_block, mock_block, mock_block],
                  [None, None, None],
                  [None, None, None]]
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'matrix', matrix):
            result = tetris.delete_blocks()
            self.assertEqual(result, 2)

        self.assertEqual(mock_kill.call_count, 6)


@mock.patch('pytetris.PyTetris.set_block_center')
@mock.patch('pytetris.PyTetris.create_screens')
@mock.patch('pytetris.PyTetris.create_sounds')
class PyTetrisMoveGroundBlocksTestCase(TestCase):
    """Tests for PyTetris.move_ground_blocks
    """

    def test_move_ground_blocks_1(self, mock_create_sounds,
                                  mock_create_screens, mock_set_block_center):
        matrices = (
            [[None, None, None, None, None],
             [None, mock.MagicMock(row=1), None, None, None],
             [mock.MagicMock(row=2), mock.MagicMock(row=2), None, None, None],
             [None, None, None, None, mock.MagicMock(row=3)],
             [None, None, None, None, None],
             [None, None, None, None, None]],
            [[None, None, None, None, None],
             [None, mock.MagicMock(row=1), None, None, None],
             [mock.MagicMock(row=2), mock.MagicMock(row=2), None, mock.MagicMock(row=2), None],
             [None, None, None, None, None],
             [None, None, None, None, None],
             [None, mock.MagicMock(row=5), None, mock.MagicMock(row=5), None]]
        )
        expects = (
            [[None, None, None, None, None],
             [None, None, None, None, None],
             [None, None, None, None, None],
             [None, mock.MagicMock(row=3), None, None, None],
             [mock.MagicMock(row=4), mock.MagicMock(row=4), None, None, None],
             [None, None, None, None, mock.MagicMock(row=5)]],
            [[None, None, None, None, None],
             [None, None, None, None, None],
             [None, None, None, None, None],
             [None, mock.MagicMock(row=3), None, None, None],
             [mock.MagicMock(row=4), mock.MagicMock(row=4), None, mock.MagicMock(row=4), None],
             [None, mock.MagicMock(row=5), None, mock.MagicMock(row=5), None]]
        )
        calls_expects = [4, 6]
        tetris = PyTetris(object())

        for matrix, expect, calls in zip(matrices, expects, calls_expects):
            with mock.patch.object(tetris, 'matrix', matrix):
                tetris.move_ground_blocks()

            for matrix_row, expect_row in zip(matrix, expect):
                for matrix_block, expect_block in zip(matrix_row, expect_row):
                    with self.subTest((matrix_block, expect_block)):
                        if expect_block is None:
                            self.assertTrue(matrix_block is None)
                        else:
                            self.assertEqual(matrix_block.row, expect_block.row)
            self.assertEqual(mock_set_block_center.call_count, calls)
            mock_set_block_center.reset_mock()


class PyTetrisCneckAndJudgeMethosTestCase(TestCase):
    """Tests for judge and check methos of PyTetris
    """

    def setUp(self):
        self.matrix = [
            [None, None, None, None, None],
            [DummyBlock(1, 0), DummyBlock(1, 1), None, None, None],
            [None, None, None, None, DummyBlock(2, 4)],
            [None, None, None, None, None],
            [None, None, None, None, None]
        ]
        patcher_create_screens = mock.patch('pytetris.PyTetris.create_screens')
        padcher_create_sounds = mock.patch('pytetris.PyTetris.create_sounds')
        patcher_create_screens.start()
        padcher_create_sounds.start()

    def tearDown(self):
        mock.patch.stopall()

    def test_check_matrix(self):
        """Test for check_matrix
        """
        tests = [(0, 1), (1, 1), (1, 4), (2, 1), (2, 4)]
        expects = [False, True, False, False, True]
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'matrix', self.matrix):
            for test, expect in zip(tests, expects):
                with self.subTest():
                    result = tetris.check_matrix(*test)
                    self.assertEqual(result, expect)

    def test_judge_left(self):
        """Test for judge_left
        """
        tests = [DummyBlock(1, 0), DummyBlock(1, 1), DummyBlock(1, 3)]
        expects = [False, False, True]
        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'matrix', self.matrix):
            for test, expect in zip(tests, expects):
                with self.subTest((test, expect)):
                    result = tetris.judge_left(test)
                    self.assertEqual(result, expect)

    def test_judge_right(self):
        """Test for judge_right
        """
        tests = [DummyBlock(1, 9), DummyBlock(2, 3), DummyBlock(1, 3)]
        expects = [False, False, True]
        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'matrix', self.matrix):
            for test, expect in zip(tests, expects):
                with self.subTest((test, expect)):
                    result = tetris.judge_right(test)
                    self.assertEqual(result, expect)

    def test_judge_down(self):
        """Test for judge_down
        """
        tests = [DummyBlock(20, 0), DummyBlock(0, 1), DummyBlock(0, 4)]
        expects = [False, False, True]
        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'matrix', self.matrix):
            for test, expect in zip(tests, expects):
                with self.subTest((test, expect)):
                    result = tetris.judge_down(test)
                    self.assertEqual(result, expect)

    def test_judge_ground(self):
        """Test for judge_ground
        """
        tests = [DummyBlock(19, 0), DummyBlock(0, 1), DummyBlock(0, 4)]
        expects = [True, True, False]
        tetris = PyTetris(object())
        with mock.patch.object(tetris, 'matrix', self.matrix):
            for test, expect in zip(tests, expects):
                with self.subTest((test, expect)):
                    result = tetris.judge_ground(test)
                    self.assertEqual(result, expect)

    @mock.patch('pytetris.min')
    @mock.patch('pytetris.max')
    def test_judge_rotate(self, mock_max, mock_min):
        """Test for judge_rotate
        """
        mock_max.side_effect = [1, 1, 0, 0, 0, 0]
        mock_min.side_effect = [-1, -1, 0, 0]
        tests = [
            np.array([[3, 3], [3, 4], [2, 4], [2, 5]]),
            np.array([[4, 3], [4, 4], [3, 4], [3, 5]]),
            np.array([[3, -1], [3, 0], [4, 0], [4, 1]]),
            np.array([[1, -1], [1, 0], [2, 0], [2, 1]]),
            np.array([[3, 1], [3, 2], [4, 2], [4, 3]]),
            np.array([[2, 3], [2, 4], [3, 2], [3, 3]])]
        expects = [(False, 0), (True, 1), (True, -1), (False, 0), (True, 0), (False, 0)]
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'matrix', self.matrix):
            for test, expect in zip(tests, expects):
                with self.subTest((test, expect)):
                    result = tetris.judge_rotate(test)
                    self.assertEqual(result, expect)


class PyTetrisCorrectTopTestCase(TestCase):
    """Tests for correct_top
    """

    @mock.patch('pytetris.PyTetris.create_screens')
    @mock.patch('pytetris.PyTetris.create_sounds')
    def test_correct_top(self, mock_create_sounds, mock_create_screens):
        mock_block = mock.MagicMock()
        mock_kill = mock.MagicMock()
        mock_block.kill = mock_kill
        expects = [(-2, 3), (-1, 3), (0, 3), (1, 3)]
        blocks = []
        for row, col in expects:
            blocks.append(mock.MagicMock(row=row, col=col))
        matrix = [
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, mock_block, None],
            [None, None, None, mock_block, None],
            [None, None, None, mock_block, None],
            [None, None, None, mock_block, None]]
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'matrix', matrix):
            tetris.correct_top(-2)
        self.assertEqual(mock_kill.call_count, 2)

        for block, (row, col) in zip(blocks, expects):
            with self.subTest():
                self.assertEqual((block.row - 2, block.col), (row, col))


class PyTetrisUpdateMatrixTestCase(TestCase):
    """Tests for update_matrix
    """

    @mock.patch('pytetris.PyTetris.create_screens')
    @mock.patch('pytetris.PyTetris.create_sounds')
    def test_update_matrix(self, mock_create_sounds, mock_create_screens):
        blocks = [
            DummyBlock(2, 4),
            DummyBlock(3, 4),
            DummyBlock(4, 4),
            DummyBlock(5, 4)]
        matrix = [[None for _ in range(5)] for _ in range(10)]
        expects = set((block.row, block.col) for block in blocks)
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'matrix', matrix):
            tetris.update_matrix()

        for i, row in enumerate(matrix):
            for j, cell in enumerate(row):
                with self.subTest():
                    if (i, j) in expects:
                        self.assertTrue(matrix[i][j])
                    else:
                        self.assertTrue(matrix[i][j] is None)


class PyTetrisMoveMethodsTestCase(TestCase):
    """Tests for move methods in PyTetris
    """

    def setUp(self):
        patcher_create_screens = mock.patch('pytetris.PyTetris.create_screens')
        padcher_create_sounds = mock.patch('pytetris.PyTetris.create_sounds')
        patcher_create_screens.start()
        padcher_create_sounds.start()
        patcher_all = mock.patch('pytetris.all')
        patcher_update_blockset_col = mock.patch('pytetris.update_blockset_col')
        patcher_update_blockset_row = mock.patch('pytetris.update_blockset_row')
        self.mock_all = patcher_all.start()
        self.mock_update_blockset_col = patcher_update_blockset_col.start()
        self.mock_update_blockset_row = patcher_update_blockset_row.start()
        self.blockset = [[None, None, None], [None, None, None]]

    def tearDown(self):
        mock.patch.stopall()

    def get_brockset(self):
        blocks = [
            mock.MagicMock(row=2, col=4),
            mock.MagicMock(row=2, col=5),
            mock.MagicMock(row=3, col=4),
            mock.MagicMock(row=3, col=5)]
        return blocks

    def test_move_right_all_return_true(self):
        """If all returns True, columns of blocks must be incremented by +1.
        """
        self.mock_all.return_value = True
        tetris = PyTetris(object())
        expect = [(2, 5), (2, 6), (3, 5), (3, 6)]
        blocks = self.get_brockset()

        with mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'blockset', self.blockset, create=True):
            tetris.move_right()
            self.mock_update_blockset_col.assert_called_once_with(tetris.blockset, 1)

        for i in range(len(blocks)):
            with self.subTest():
                block = blocks[i]
                self.assertEqual((block.row, block.col), expect[i])

    def test_move_right_all_return_false(self):
        """If all returns True, columns of blocks must not be changed.
        """
        self.mock_all.return_value = False
        tetris = PyTetris(object())
        expect = [(2, 4), (2, 5), (3, 4), (3, 5)]
        blocks = self.get_brockset()

        with mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'blockset', self.blockset, create=True):
            tetris.move_right()
            self.mock_update_blockset_col.assert_not_called()

        for i in range(len(blocks)):
            with self.subTest():
                block = blocks[i]
                self.assertEqual((block.row, block.col), expect[i])

    def test_move_left_all_return_true(self):
        """If all returns True, columns of blocks must be incremented by -1.
        """
        self.mock_all.return_value = True
        tetris = PyTetris(object())
        expect = [(2, 3), (2, 4), (3, 3), (3, 4)]
        blocks = self.get_brockset()

        with mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'blockset', self.blockset, create=True):
            tetris.move_left()
            self.mock_update_blockset_col.assert_called_once_with(tetris.blockset, -1)

        for i in range(len(blocks)):
            with self.subTest():
                block = blocks[i]
                self.assertEqual((block.row, block.col), expect[i])

    def test_move_left_all_return_false(self):
        """If all returns True, columns of blocks must not be changed.
        """
        self.mock_all.return_value = False
        tetris = PyTetris(object())
        expect = [(2, 4), (2, 5), (3, 4), (3, 5)]
        blocks = self.get_brockset()

        with mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'blockset', self.blockset, create=True):
            tetris.move_left()
            self.mock_update_blockset_col.assert_not_called()

        for i in range(len(blocks)):
            with self.subTest():
                block = blocks[i]
                self.assertEqual((block.row, block.col), expect[i])

    def test_move_down_all_return_true(self):
        """If all returns True, rows of blocks must be incremented by +1.
        """
        self.mock_all.return_value = True
        tetris = PyTetris(object())
        expect = [(3, 4), (3, 5), (4, 4), (4, 5)]
        blocks = self.get_brockset()

        with mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'blockset', self.blockset, create=True):
            tetris.move_down()
            self.mock_update_blockset_row.assert_called_once_with(tetris.blockset, 1)

        for i in range(len(blocks)):
            with self.subTest():
                block = blocks[i]
                self.assertEqual((block.row, block.col), expect[i])

    def test_move_down_all_return_false(self):
        """If all returns True, rows of blocks must not be changed.
        """
        self.mock_all.return_value = False
        tetris = PyTetris(object())
        expect = [(2, 4), (2, 5), (3, 4), (3, 5)]
        blocks = self.get_brockset()

        with mock.patch.object(tetris, 'blocks', blocks), \
                mock.patch.object(tetris, 'blockset', self.blockset, create=True):
            tetris.move_down()
            self.mock_update_blockset_row.assert_not_called()

        for i in range(len(blocks)):
            with self.subTest():
                block = blocks[i]
                self.assertEqual((block.row, block.col), expect[i])


class PyTetrisRotateTestCase(TestCase):
    """Tests for rotate mothod
    """

    def setUp(self):
        patcher_create_screens = mock.patch('pytetris.PyTetris.create_screens')
        padcher_create_sounds = mock.patch('pytetris.PyTetris.create_sounds')
        patcher_create_screens.start()
        padcher_create_sounds.start()
        patcher_create_screens = mock.patch('pytetris.PyTetris.judge_rotate')
        self.mock_judge_rotate = patcher_create_screens.start()
        self.mock_rotate_sound = mock.MagicMock()
        self.mock_play = mock.MagicMock()
        self.mock_rotate_sound.play = self.mock_play
        self.blockset = np.array(
            [[[-1, 4], [0, 3], [0, 4], [0, 5]],
             [[-1, 4], [0, 4], [1, 4], [0, 3]],
             [[-1, 3], [-1, 4], [-1, 5], [0, 4]],
             [[-1, 4], [0, 4], [1, 4], [0, 5]]])
        self.blocks = [
            mock.MagicMock(row=-1, col=3),
            mock.MagicMock(row=-1, col=4),
            mock.MagicMock(row=-1, col=5),
            mock.MagicMock(row=0, col=4)]

    def tearDown(self):
        mock.patch.stopall()

    def test_rotatable_is_true(self):
        """If judge_rotate returns True, block must be rotated.
        """
        self.mock_judge_rotate.return_value = (True, 2)
        expects = [(-1, 2), (0, 2), (1, 2), (0, 3)]
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'index', 2, create=True), \
                mock.patch.object(tetris, 'blockset', self.blockset, create=True), \
                mock.patch.object(tetris, 'rotate_sound', self.mock_rotate_sound, create=True), \
                mock.patch.object(tetris, 'blocks', self.blocks, create=True):
            tetris.rotate()
            self.mock_play.assert_called_once()
            self.assertEqual(tetris.index, 3)

        for block, expect in zip(self.blocks, expects):
            with self.subTest():
                self.assertEqual((block.row, block.col), expect)

    def test_rotatable_is_false(self):
        """If judge_rotate returns True, block is not rotated.
        """
        self.mock_judge_rotate.return_value = (False, 0)
        expects = [(-1, 3), (-1, 4), (-1, 5), (0, 4)]
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'index', 1, create=True), \
                mock.patch.object(tetris, 'blockset', self.blockset, create=True), \
                mock.patch.object(tetris, 'rotate_sound', self.mock_rotate_sound, create=True):
            tetris.rotate()
            self.mock_play.assert_not_called()
            self.assertEqual(tetris.index, 1)

        for block, expect in zip(self.blocks, expects):
            with self.subTest():
                self.assertEqual((block.row, block.col), expect)

    def test_rotatable_index_set_to_0(self):
        """If judge_rotate returns True, block must be rotated.
        """
        self.mock_judge_rotate.return_value = (True, 0)
        expects = [(-1, 4), (0, 3), (0, 4), (0, 5)]
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'index', 3, create=True), \
                mock.patch.object(tetris, 'blockset', self.blockset, create=True), \
                mock.patch.object(tetris, 'rotate_sound', self.mock_rotate_sound, create=True), \
                mock.patch.object(tetris, 'blocks', self.blocks, create=True):
            tetris.rotate()
            self.mock_play.assert_called_once()
            self.assertEqual(tetris.index, 0)

        for block, expect in zip(self.blocks, expects):
            with self.subTest():
                self.assertEqual((block.row, block.col), expect)


class PyTetrisClickTestCase(TestCase):
    """Tests for click mothod
    """

    def setUp(self):
        patcher_create_screens = mock.patch('pytetris.PyTetris.create_screens')
        padcher_create_sounds = mock.patch('pytetris.PyTetris.create_sounds')
        patcher_create_screens.start()
        padcher_create_sounds.start()
        patcher_initialize = mock.patch('pytetris.PyTetris.initialize')
        self.mock_initialize = patcher_initialize.start()

    def tearDown(self):
        mock.patch.stopall()

    def test_click_stop_button(self):
        mock_collidepoint = mock.MagicMock()
        mock_stop_button = mock.MagicMock()
        mock_stop_button.rect.collidepoint = mock_collidepoint
        mock_collidepoint.return_value = True
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'status', Status.PLAY), \
                mock.patch.object(tetris, 'stop_button', mock_stop_button, create=True):
            tetris.click(3, 3)
            self.assertEqual(tetris.status, Status.START)

    def test_click_pause_button(self):
        # stop button
        mock_stop_collidepoint = mock.MagicMock()
        mock_stop_button = mock.MagicMock()
        mock_stop_button.rect.collidepoint = mock_stop_collidepoint
        mock_stop_collidepoint.return_value = False
        # pause button
        mock_pause_collidepoint = mock.MagicMock()
        mock_pause_button = mock.MagicMock()
        mock_pause_button.rect.collidepoint = mock_pause_collidepoint
        mock_pause_collidepoint.return_value = True
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'status', Status.PLAY), \
                mock.patch.object(tetris, 'stop_button', mock_stop_button, create=True), \
                mock.patch.object(tetris, 'pause_button', mock_pause_button, create=True), \
                mock.patch.object(tetris, 'update', tetris.update_moving_block, create=True):
            tetris.click(3, 3)
            self.assertEqual(tetris.status, Status.PAUSE)
        self.assertEqual(tetris.update_before_pause, tetris.update_moving_block)

    def test_click_restart_button(self):
        mock_collidepoint = mock.MagicMock()
        mock_restart_button = mock.MagicMock()
        mock_restart_button.rect.collidepoint = mock_collidepoint
        mock_collidepoint.return_value = True
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'status', Status.PAUSE), \
                mock.patch.object(tetris, 'restart_button', mock_restart_button, create=True), \
                mock.patch.object(tetris, 'update_before_pause', tetris.update_ground_blocks, create=True):
            tetris.click(3, 3)
            self.assertEqual(tetris.status, Status.PLAY)
        self.assertEqual(tetris.update, tetris.update_ground_blocks)

    def test_click_start_button(self):
        mock_collidepoint = mock.MagicMock()
        mock_start_button = mock.MagicMock()
        mock_start_button.rect.collidepoint = mock_collidepoint
        mock_collidepoint.return_value = True
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'status', Status.START), \
                mock.patch.object(tetris, 'start_button', mock_start_button, create=True), \
                mock.patch.object(tetris, 'update_before_pause', tetris.update_ground_blocks, create=True):
            tetris.click(3, 3)
            self.assertEqual(tetris.status, Status.START)
        self.mock_initialize.assert_called_once()

    def test_click_repeat_button(self):
        mock_collidepoint = mock.MagicMock()
        mock_repeat_button = mock.MagicMock()
        mock_repeat_button.rect.collidepoint = mock_collidepoint
        mock_collidepoint.return_value = True
        mock_gameover_screen = mock.MagicMock()
        mock_gameover_initialize = mock.MagicMock()
        mock_gameover_screen.initialize = mock_gameover_initialize
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'status', Status.REPEAT), \
                mock.patch.object(tetris, 'repeat_button', mock_repeat_button, create=True), \
                mock.patch.object(tetris, 'gameover_screen', mock_gameover_screen, create=True):
            tetris.click(3, 3)
            self.assertEqual(tetris.status, Status.REPEAT)
        self.mock_initialize.assert_called_once()
        mock_gameover_initialize.assert_called_once()


class ScoreTestCase(TestCase):
    """Tests for Score class
    """

    @mock.patch('pytetris.pygame.font.SysFont')
    def test_add(self, mock_sysfont):
        tests = [1, 2, 3, 4]
        # (lines, level, score)
        expects = [(1, 1, 40), (3, 1, 140), (6, 1, 440), (10, 2, 2840)]
        score = Score(object())

        for test, expect in zip(tests, expects):
            with self.subTest():
                score.add(test)
                self.assertEqual(
                    (score.lines, score.level, score.score), expect)


class GameOverTestCase(TestCase):
    """Tests for GameOver class
    """

    def setUp(self):
        GameOver.containers = object()
        patcher_load = mock.patch('pytetris.pygame.image.load')
        patcher_sprite = mock.patch('pytetris.pygame.sprite.Sprite.__init__')
        patcher_sysfont = mock.patch('pytetris.pygame.font.SysFont')
        mock_load = patcher_load.start()
        patcher_sprite.start()
        self.mock_sysfont = patcher_sysfont.start()

        mock_image = mock.MagicMock()
        mock_get_rect = mock.MagicMock()
        mock_get_rect.return_value = mock.MagicMock(left=0, top=0)
        mock_image.get_rect = mock_get_rect

        mock_convert_alpha = mock.MagicMock()
        mock_convert_alpha.return_value = mock_image
        mock_load.convert_alpha = mock_convert_alpha

    def tearDown(self):
        mock.patch.stopall()

    @mock.patch('pytetris.GameOver.draw_image')
    @mock.patch('pytetris.GameOver.draw_text')
    def test_update_status_is_none(self, mock_draw_text, mock_draw_image):
        gameover = GameOver('test.png', mock.MagicMock(), mock.MagicMock())
        with mock.patch.object(gameover, 'timer', 1):
            gameover.update()
            self.assertEqual(gameover.timer, 20)
            self.assertEqual(gameover.status, Status.REPEAT)
            self.assertEqual(gameover.game.status, Status.REPEAT)
        mock_draw_image.assert_called_once()
        mock_draw_text.assert_not_called()

    @mock.patch('pytetris.GameOver.draw_image')
    @mock.patch('pytetris.GameOver.draw_text')
    def test_update_status_is_none_timer_not_zero(self, mock_draw_text, mock_draw_image):
        gameover = GameOver('test.png', mock.MagicMock(), mock.MagicMock())
        with mock.patch.object(gameover, 'timer', 100):
            gameover.update()
            self.assertEqual(gameover.timer, 99)
            self.assertEqual(gameover.status, None)
        mock_draw_image.assert_called_once()
        mock_draw_text.assert_not_called()

    @mock.patch('pytetris.GameOver.draw_image')
    @mock.patch('pytetris.GameOver.draw_text')
    def test_update_status_is_not_none(self, mock_draw_text, mock_draw_image):
        gameover = GameOver('test.png', mock.MagicMock(), mock.MagicMock())
        with mock.patch.object(gameover, 'status', Status.REPEAT):
            gameover.update()
            self.assertEqual(gameover.timer, 100)
        mock_draw_image.assert_called_once()
        mock_draw_text.assert_called_once()

    def test_draw_image_top_less_than_gameovertop(self):
        gameover = GameOver('test.png', mock.MagicMock(), mock.MagicMock())
        gameover.draw_image()
        self.assertEqual(gameover.top, 20)
        self.assertEqual(gameover.is_drop, True)
        self.assertEqual(gameover.rect.left, GAMEOVER_LEFT)
        self.assertEqual(gameover.rect.top, 20)

    def test_draw_image_top_more_than_gameovertop(self):
        gameover = GameOver('test.png', mock.MagicMock(), mock.MagicMock())

        with mock.patch.object(gameover, 'top', GAMEOVER_TOP + 20):  # GAMEOVER_TOP + 20 is 240
            gameover.draw_image()
            self.assertEqual(gameover.stop, 1)
            self.assertEqual(gameover.is_drop, False)
            self.assertEqual(gameover.top, GAMEOVER_TOP + 15)  # GAMEOVER_TOP + 15 is 235

        self.assertEqual(gameover.rect.left, GAMEOVER_LEFT)
        self.assertEqual(gameover.rect.top, GAMEOVER_TOP + 15)

    def test_draw_image_top_less_than_gameoverboundtop(self):
        gameover = GameOver('test.png', mock.MagicMock(), mock.MagicMock())

        # GAMEOVER_BOUND_TOP -5 is 165
        with mock.patch.object(gameover, 'top', GAMEOVER_BOUND_TOP - 5), \
                mock.patch.object(gameover, 'stop', 1), \
                mock.patch.object(gameover, 'is_drop', False):
            gameover.draw_image()
            self.assertEqual(gameover.stop, 1)
            self.assertEqual(gameover.is_drop, True)

        self.assertEqual(gameover.rect.left, GAMEOVER_LEFT)
        self.assertEqual(gameover.rect.top, GAMEOVER_BOUND_TOP - 5)

    def test_draw_text(self):
        mock_render = mock.MagicMock()
        mock_font = mock.MagicMock()
        mock_font.render = mock_render
        self.mock_sysfont.return_value = mock_font
        mock_screen = mock.MagicMock()
        mock_screen.blit = mock.MagicMock()

        gameover = GameOver('test.png', mock_screen, mock.MagicMock())

        with mock.patch.object(gameover, 'timer', 1):
            gameover.draw_text()
            self.assertEqual(gameover.index, 0)
            self.assertEqual(gameover.timer, 20)

    def test_draw_text_index_more_than_messagesize(self):
        mock_render = mock.MagicMock()
        mock_font = mock.MagicMock()
        mock_font.render = mock_render
        self.mock_sysfont.return_value = mock_font
        mock_screen = mock.MagicMock()
        mock_screen.blit = mock.MagicMock()

        gameover = GameOver('test.png', mock_screen, mock.MagicMock())

        with mock.patch.object(gameover, 'timer', 1), \
                mock.patch.object(gameover, 'index', 3):
            gameover.draw_text()
            self.assertEqual(gameover.index, -1)
            self.assertEqual(gameover.timer, 20)


class StartTestCase(TestCase):
    """Tests for Start class
    """

    def setUp(self):
        Start.containers = object()
        patcher_load = mock.patch('pytetris.pygame.image.load')
        patcher_sprite = mock.patch('pytetris.pygame.sprite.Sprite.__init__')
        patcher_sysfont = mock.patch('pytetris.pygame.font.SysFont')
        mock_load = patcher_load.start()
        patcher_sprite.start()
        self.mock_sysfont = patcher_sysfont.start()
        mock_render = mock.MagicMock()
        self.mock_sysfont.render = mock_render

        mock_image = mock.MagicMock()
        mock_get_rect = mock.MagicMock()
        mock_get_rect.return_value = mock.MagicMock(left=0, top=0)
        mock_image.get_rect = mock_get_rect

        mock_convert = mock.MagicMock()
        mock_convert.return_value = mock_image
        mock_load.convert = mock_convert

    def tearDown(self):
        mock.patch.stopall()

    def test_draw_text_timer_set_to_20(self):
        mock_screen = mock.MagicMock()
        mock_blit = mock.MagicMock()
        mock_screen.blit = mock_blit
        start = Start('test.png', mock_screen)

        with mock.patch.object(start, 'timer', 1):
            start.draw_text()
            self.assertEqual(start.timer, 20)
            self.assertEqual(start.index, 0)

    def test_draw_text_index_set_to_default(self):
        mock_screen = mock.MagicMock()
        mock_blit = mock.MagicMock()
        mock_screen.blit = mock_blit
        start = Start('test.png', mock_screen)

        with mock.patch.object(start, 'timer', 1), \
                mock.patch.object(start, 'index', 2):
            start.draw_text()
            self.assertEqual(start.timer, 20)
            self.assertEqual(start.index, -1)


class PauseTestCase(TestCase):
    """Tests for Pause class
    """

    def setUp(self):
        Pause.containers = object()
        patcher_sprite = mock.patch('pytetris.pygame.sprite.Sprite.__init__')
        patcher_sysfont = mock.patch('pytetris.pygame.font.SysFont')
        patcher_sprite.start()
        patcher_sysfont.start()

        mock_image = mock.MagicMock()
        mock_image.get_rect.return_value = mock.MagicMock()

        def generator():
            for _ in range(7):
                yield mock_image

        patcher_create_image = mock.patch('pytetris.Pause.create_image')
        mock_create_image = patcher_create_image.start()
        mock_create_image.return_value = generator()

    def tearDown(self):
        mock.patch.stopall()

    def test_draw_image_timer_is_0(self):
        pause = Pause('images', mock.MagicMock())
        with mock.patch.object(pause, 'timer', 1):
            pause.draw_image()
            self.assertEqual(pause.timer, 20)
            self.assertEqual(pause.index, 1)

    def test_draw_image_index_timer_is_20(self):
        pause = Pause('images', mock.MagicMock())
        pause.draw_image()
        self.assertEqual(pause.timer, 19)
        self.assertEqual(pause.index, 0)

    def test_draw_image_index_set_to_default(self):
        pause = Pause('images', mock.MagicMock())
        with mock.patch.object(pause, 'timer', 1), \
                mock.patch.object(pause, 'index', 7):
            pause.draw_image()
            self.assertEqual(pause.timer, 20)
            self.assertEqual(pause.index, 1)


if __name__ == '__main__':
    main()
