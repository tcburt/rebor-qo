import unittest
import CCqo102_ring_damping

class TestCCqo102(unittest.TestCase):

    def setUp(self):
        self.couplings = [12.0, 20.0]
        self.velocities = [3.0, 4.0]

    
    def test_SingleC_SingleV_damping(self):
        [damping, path_losses] = CCqo102_ring_damping.calc_ring_damping(self.couplings[0], 
                                                                        self.velocities[0])
        self.assertEqual(damping, 24.)

    def test_SingleC_SingleV_losses(self):
        [damping, path_losses] = CCqo102_ring_damping.calc_ring_damping(self.couplings[0], 
                                                                        self.velocities[0])
        self.assertEqual(path_losses, 24.)

    def test_SingleC_MultiVs_damping(self):
        [damping, path_losses] = CCqo102_ring_damping.calc_ring_damping(self.couplings[0], 
                                                                        self.velocities)
        self.assertEqual(damping, 42.)

    def test_SingleC_MultiVs_losses(self):
        [damping, path_losses] = CCqo102_ring_damping.calc_ring_damping(self.couplings[0], 
                                                                        self.velocities)
        self.assertListEqual(path_losses.tolist(), [24., 18.])

    def test_MultiCs_SingleV_damping(self):
        [damping, path_losses] = CCqo102_ring_damping.calc_ring_damping(self.couplings, 
                                                                        self.velocities[1])
        self.assertEqual(damping, 68.)

    def test_MultiCs_SingleV_losses(self):
        [damping, path_losses] = CCqo102_ring_damping.calc_ring_damping(self.couplings, 
                                                                        self.velocities[1])
        self.assertListEqual(path_losses.tolist(), [18., 50.])

    def test_MultiCs_MultiVs_damping(self):
        [damping, path_losses] = CCqo102_ring_damping.calc_ring_damping(self.couplings, 
                                                                        self.velocities)
        self.assertEqual(damping, 74.)

    def test_MultiCs_MultiVs_losses(self):
        [damping, path_losses] = CCqo102_ring_damping.calc_ring_damping(self.couplings, 
                                                                        self.velocities)
        self.assertListEqual(path_losses.tolist(), [24., 50.])

suite = unittest.TestLoader().loadTestsFromTestCase(TestCCqo102)
unittest.TextTestRunner(verbosity=2).run(suite)
