import unittest
from pathlib import Path
from agents import analyze
class Tests(unittest.TestCase):
    def setUp(self):self.source=(Path(__file__).resolve().parents[1]/'sample.csv').read_text()
    def test_demo(self):
        r=analyze(self.source);self.assertEqual(r['total_vehicles'],630);self.assertEqual(r['routes'][0]['route'],'Riverside corridor')
    def test_signal_budget(self):
        p=analyze(self.source)['signals'][0];self.assertAlmostEqual(sum(x['green_seconds'] for x in p['phases'])+p['assumed_lost_seconds'],90);self.assertTrue(all(x['green_seconds']>=10 for x in p['phases']))
    def test_context(self):
        self.assertGreater(analyze(self.source,'rain',20)['traffic'][0]['load_proxy'],analyze(self.source)['traffic'][0]['load_proxy'])
    def test_invalid(self):
        for source in ('',self.source.replace(',240,15',',-1,15'),self.source.replace(',240,15',',240,0')):
            with self.assertRaises(ValueError):analyze(source)
    def test_short_cycle(self):
        with self.assertRaises(ValueError):analyze(self.source,cycle=40)
    def test_bad_context(self):
        with self.assertRaises(ValueError):analyze(self.source,event=101)
if __name__=='__main__':unittest.main()
