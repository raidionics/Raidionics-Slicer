from slicer.ScriptedLoadableModule import *
import logging

#import configparser
try:
    import configparser
except:
    slicer.util.pip_install('configparser')
    import configparser
import Queue
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
from src.DeepSintefLogic import *
from src.gui.DeepSintefWidget import *

"""
DeepSintef is based upon the DeepInfer code (available at https://github.com/DeepInfer/Slicer-DeepInfer)
"""


class DeepSintef(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "DeepSintef"
    self.parent.categories = ["Machine Learning"]
    self.parent.dependencies = []
    self.parent.contributors = ["David Bouget (SINTEF)"]
    self.parent.helpText = """
    This is a plugin developped by SINTEF MedTek, allowing users to run pre-trained models on neuro and mediastinum
    data."""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
    This plugin is based upon the DeepInfer plugin (available at https://github.com/DeepInfer/Slicer-DeepInfer), 
    originally developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc.. """
