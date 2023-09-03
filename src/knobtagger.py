from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import argparse
import scipy.stats as stats
from dataclasses import dataclass
import sys
import shutil
import math

class StatsLogger:
    def __init__(self):
        self.samples = []

    def log(self, x):
        if math.isinf(x)==False:
            self.samples.append(x)

    def get_stats(self, title='statistics'):
        histogram, bins = np.histogram(self.samples)
        mean = np.mean(self.samples)
        std = np.std(self.samples)
        # plt.hist(self.samples, bins='auto')
        # plt.xlabel('Values')
        # plt.ylabel('Frequency')
        # plt.title('Histogram of X Values')
        # plt.show()

        plt.bar(bins[:-1], histogram, width=np.diff(bins), align='edge')
        plt.axvline(mean, color='r', linestyle='--', label=f'{mean:6.2f}')
        plt.axvline(mean + std, color='g', linestyle='--', label=f'mean + {std:6.2f} = {mean + std:6.2f}')
        plt.axvline(mean - std, color='g', linestyle='--', label=f'mean - {std:6.2f} = {mean - std:6.2f}')
        
        plt.xlabel('Bins')
        plt.ylabel('Frequency')
        plt.title(f'Histogram {title}')
        plt.legend()
        plt.show()
        return histogram, mean, std


class ImageStats:
    def __init__(self):
        self.peak_index = -1
        self.peak_val = float('-inf')
        self.mean_val= float('-inf')
        self.peak_metric = float('-inf')
        self.sym_metric = float('-inf')

    def __str__(self):
        s = f"peak index={self.peak_index} peak_val={self.peak_val} mean_val={self.mean_val} peak_metric={self.peak_metric} sym_metric={self.sym_metric}"
        return s
        

def parse_args():
    DEFAULT_PEAK_DELTA=50
    DEFAULT_PEAK_METRIC=50.0
    DEFAULT_SKEW_METRIC=20.0
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", type=Path, help="path to image")
    parser.add_argument("-d", "--disp", action="store_true", default=False, help="display/plot stuff")
    parser.add_argument("-q", "--peak_delta_thresh",
                        type=float,
                        default=DEFAULT_PEAK_DELTA,
                        help=f"peak delta threshold; default {DEFAULT_PEAK_DELTA}")
    parser.add_argument("-r", "--pmetric_thresh",
                        type=float,
                        default=DEFAULT_PEAK_METRIC,
                        help=f"peakiness metric threshold; default {DEFAULT_PEAK_METRIC}")
    parser.add_argument("-s", "--skew_thresh",
                        type=float,
                        default=DEFAULT_SKEW_METRIC,
                        help=f"peakiness metric threshold; default {DEFAULT_SKEW_METRIC}")
    parser.add_argument("--all_off",
                        action="store_true",
                        default=
                        False,
                        help="override: classify all images as OFF")
                        
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
    xleft = x[0:mid+1]
    meanleft = np.mean(xleft)

    xright = x[mid:]
    meanright = np.mean(xright)

    assert len(xright)==len(xleft)

    diff = meanright - meanleft
    #print(f"meanleft={meanleft}, {meanright}, diff={meanright - meanleft}")
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

def is_valid_peak(indx, max_val, mean_val, thresh):
    if indx < 20 or indx > 80:
        return False
    if max_val - mean_val < thresh:
        return False
    else:
        return True

def knob_is_off(sum_x, sum_y, peak_delta_thresh, pmetric_thresh, skew_thresh):
    
    knob_stats = ImageStats()
    knob_stats.peak_index, knob_stats.peak_val, knob_stats.mean_val = find_peak_index(sum_y, 20, 80)

    #
    # there's a definite peak
    valid_flag = is_valid_peak(knob_stats.peak_index,
                               knob_stats.peak_val,
                               knob_stats.mean_val,
                               peak_delta_thresh)
    if valid_flag==False:
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
    knob_stats.sym_metric = calc_symmetry_metric(win)

    if knob_stats.peak_metric > pmetric_thresh:
        return False, knob_stats
    #

    # the peak is skewed right
    if knob_stats.sym_metric < skew_thresh:
        return False, knob_stats

    return True, knob_stats

    
# def print_report(image_path, is_off, knob_stats):
#     if len(str(image_path)) > 15:
#         fname = str(image_path)[-15:]
#     else:
#         fname = str(image_path)
#     #
#     print(f"{fname:15s} {knob_stats.peak_index:4d} {knob_stats.peak_value:4.3f} {knob_stats.mean_val:4.3f} {str(is_off):6s}")

