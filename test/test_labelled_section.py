import unittest
from geometry import Point, Quaternion, Transformation
import flightanalysis.schedule.p21 as sched
from flightanalysis.section import LabelledSection
import numpy as np
import pandas as pd

class TestLabelledSection(unittest.TestCase):
    def test_from_manoeuvre(self):

        man = LabelledSection.from_manoeuvre(
            transform=Transformation(
                Point(0, 0, 0), Quaternion.from_euler(Point(np.pi, 0, np.pi))
            ),
            manoeuvre=sched.p21.manoeuvres[0],
            scale=200.0
        )

        self.assertEqual(len(man.labels),5)


        #pd.testing.assert_frame_equal(man.labels[0].data, man.section.data.iloc[0:len(man.labels[0].data)])
    
    def test_from_schedule(self):
        schedule = LabelledSection.from_schedule(
            schedule=sched.p21,
            enter_from = "left",
            distance=170.0
        )

        self.assertEqual(len(schedule.labels),17)
        self.assertEqual(len(schedule[0].labels),5)
        