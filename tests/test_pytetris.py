import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import itertools
from collections import namedtuple
from pathlib import Path
from unittest import TestCase, main, mock

from pytetris import ImageFiles, SoundFiles, PyTetris, BLOCKSETS, Status, Score


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

@mock.patch('pytetris.PyTetris.create_screens')
@mock.patch('pytetris.PyTetris.create_sounds')
class PyTetrisCneckAndJudgeMethosTestCase(TestCase):
    """Tests for judge and check methos of PyTetris
    """

    def test_check_matrix(self, mock_create_sounds, mock_create_screens):
        """Tests for check_matrix
        """
        matrix = [
            [None, None, None, None, None],
            [DummyBlock(1, 0), DummyBlock(1, 1), None, None, None],
            [None, None, None, None, DummyBlock(2, 4)]
        ]
        tests = [(0, 1), (1, 1), (1, 4), (2, 1), (2, 4)]
        expects = [None, True, None, None, True]
        tetris = PyTetris(object())

        with mock.patch.object(tetris, 'matrix', matrix):
            for test, expect in zip(tests, expects):
                with self.subTest():
                    result = tetris.check_matrix(*test)
                    self.assertEqual(result, expect)


if __name__ == '__main__':
    main()