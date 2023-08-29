from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import argparse
import scipy.stats as stats
from dataclasses import dataclass


class ImageStats:
    def __init__(self):
        self.peak_index = -1
        self.peak_val = float('-inf')
        self.mean_val= float('-inf')
        self.peak_metric = float('inf')
        self.sym_metric = 0.0

    def __str__(self):
        s = f"peak index={self.peak_index} peak_val={self.peak_val} mean_val={self.mean_val} peak_metric={self.peak_metric} sym_metric={self.sym_metric}"
        return s
        

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", type=Path, help="path to image")
    parser.add_argument("-p", "--plot", action="store_true", default=False, help="plot stuff")
    return parser.parse_args()

def calc_image_cumulants(img_name):
    image = Image.open(img_name).convert('L')
    resized_img = image.resize((100, 100))

    # normalize
    mean = np.mean(resized_img)
    std = np.std(resized_img)
    norm_img = (resized_img -  mean) / std
    
    sum_x = np.sum(norm_img, axis=1)  # sum across col (horizontally)
    sum_y = np.sum(norm_img, axis=0) # sum down rows (vertically)
    return norm_img, sum_x, sum_y

def plot_data(x, fname='data'):
    if len(x.shape)==2:
        ax1 = plt.subplot(111)
        ax1.imshow(x, cmap='gray')
    elif len(x.shape)==1:
        ax1 = plt.subplot(111)
        ax1.plot(x)
        ax1.plot(x,'o')
    ax1.set_title(fname)
    plt.show()
    
def plot_stats(fname, img, sum_x, sum_y):

    if len(str(fname)) > 30:
        fname_title=str(fname)[-30:]
    else:
        fname_title=fname
    #
    
    # Display the grayscale image
    ax1 = plt.subplot2grid((6,8), (0,1), colspan=4, rowspan=4)  # grid needs to have 8 cols so that sharex works
    ax2 = plt.subplot2grid((6,8), (4,1), colspan=4, rowspan=2)
    ax3 = plt.subplot2grid((6,8), (0,5), colspan=2, rowspan=4)
    ax2.sharex(ax1)
    ax3.sharey(ax1)

    ax1.imshow(img, cmap='gray')
    ax1.set_title(fname_title)

    ax2.bar(range(len(sum_y)), sum_y)
    #ax2.set_title('cumulant over rows')
    #ax2.set_xlabel('col')

    
    # ax1.set_xlim(ax2.get_xlim())
    # ax2.set_xlim(ax1.get_xlim())
    
    # Plot the vertical histogram
    # ax3 = plt.subplot2grid((6,6), (0,0), colspan=1, rowspan=4, sharey=ax1)
    ax3.barh(range(len(sum_x)),sum_x)
    ax3.set_title('cumulant over cols')
    #ax3.set_ylabel('row')


    # Adjust the spacing and show the plots
    plt.tight_layout()
    plt.show()

def calc_symmetry_metric(x):
    #
    #  < 0: skews left
    # == 0: perfectly symmetric
    #  > 0: skews right
    #
    assert len(x) % 2==1  # odd length window
    mid = int(len(x)/2)
    xleft = x[0:mid+1]; print(len(xleft))
    meanleft = np.mean(xleft)

    xright = x[mid:];print(len(xright))
    meanright = np.mean(xright)

    assert len(xright)==len(xleft)

    diff = meanright - meanleft
    print(f"meanleft={meanleft}, {meanright}, diff={meanright - meanleft}")
    return diff

def calc_peakiness_metric(x):
    # peakiness = standard deviation
    # smaller value -> sharper peak
    std = np.std(x)
    return std
    
def find_peak_index(x, start_index, stop_index):
    max_val = -999
    max_indx = -1
    for n in range(start_index,stop_index):
        if x[n] > max_val:
            max_val = x[n]
            max_indx = n
        #
    #
    mean_val = np.mean(x[start_index:stop_index])
    return max_indx, max_val, mean_val

def is_valid_peak(indx, max_val, mean_val):
    if indx < 20 or indx > 80:
        return False
    if max_val - mean_val < 50:
        return False
    else:
        return True

def knob_is_off(sum_x, sum_y):
    THRESH_PEAKINESS_METRIC = 50.0
    THRESH_SYMMETRY_METRIC = 0.0
    
    knob_stats = ImageStats()
    knob_stats.peak_index, knob_stats.peak_val, knob_stats.mean_val = find_peak_index(sum_y, 20, 80)

    #
    # there's a definite peak
    if is_valid_peak(knob_stats.peak_index, knob_stats.peak_val, knob_stats.mean_val)==False:
        return False, knob_stats

    # extract window
    start_indx = knob_stats.peak_index - 10
    if start_indx < 0:
        start_indx = 0
    stop_indx = start_indx + 21
    assert stop_indx < len(sum_y)
    win = sum_y[start_indx:stop_indx]
    assert len(win) % 2 == 1    # it's odd length
    
    # the peak is peaky
    knob_stats.peak_metric = calc_peakiness_metric(win)
    if knob_stats.peak_metric > THRESH_PEAKINESS_METRIC:
        return False, knob_stats
    #

    # the peak is skewed right
    knob_stats.sym_metric = calc_symmetry_metric(win)
    if knob_stats.sym_metric < THRESH_SYMMETRY_METRIC:
        return False, knob_stats

    return True, knob_stats

    
# def print_report(image_path, is_off, knob_stats):
#     if len(str(image_path)) > 15:
#         fname = str(image_path)[-15:]
#     else:
#         fname = str(image_path)
#     #
#     print(f"{fname:15s} {knob_stats.peak_index:4d} {knob_stats.peak_value:4.3f} {knob_stats.mean_val:4.3f} {str(is_off):6s}")
    
    
if __name__=="__main__":
    args = parse_args()
    img_bw, sum_x, sum_y = calc_image_cumulants(args.image_path)
    is_off, knob_stats = knob_is_off(sum_x, sum_y)
    print(str(knob_stats))
    #print_report(args.image_path, is_off, stats)
    if args.plot:
        plot_stats(args.image_path, img_bw, sum_x, sum_y)
    
