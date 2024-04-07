import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
from PIL import Image
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from .s3_utils import create_s3_client
import math as mth


def viz_overhead(nvp_x_cartesian, nvp_y_cartesian, eye_height_full, eye_point_full, vru_selected):
    '''
    Takes NVPs, vehicle measurements, and VRU. Plots overhead view of blind zone 
      with nearest forward-visible VRU. Saves the figure as an SVG and returns fig
       for viewing, if desired.

    Takes inputs:
    vp_x_cartesian = np.array([nums])
    nvp_y_cartesian = np.array([nums])
    eye_height_full = num # eye height calculated from interpolated seat-ground + 
      human eye point on seat (in)
    eye_point_full = num # interpolated front-of-hood to eye distance 
      interpolated (in)
    vru_selected = num # options: 1=toddler, 2=elementary, 3=elem_bike, 
      4=wheelchair, 5=adult_bike, 6=adult

    *np.array requires importing the numpy library (import numpy as np)
    '''
    #  FOR TESTING
    nvp_x_cartesian = np.array([-5744, -5744, -5744, -5744, -5744, -5744, -5744, -5744, -5744, -5744, -5744, -10414, 5782, 5782, 5782, 5782, 5782, 5782, 5782, 5782, 5782, 5782, 5782, 5782, 5782, 5782, -2741, -2741, -3670, -10627, -10627, -10627, -10627, -10627, -10627, -10627, -10627, -10627, -5518, -5518, -5518, -5518, -5518, -5518, -5518, -5518, -5518, -5518, -5949, -5949, 25447, 25447, 1604, 1604, 1570, 1570, 1570,
                               1570, 1657, 1657, 1657, 1657, 1657, 1657, 1657, 1657, 1657, 1657, 1508, 1508, 1508, 1663, 1663, 1663, 2556, 2079, 2079, 1562, 1012, 1012, 1012, 1012, 1012, 863, 803, 1080, 787, 787, 787, 693, 693, 1028, 1028, 1028, 1028, 445, 445, 445, 445, 354, 283, 283, 283, 283, 283, 114, 114, 114, 114, 17, 17, 17, -207, -207, -207, -207, -207, -433, -433, -433, -433, -554, -383, -383, -383, -579, -579, -579, -579, -579])
    nvp_y_cartesian = np.array([1841, 1841, 1841, 1841, 1841, 1841, 1841, 1841, 1841, 1841, 1841, 2509, -606, -606, -606, -606, -606, -606, -606, -606, -606, -606, -606, -606, -606, -606, 24, 24, -693, -3284, -3284, -3284, -3284, -3284, -3284, -3284, -3284, -3284, -2496, -2496, -2496, -2496, -2496, -2496, -2496, -2496, -2496, -2496, -3223, -3223, 16112, 16112, 1035, 1035, 1156, 1156, 1156, 1156, 1642, 1642, 1642,
                               1642, 1642, 1642, 1642, 1642, 1642, 1642, 1667, 1667, 1667, 2073, 2073, 2073, 3310, 2948, 2948, 2627, 1724, 1724, 1724, 1724, 1724, 1615, 1621, 2253, 1825, 1825, 1825, 1823, 1823, 3214, 3214, 3214, 3214, 1893, 1893, 1893, 1893, 1874, 1948, 1948, 1948, 1948, 1948, 1869, 1869, 1869, 1869, 1852, 1852, 1852, 2463, 2463, 2463, 2463, 2463, 3188, 3188, 3188, 3188, 3138, 1787, 1787, 1787, 1788, 1788, 1788, 1788, 1788])
    # eye height calculated from interpolated seat-ground + human eye point on seat (in)
    eye_height_full = 60
    # interpolated front-of-hood to eye distance interpolated (in)
    eye_point_full = 84

    # VRU sizes (taken fron VIEW 1.0)
    # 'toddler', 'elementary', 'elem_bike', 'wheelchair', 'adult_bike', 'adult'
    # shoulder height, width, person height (all in [in])
    # DOESN'T CONTAIN DEPTH, BUT ASSUMES THAT BICYCLES ARE 4X DEPTH OF PEOPLE AND IGNORES WHEELCHAIRS?
    vru_label = ['toddler', 'elementary school child', 'elementary schooler on bike',
                 'wheelchair user', 'adult on bike', 'adult']
    vru_sizes = np.array([[28, 9, 34], [37, 12, 45], [35, 12, 45], [
                         39, 26, 49], [47, 16, 58], [49, 16, 60]])
    # store 'shoulder height' of selected VRU in [ft]
    vru_height = vru_sizes[vru_selected-1, 0]/12
    # store 'width' of selected VRU in [ft]
    vru_width = vru_sizes[vru_selected-1, 1]/12

    max_distance = 7*15  # maximum distance plotted (multiple of 7)

    # start and end angles for plotting [deg]
    plot_start = -20
    plot_end = 200

    # background colors (make sure to have the same number of colors as plot divisions)
    greenBG = ['#143A1D', '#1A5A2D', '#1F723A',
               '#429344', '#7CBC55', '#A6C991', '#CAE4BB']

    ''' -------------------------
  Begin initial data processing
  --------------------------'''
    # convert from [cm] to [ft]
    nvp_x_cartesian_ft = np.asarray(nvp_x_cartesian)*0.032808399
    nvp_y_cartesian_ft = np.asarray(nvp_y_cartesian)*0.032808399

    # convert to polar coordinate system
    r = np.sqrt(np.square(nvp_x_cartesian_ft) + np.square(nvp_y_cartesian_ft))
    theta = np.arctan2(nvp_y_cartesian_ft, nvp_x_cartesian_ft)

    # remove erroneous data (pillars)
    to_keep = r <= 800
    r = r[to_keep]
    theta = theta[to_keep]

    '''# remove data outside of plotting angle boundaries
    to_keep = theta <= mth.radians(plot_end)
    theta = theta[to_keep]
    r = r[to_keep]
    to_keep = theta >= mth.radians(plot_start)
    theta = theta[to_keep]
    r = r[to_keep]'''

    # sort data from smallest to largest theta value ('untwist') (WIP)
    idx = np.argsort(theta)  # find indices that would sort the array
    r_sorted = np.array(r)[idx]
    theta_sorted = np.array(theta)[idx]
    ''' -----------------------
  End initial data processing
  ------------------------'''

    # set figure size (check as regular script since notebooks don't work the same way)
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig, ax = plt.subplots(
        subplot_kw={'projection': 'polar'}, figsize=(800*px, 600*px))

    # plot background arcs
    for i in range(0, 7):
        colorBG = greenBG[i]
        ax.bar(np.pi/2, max_distance/7, width=mth.radians(plot_end-plot_start), bottom=i*max_distance/7,
               color=colorBG, edgecolor=colorBG, label='Visible Zone')  # 294 previously max(r)

    # plot NVPs
    ax.plot(theta_sorted, r_sorted, '#000', linewidth=0)
    ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
    # 65% opacity (a6) 404040bf is darker
    ax.fill(theta_sorted, r_sorted, '#5c5c5ca6', label='Blind Zone')

    ''' --------------------------------------
  Begin calculate NVPs for seeing vru_selected
  -----------------------------------------'''
    r_vru_nvp = np.empty(len(r_sorted))
    
    for i in range(len(theta_sorted)):
        # find sides of triangle from eye to ground
        b_eye = r_sorted[i] # length
        a_eye = eye_height_full # height
        c_eye = mth.sqrt(a_eye**2 + b_eye**2) # hypotenuse

        # find sides of similar triangle from vru to ground
        a_vru = vru_height # height
        c_vru = (a_vru*c_eye)/a_eye # hypotenuse (similar triangles)
        b_vru = mth.sqrt(a_vru**2 + c_vru**2) # length

        r_vru_nvp[i] =  b_eye-b_vru # find distance from eye to visible vru

    # plot effective NVP to vru
    ax.plot(theta_sorted, r_vru_nvp, '#2bb0e5', linewidth=1)
    ax.fill(theta_sorted, r_vru_nvp, '#2bb0e5a6', label='Blind Zone to VRU')
    ''' ------------------------------------
  End calculate NVPs for seeing vru_selected
  ---------------------------------------'''
    
    ''' ----------------------------------------------------------------
  Begin calculate minimum distance from hood to VRU in front of driver
  -----------------------------------------------------------------'''
    # store eye and hood data passed to function (convert to [ft])
    eye_height = eye_height_full/12
    hood_length = eye_point_full/12

    # store hood length in line with eye point in polar coordinates
    hood_r = hood_length
    hood_theta = np.pi/2  # 90 deg in rad

    # find nvp in front of driver (with tolerance)
    # b/w 89 and 90deg (taking ind0 since returns array inside variable)
    front_range_indices = np.where(np.logical_and(
        theta_sorted >= hood_theta-mth.radians(1), theta_sorted <= hood_theta+mth.radians(1)))[0]
    # find index of minimum of selected entries
    front_r_min_index = front_range_indices[np.argmin(
        r_sorted[front_range_indices])]
    front_r_min = r_sorted[front_r_min_index]
    front_theta_min = theta_sorted[front_r_min_index]

    # generate r values and heights b/w eye and closest NVP in increments of 1 VRU width
    # includes final r value to over- rather than under-estimate
    r_fit_nvp = np.arange(0, front_r_min+vru_width, vru_width)
    # generate height height values for each r value
    height_fit_nvp = np.linspace(eye_height, 0, len(r_fit_nvp))

    # remove nvp_fit data before hood_r
    to_keep = r_fit_nvp >= hood_r  # keep r values at least a hood's-distance away
    r_hood_nvp = r_fit_nvp[to_keep]
    height_hood_nvp = height_fit_nvp[to_keep]

    # find r values with height lower than vru height
    # store inds of all heights lower than vru height
    vru_fit_ind = np.where(height_hood_nvp < vru_height)[0]
    # store value of first r that meets the conditions above (absolute distance)
    r_vru_fit = r_hood_nvp[vru_fit_ind[0]]

    # minimum distance from HOOD to first visible VRU in front of driver (relative distance)
    front_vru_dist = r_vru_fit-hood_r  # [ft]

    # plot closest forward-visible VRU
    '''(theta might be slightly off but hopefully covered by dot size,
    distance is rounded since working in increments of 1 unit)'''
    ax.plot(hood_theta, r_vru_fit, '#2bb0e5', marker='o', markersize=5,
            linewidth=0, label='Closest Forward-Visible VRU')

    ''' NOT CURRENTLY IN USE, BUT COULD MAKE PLOT MORE INTERESTING
  # VRU arc
  ax.bar(np.pi/2, 2, width=np.pi/3, bottom=r_vru_fit,
         color='#2bb0e5', edgecolor='#2bb0e5', label='Visible VRU Arc')
  '''

    # note distance to closest visible VRU
    ax.text(0.05, 0.05, 'The closest forward-visible\n' + vru_label[vru_selected-1] + '\nis ' +
            str(round(front_vru_dist)) + 'ft in front of the vehicle',
            transform=ax.transAxes, fontsize=12, verticalalignment='center',
            bbox=dict(boxstyle='square', facecolor='#fff', alpha=0))
    graph_str = 'The closest forward-visible ' + \
        vru_label[vru_selected-1] + ' is ' + \
        str(round(front_vru_dist)) + 'ft in front of the vehicle'
    ''' --------------------------------------------------------------
  End calculate minimum distance from hood to VRU in front of driver
  ---------------------------------------------------------------'''

    # restrict angles of plot (switching min and max moves tick labels)
    ax.set_thetamin(plot_end)
    ax.set_thetamax(plot_start)

    # make plot axes match background divisions
    # generate markers range(0,round(max(r)),round(max(r)/7))
    tick_list = np.arange(0, max_distance+1, max_distance/7)
    ax.set_ylim(0, max_distance)  # [0,round(max(r))]
    plt.yticks(tick_list)  # range(0,round(max(r)),round(max(r)/7))

    ax.grid(True, color='#fff')
    ax.spines['polar'].set_visible(False)

    # plot car image
    image_file = "Vehicle-Overhead-09.png"
    # create s3 client to  access digital ocean space bucket for image
    s3_client = create_s3_client()

    # Get recently uploaded scan from the bucket
    response = s3_client.get_object(
        Bucket='vehicle-scans', Key=f'static/lidar/images/{image_file}')

    img = Image.open(response['Body'])
    # change image zoom based on vehicle size
    imagebox = OffsetImage(img, zoom=0.03)
    ab = AnnotationBbox(imagebox, (0, 0), frameon=False)
    ax.add_artist(ab)
    ax.patch.set_alpha(0)

    # shift plot over to the right by editing its bbox
    '''pos = ax.get_position()
    pos.x0 += .11  # increase value by 11% of figure sizw
    pos.x1 += .11  # must mach value for x0 for shift, otherwise it narrows the box
    ax.set_position(pos)'''

    # legend in bottom left corner of FIGURE, not PLOT
    #fig.legend(loc='lower left', fancybox=False)

    imgdata = StringIO()
    # save file as SVG
    # plt.savefig('/content/viz_overhead.svg', transparent=False, dpi='figure',
    #             pad_inches=0, facecolor='#fff', edgecolor='#5c5c5c')
    fig.savefig(imgdata, format='svg', transparent=False, dpi='figure',
                pad_inches=0, facecolor='#fff', edgecolor='#5c5c5c')

    imgdata.seek(0)

    data = imgdata.getvalue()

    return [data, graph_str]
