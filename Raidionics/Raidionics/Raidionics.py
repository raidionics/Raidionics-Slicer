from slicer.ScriptedLoadableModule import *
import logging
import json
import platform
import os
import numpy
import re
import subprocess
import shutil
import threading
from collections import OrderedDict
from glob import glob
from time import sleep
from copy import deepcopy
from __main__ import qt, ctk, slicer, vtk

import SimpleITK as sitk
import sitkUtils
from src.RaidionicsLogic import *
from src.gui.RaidionicsWidget import *


class Raidionics(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Raidionics"
    self.parent.categories = ["Machine Learning"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Bouget (Medical Technology, SINTEF Digital) david.bouget@sintef.no"]
    self.parent.helpText = """
    The Raidionics plugin for 3D Slicer allows users to run pre-trained models for segmentation and standardized
    reporting (RADS) over MRI volumes for patients diagnosed with brain cancer, and CT volumes for patients diagnosed 
    with lung cancer.
    The plugin has been developed in the Medical Technology group, Health Research Department, SINTEF Digital.
    """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
    This plugin is based upon the DeepInfer plugin (available at https://github.com/DeepInfer/Slicer-DeepInfer), 
    originally developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc.. """
