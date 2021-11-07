import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import itertools
from collections import namedtuple
from pathlib import Path
from unittest import TestCase, main, mock

from pytetris import ImageFiles, SoundFiles, PyTetris, BLOCKSETS, Status


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


class PyTetrisCreateBlockTestCase(TestCase):
    """Tests for PyTetris.create_block
    """

    @mock.patch('pytetris.PyTetris.create_screens')
    @mock.patch('pytetris.PyTetris.create_sounds')
    @mock.patch('pytetris.PyTetris.get_blockset_index')
    @mock.patch('pytetris.Block')
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

    @mock.patch('pytetris.PyTetris.create_screens')
    @mock.patch('pytetris.PyTetris.create_sounds')
    @mock.patch('pytetris.PyTetris.get_blockset_index')
    @mock.patch('pytetris.Block')
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

    @mock.patch('pytetris.PyTetris.set_block_center')
    @mock.patch('pytetris.PyTetris.correct_top')
    @mock.patch('pytetris.PyTetris.move_down')
    @mock.patch('pytetris.PyTetris.create_screens')
    @mock.patch('pytetris.PyTetris.create_sounds')
    def test_update_moving_block(self, mock_create_sounds, mock_create_screens, mock_move_down,
                                 mock_correct_top, mock_set_block_center):
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

        mock_move_down.assert_called_once()
        mock_correct_top.assert_not_called()
        self.assertEqual(mock_set_block_center.call_count, 4)





if __name__ == '__main__':
    main()