"""This is the main file for annotation of depth files

Copyright 2016 Markus Oberweger, ICG,
Graz University of Technology <oberweger@icg.tugraz.at>

This file is part of SemiAutoAnno.

SemiAutoAnno is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SemiAutoAnno is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SemiAutoAnno.  If not, see <http://www.gnu.org/licenses/>.
"""

import getopt
import numpy
import os
import sys
import pwd
from PyQt4.QtGui import QApplication
from data.importers import IntelImporter
from util.handconstraints import IntelHandConstraints
from util.handpose_evaluation import IntelHandposeEvaluation
from util.interactivedatasetlabeling import InteractiveDatasetLabeling

__author__ = "Markus Oberweger <oberweger@icg.tugraz.at>"
__copyright__ = "Copyright 2016, ICG, Graz University of Technology, Austria"
__credits__ = ["Markus Oberweger"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Markus Oberweger"
__email__ = "oberweger@icg.tugraz.at"
__status__ = "Development"


if __name__ == '__main__':
    person = None
    username = None
    start_idx = None
    try:
        opts, args = getopt.getopt(sys.argv, "hs:p:u:", ["person=", "start_idx=", "username="])
    except getopt.GetoptError:
        print('main_labeling_pose.py -p <person> -s <start_idx> -u <username>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('main_labeling_pose.py -p <person> -s <start_idx> -u <username>')
            sys.exit()
        elif opt in ("-p", "--person"):
            person = arg.lower()
        elif opt in ("-u", "--username"):
            username = arg.lower()
        elif opt in ("-s", "--start_idx"):
            start_idx = int(arg)

    if person is None:
        print('Person must be specified: -p <person> or enter now:')
        person = 'test_seq2'
        if len(person.strip()) == 0:
            sys.exit(2)
    else:
        print('Person is {}'.format(person))

    if username is None:
        print('Username must be specified: -u <username> or enter now:')
        username = input().lower()
        if len(username.strip()) == 0:
            sys.exit(2)
    else:
        print('Username is {}'.format(username))

    if start_idx is None:
        print('Start frame index can be specified: -s <start_idx> or enter now:')
        start_idx = input().lower()
        if len(start_idx.strip()) == 0:
            start_idx = 0
        else:
            start_idx = int(start_idx)
    else:
        print('Start frame index is {}'.format(start_idx))

    rng = numpy.random.RandomState(23455)

    # subset to label
    subset_idxs = []

    if person == 'test_seq2':
        di = IntelImporter('/home/boonyew/Documents/semi-auto-anno-master/semi-auto-anno/data/intel/', useCache=False)
        Seq2 = di.loadSequence(person, shuffle=False)
        hc = IntelHandConstraints([Seq2.name])
        hpe = IntelHandposeEvaluation([j.gt3Dorig for j in Seq2.data], [j.gt3Dorig for j in Seq2.data])
        for idx, seq in enumerate(Seq2.data):
            ed = {'vis': [], 'pb': {'pb': [], 'pbp': []}}
            Seq2.data[idx] = seq._replace(gtorig=numpy.zeros_like(seq.gtorig), extraData=ed)

        # common subset for all
        subset_idxs = [25,30,35,45,50,55,60,65]
    else:
        raise NotImplementedError("")

    replace_off = 0
    replace_file = None  # './params_tracking.npz'

    output_path = di.basepath

    filename_joints = output_path+person+'/joint_'+username+'.txt'
    filename_pb = output_path+person+'/pb_'+username+'.txt'
    filename_vis = output_path+person+'/vis_'+username+'.txt'
    filename_log = output_path+person+'/annotool_log_'+username+'.txt'

    # create empty file
    if not os.path.exists(filename_joints):
        annoFile = open(filename_joints, "w")
        annoFile.close()
    else:
        bak = filename_joints+'.bak'
        i = 0
        while os.path.exists(bak):
            bak = filename_joints+'.bak.{}'.format(i)
            i += 1
        os.popen('cp '+filename_joints+' '+bak)

    if not os.path.exists(filename_pb):
        annoFile = open(filename_pb, "w")
        annoFile.close()
    else:
        bak = filename_pb+'.bak'
        i = 0
        while os.path.exists(bak):
            bak = filename_pb+'.bak.{}'.format(i)
            i += 1
        os.popen('cp '+filename_pb+' '+bak)

    if not os.path.exists(filename_vis):
        annoFile = open(filename_vis, "w")
        annoFile.close()
    else:
        bak = filename_vis+'.bak'
        i = 0
        while os.path.exists(bak):
            bak = filename_vis+'.bak.{}'.format(i)
            i += 1
        os.popen('cp '+filename_vis+' '+bak)

    app = QApplication(sys.argv)
    browser = InteractiveDatasetLabeling(Seq2, hpe, di, hc, filename_joints, filename_pb, filename_vis, filename_log,
                                         subset_idxs, start_idx, replace_file, replace_off)
    browser.show()
    app.exec_()
    print(browser.curData, browser.curVis, browser.curPb, browser.curPbP, browser.curCorrected)

