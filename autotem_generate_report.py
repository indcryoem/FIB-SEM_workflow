#!/usr/bin/env python3

# ===================================================================
# Name:		autotem_generate_report.py
# Purpose:	Generates report from AutoTEM job during FIB milling session. 
#		More information: Check tutorial.pdf
# Author:	Arthur Melo
# Created:	2023/08/18
# Version:	alpha_v00
# Last Change:	
# ===================================================================    

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import scipy as sc
import subprocess
import argparse

from skimage import io
from matplotlib.backends.backend_pdf import PdfPages

parser = argparse.ArgumentParser("autotem_generate_report.py")
parser.add_argument("-i",dest="input_autotem_project", help="AutoTEM project folder", type=str)
args = parser.parse_args()

autotem_project=args.input_autotem_project

#get autotem structure
autotem_abs_path = os.path.abspath(autotem_project)
autotem_sites = autotem_abs_path + '/Sites'

#get lamella sites
lamella = [name for name in os.listdir(autotem_sites) if os.path.isdir(os.path.join(autotem_sites, name))]
lamella_dir=sorted(lamella)

#generate empty image
img_empty = np.zeros([30,50,3],dtype=np.uint8)
img_empty.fill(255)

pdf_pages = PdfPages(autotem_project + '_report.pdf')
fig, axes = plt.subplots(len(lamella_dir), 4, figsize=(20, 5 * len(lamella_dir)))

for n,L in enumerate(lamella_dir):
    #Eucentric Tilt images
    eucentric_tilt_images = '{}/{}/EucentricTiltImages'.format(autotem_sites,L)
    if os.path.isdir(eucentric_tilt_images):
        euc_img_list = sorted(os.listdir(eucentric_tilt_images))
        if np.size(euc_img_list) > 3:
            euc_img = '{}/{}'.format(eucentric_tilt_images,euc_img_list[-3])
            euimg = io.imread(euc_img)
        else:
            print("not enough eucentricity images")
            euimg = img_empty
            
    else:
        print(eucentric_tilt_images + " doesn't exist")
       
    #PrecisePositioningLogImages
    PPLI = '{}/{}/PrecisePositioningLogImages'.format(autotem_sites,L)
    if os.path.isdir(PPLI):
        PPLI_img_list = sorted(os.listdir(PPLI))
        StressReliefCuts_files = [filename for filename in PPLI_img_list if 'Stress-Relief-Cuts-match-information' in filename]
        if np.size(StressReliefCuts_files) >= 1:
            StressReliefCuts_img = '{}/{}'.format(PPLI,StressReliefCuts_files[-1])
            SRCimg = io.imread(StressReliefCuts_img)
        else: 
            print("not enough StressReliefCuts files")
            SRCimg = img_empty
    else:
        print(PPLI + " doesn't exist")
        
    
    #Lamella evaluation images
    lamella_evaluation_img = '{}/{}/LamellaEvaluationImages'.format(autotem_sites,L)
    if os.path.isdir(lamella_evaluation_img):
        img_list = sorted(os.listdir(lamella_evaluation_img))
        ion_img = '{}/{}'.format(lamella_evaluation_img,img_list[-2])
        electron_img = '{}/{}'.format(lamella_evaluation_img,img_list[-1])
        eimg = io.imread(electron_img)
        iimg = io.imread(ion_img)
    else:
        print(lamella_evaluation_img + " doesn't exist")
        eimg = img_empty
        iimg = img_empty

    
    #get class name
    ax_row = axes[n]
    ax_row[0].set_title( L + " - Eucentric Tilt")
    ax_row[0].imshow(euimg, cmap='gray')
    ax_row[1].set_title( L + " - Milling Image")
    ax_row[1].imshow(SRCimg, cmap='gray')
    ax_row[2].set_title( L + " - Ion Image")
    ax_row[2].imshow(iimg, cmap='gray')
    ax_row[3].set_title(L + " - Electron Image")
    ax_row[3].imshow(eimg, cmap='gray')

plt.tight_layout()
# Save the figure to the PDF file
pdf_pages.savefig(fig)
# Close the PdfPages object
pdf_pages.close()