def find_img_files(image_dir):
    """
    return list of img files
    """
    assert image_dir.is_dir()
    png_files = list(image_dir.glob('*-b[0-9][0-9].png'))
    img_l = sorted(png_files)
    return img_l


def print_header():
    s  = f"| {'filename':30s} "
    s += f"| {'PI':4s} "
    s += f"| {'PDelta':8s} "
    s += f"| {'peakM':8s} "
    s += f"| {'symm':8s} "
    s += f"| {'stove_state':12s} |"
    print(s)
    
def print_img_summary(img_fname, knob_stats, is_off):
    def float_or_inf(f):
        if f==float('-inf'):
            s = 8 * ' '
        else:
            s = f"{f:8.3f}"
        return s
        
    s =  f"| {str(img_fname)[-30:]:30s} "
    s += f"| {knob_stats.peak_index:4d} " 
    s += f"| {knob_stats.peak_val - knob_stats.mean_val:8.3f} " 
    s += f"| {float_or_inf(knob_stats.peak_metric):8s} " 
    s += f"| {float_or_inf(knob_stats.sym_metric):8s} " 
    #s += f"| {str(is_off):8s} |"
    stove_state = "off" if is_off else "STOVE ON"
    s += f"| {stove_state:12s} |"
    
    print(s)

def delete_dest_dir(image_path):
    dest_path =  Path("../data/out-knobtagger")
    if image_path.is_file():
        dest_path = dest_path / image_path.parts[-3] / image_path.parts[-2]
    else:
        dest_path = dest_path / image_path.parts[-2] / image_path.parts[-1]
    #
    try:
        shutil.rmtree(dest_path)
    except FileNotFoundError:
        pass
    
    
def copy_file(img_fname, is_off):
    """
    copy file to either .../on/fname or .../off/fname
    """
    dest_path =  Path("../data/out-knobtagger")
    dest_path = dest_path / img_fname.parts[-3] / img_fname.parts[-2]   # the last directory element
    dest_on  = dest_path / "on" / img_fname.name
    dest_off = dest_path / "off"  / img_fname.name

    dest_on.parent.mkdir(exist_ok=True, parents=True)
    dest_off.parent.mkdir(exist_ok=True, parents=True)

    if is_off:
        shutil.copy(img_fname, dest_off)
    else:
        shutil.copy(img_fname, dest_on)

def collect_stats(knob_stats, log_peak_diff, log_peakiness, log_symmetry):
    log_peak_diff.log(knob_stats.peak_val - knob_stats.mean_val)
    log_peakiness.log(knob_stats.peak_metric)
    log_symmetry.log(knob_stats.sym_metric)
    return log_peak_diff, log_peakiness, log_symmetry
    
        
def classify_knobs(image_path,
                   peak_delta_thresh,
                   pmetric_thresh,
                   skew_thresh,
                   all_off_flag=False):
    if image_path.is_file():
        files_l = [image_path]
    else:
        assert image_path.is_dir()
        files_l = find_img_files(image_path)
    #

    log_peak_diff = StatsLogger()
    log_peakiness = StatsLogger()
    log_symmetry = StatsLogger()
    
    delete_dest_dir(image_path)
    print_header()
    for img_fname in files_l:
        img_bw, sum_x, sum_y = calc_image_cumulants(img_fname)
        is_off, knob_stats = knob_is_off(sum_x,
                                         sum_y,
                                         peak_delta_thresh,
                                         pmetric_thresh,
                                         skew_thresh)
        if all_off_flag==True:
            #override automatic classification
            is_off=True
        #

        print_img_summary(img_fname, knob_stats, is_off)

        if args.disp:
            plot_stats(img_fname, img_bw, sum_x, sum_y)
        #
        copy_file(img_fname, is_off)

        log_peak_diff, log_peakiness, log_symmetry = collect_stats(knob_stats,
                                                                   log_peak_diff,
                                                                   log_peakiness,
                                                                   log_symmetry)
    #

    if len(files_l) > 1 and args.disp:
        log_peak_diff.get_stats(title='peak diff')
        log_peakiness.get_stats(title='peakiness')
        log_symmetry.get_stats(title='symmetry')
    #

    
if __name__=="__main__":
    args = parse_args()
    classify_knobs(args.image_path,
                   args.peak_delta_thresh,
                   args.pmetric_thresh,
                   args.skew_thresh,
                   all_off_flag= args.all_off)
    
