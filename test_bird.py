"""실행: python -m unittest -v test_bird"""

import unittest
from unittest.mock import Mock, patch

import bird
import game_framework
import game_world
import play_mode


class BirdTests(unittest.TestCase):
    def setUp(self):
        self.image = Mock(w=918, h=506)
        self.loader = patch('bird.load_image', return_value=self.image)
        self.width = patch('bird.get_canvas_width', return_value=1600)
        self.loader.start()
        self.width.start()
        bird.Bird.image = None
        self.old_frame_time = game_framework.frame_time
        self.addCleanup(self.loader.stop)
        self.addCleanup(self.width.stop)
        self.addCleanup(setattr, game_framework, 'frame_time', self.old_frame_time)
        self.addCleanup(setattr, bird.Bird, 'image', None)
        self.addCleanup(game_world.clear)

    def advance(self, item, seconds, fps):
        game_framework.frame_time = 1 / fps
        for _ in range(round(seconds * fps)):
            item.update()

    def test_frame_rectangles_exclude_empty_cell(self):
        rectangles = [bird.frame_rect(i, 918, 506) for i in range(14)]
        self.assertEqual(len(set(rectangles)), 14)
        self.assertEqual(rectangles[0], (0, 338, 183, 168))
        self.assertEqual(rectangles[-1], (549, 2, 183, 168))
        self.assertEqual(bird.frame_rect(14, 918, 506), rectangles[0])
        for x, y, w, h in rectangles:
            self.assertTrue(0 <= x < x + w <= 918)
            self.assertTrue(0 <= y < y + h <= 506)

    def test_flock_distribution_and_shared_image(self):
        flock = bird.create_flock()
        self.assertEqual(len(flock), 10)
        self.assertEqual(len({item.y for item in flock}), 10)
        self.assertEqual(min(item.y for item in flock), 350)
        self.assertEqual(max(item.y for item in flock), 500)
        self.assertEqual(len({item.x for item in flock}), 10)
        self.assertEqual(len({item.frame for item in flock}), 10)
        self.assertEqual({item.direction for item in flock}, {-1, 1})
        self.assertTrue(all(item.image is self.image for item in flock))
        bird.load_image.assert_called_once_with('bird_animation.png')

    def test_speed_cycle_and_frame_rate_independence(self):
        for fps in (15, 30, 60, 144):
            item = bird.Bird(200, 425, frame=2.5)
            self.advance(item, 3, fps)
            self.assertAlmostEqual(item.x, 700)
            self.assertAlmostEqual(item.frame, 2.5)
            self.assertEqual(item.y, 425)

    def test_complete_flap_cycle(self):
        item = bird.Bird(200, 400, frame=0)
        game_framework.frame_time = 0.6 / 14
        frames = []
        for _ in range(14):
            frames.append(int(item.frame))
            item.update()
        self.assertEqual(frames, list(range(14)))
        self.assertAlmostEqual(item.frame % 14, 0)
        self.assertAlmostEqual(item.x, 300)

    def test_both_edges_preserve_overshoot(self):
        game_framework.frame_time = 0.12  # 20px 이동
        right = bird.Bird(1550, 400, direction=1, frame=3)
        right.update()
        self.assertAlmostEqual(right.x, 1540)
        self.assertEqual(right.direction, -1)
        self.assertNotEqual(right.frame, 0)
        left = bird.Bird(50, 400, direction=-1)
        left.update()
        self.assertAlmostEqual(left.x, 60)
        self.assertEqual(left.direction, 1)

    def test_large_time_step_matches_small_steps(self):
        one_step = bird.Bird(1000, 400, direction=-1, frame=4)
        many_steps = bird.Bird(1000, 400, direction=-1, frame=4)
        game_framework.frame_time = 120
        one_step.update()
        self.advance(many_steps, 120, 60)
        self.assertAlmostEqual(one_step.x, many_steps.x)
        self.assertEqual(one_step.direction, many_steps.direction)
        self.assertTrue(45 <= one_step.x <= 1555)

    def test_draw_faces_direction(self):
        item = bird.Bird(200, 400, direction=-1, frame=13)
        item.draw()
        args = self.image.clip_composite_draw.call_args.args
        self.assertEqual(args[:4], (549, 2, 183, 168))
        self.assertEqual(args[5], 'h')
        item.direction = 1
        item.draw()
        self.assertEqual(self.image.clip_composite_draw.call_args.args[5], '')

    def test_scene_restart_and_cleanup(self):
        with patch('play_mode.Boy'), patch('play_mode.Grass'):
            for _ in range(2):
                play_mode.init()
                objects = [obj for layer in game_world.world for obj in layer]
                self.assertEqual(sum(isinstance(obj, bird.Bird) for obj in objects), 10)
                self.assertEqual(len(objects), 12)
            play_mode.finish()
            self.assertTrue(all(not layer for layer in game_world.world))
            self.assertIsNone(play_mode.boy)


if __name__ == '__main__':
    unittest.main()
