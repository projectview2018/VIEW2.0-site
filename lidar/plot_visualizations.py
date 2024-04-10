import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
from PIL import Image
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from .s3_utils import create_s3_client
import math as mth


def viz_overhead(nvp_x_cartesian, nvp_y_cartesian, eye_height_full, eye_point_full, eye_pos, vru_selected, vehicle):
    '''
    Takes NVPs, vehicle measurements, and VRU. Plots overhead view of blind zone
      with nearest forward-visible VRU. Saves the figure as an SVG and returns fig
       for viewing, if desired.

    Takes inputs:
    vp_x_cartesian = np.array([nums]) [cm]
    nvp_y_cartesian = np.array([nums]) [cm]
    eye_height_full = num # eye height calculated from interpolated seat-ground [m]
    eye_point_full = num # interpolated front-of-hood to eye distance
      interpolated [m]
    vru_selected = array # options: 1=toddler, 2=elementary, 3=elem_bike,
      4=wheelchair, 5=adult_bike, 6=adult

    *np.array requires importing the numpy library (import numpy as np)
    '''
    #  FOR TESTING
    # nvp_x_cartesian = np.array([185, 186, 186, 194, 195, 195, 195, 198, 197, 200, 200, 202, 202, 202, 202, 203, 203, 203, 203, 203, 204, 203, 203, 203, 203, 214, 214, 215, 216, 214, 211, 213, 210, 210, 210, 219, 220, 221, 219, 217, 216, 215, 224, 222, 221, 220, 215, 215, 225, 224, 221, 220, 216, 226, 222, 221, 218, 214, 222, 219, 217, 213, 220, 217,
    #                            212, 220, 216, 221, 216, 223, 232, 234, 234, 232, 232, 228, 235, 236, 228, 235, 228, 227, 225, 228, 229, 228, 225, 223, 225, 231, 228, 233, 237, 241, 247, 238, 239, 280, 272, 245, 236, 222, 203, 187, 170, 149, 116, 79, 57, 15, 1, -34, -61, -98, -124, -167, -190, -227, -263, -289, -313, -347, -382, -382, -430, -452, -483, -508, -536, -539])
    # nvp_y_cartesian = np.array([-22, -15, -15, -18, -14, -14, -14, -12, -10, -9, -9, -7, -7, -7, -7, -4, -4, -4, -3, -3, 0, 2, 2, 2, 5, 7, 7, 9, 10, 11, 8, 13, 8, 14, 15, 16, 18, 21, 20, 23, 23, 23, 25, 27, 28, 28, 31, 31, 33, 37, 36, 37, 38, 41, 42, 46, 44, 46, 48, 50, 52, 51, 52, 55, 59, 61, 61, 69,
    #                            67, 72, 77, 81, 81, 84, 90, 92, 94, 98, 104, 103, 107, 113, 120, 121, 132, 136, 141, 150, 153, 166, 172, 186, 202, 216, 235, 243, 265, 334, 351, 355, 356, 391, 411, 425, 450, 450, 474, 476, 474, 476, 474, 475, 474, 501, 500, 500, 498, 497, 494, 495, 494, 492, 491, 464, 460, 458, 456, 453, 453, 428])
    # eye height calculated from interpolated seat-ground + human eye point on seat [m]
    # eye_height_full = ((18.3-16.25)*0.0254)+1.2
    # interpolated front-of-hood to eye distance interpolated [m]
    # eye_point_full = ((84-70)+20.5)*0.0254
    height_percentile = "Nth-Percentile Female"
    # vru_selected = [1, 3]
    # plt.plot(nvp_x_cartesian, nvp_y_cartesian)
    # plt.show()
    # SHOULD BE UNCOMMENTED WHEN TESTING IS DONE
    # set true eye height (height of chair PLUS height of sitting person to eye) according to eye position
    height_percentile = ""
    if (eye_pos == 1):
        height_percentile = "5th-Percentile Female"
    elif (eye_pos == 2):
        height_percentile = "50th-Percentile Male"
    elif (eye_pos == 3):
        height_percentile = "95th-Percentile Male"
    else:
        height_percentile = "50th-Percentile Male"

    '''VRU sizes (taken fron VIEW 1.0)
      'pre-school', 'elem_bike', 'elementary', 'wheelchair', 'adult_bike', 'adult'
      shoulder height, width, person height (all in [in])
      DOESN'T CONTAIN DEPTH, BUT ASSUMES THAT BICYCLES ARE 4X DEPTH OF PEOPLE AND IGNORES WHEELCHAIRS?'''
    vru_label = ['pre-school child', 'elementary schooler on bike', 'elementary school child',
                 'wheelchair user', 'adult on bike', 'adult']
    vru_sizes = np.array([[28, 9, 34], [35, 12, 45], [37, 12, 45], [
                         39, 26, 49], [47, 16, 58], [49, 16, 60]])

    max_distance = 7*7  # maximum distance plotted (multiple of 7)

    # start and end angles for plotting [deg]
    plot_start = -20
    plot_end = 200

    # background colors (make sure to have the same number of colors as plot divisions)
    greenBG = ['#143A1D', '#1A5A2D', '#1F723A',
               '#429344', '#7CBC55', '#A6C991', '#CAE4BB']

    ''' -------------------------
  Begin initial data processing
  --------------------------'''
    # convert vehicle measurements from [m] to [ft]
    eye_height_full = eye_height_full*3.28084
    eye_point_full = eye_point_full*3.28084

    # convert NVP data from [cm] to [ft]
    nvp_x_cartesian_ft = np.asarray(nvp_x_cartesian)*0.032808399
    nvp_y_cartesian_ft = np.asarray(nvp_y_cartesian)*0.032808399

    # convert to polar coordinate system
    r = np.sqrt(np.square(nvp_x_cartesian_ft) + np.square(nvp_y_cartesian_ft))
    theta = np.arctan2(nvp_y_cartesian_ft, nvp_x_cartesian_ft)

    # remove erroneous data (pillars)
    to_keep = r <= max_distance
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
    '''idx = np.argsort(theta)  # find indices that would sort the array
    r_sorted = np.array(r)[idx]
    theta_sorted = np.array(theta)[idx]'''
    r_sorted = np.append(r,0)
    theta_sorted = np.append(theta,0)
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
               color=colorBG, edgecolor=colorBG, label='_Visible Zone')  # 294 previously max(r)

    # plot NVPs
    ax.plot(theta_sorted, r_sorted, '#404040',
            linewidth=0)
    ax.set_rlabel_position(-20)  # Move radial labels away from plotted line
    # 65% opacity (a6) 5c5c5ca6 is lighter bf
    ax.fill(theta_sorted, r_sorted, '#404040', label="ground blindzone")

    # set plot color options based on number of VRUs so ligher color is always on top
    if len(vru_selected) == 2:
      vru_plot_colors = ['#A34D9D', '#A6DDE7']
      vru_fill_colors = ['#A34D9Da6', '#A6DDE7a6']
    else:
      vru_plot_colors = ['#A6DDE7']
      vru_fill_colors = ['#A6DDE7a6']
    graph_str = ['', '']
    vru_index = 0
    for vru in vru_selected:
        ''' --------------------------------------
      Begin calculate NVPs for seeing vru_selected
      -----------------------------------------'''

        # store 'shoulder height' of selected VRU in [ft]
        vru_height = vru_sizes[vru-1, 0]/12
        # store 'width' of selected VRU in [ft]
        vru_width = vru_sizes[vru-1, 1]/12

        r_vru_nvp = np.empty(len(r_sorted))

        for i in range(len(theta_sorted)):
            # find sides of triangle from eye to ground
            b_eye = r_sorted[i]  # length
            a_eye = eye_height_full  # height
            c_eye = mth.sqrt(a_eye**2 + b_eye**2)  # hypotenuse

            # find sides of similar triangle from vru to ground
            a_vru = vru_height  # height
            c_vru = (a_vru*c_eye)/a_eye  # hypotenuse (similar triangles)
            b_vru = mth.sqrt(a_vru**2 + c_vru**2)  # length

            r_vru_nvp[i] = b_eye-b_vru  # find distance from eye to visible vru

        # plot effective NVP to vru
        ax.plot(theta_sorted, r_vru_nvp,
                vru_plot_colors[vru_index], linewidth=1)
        ax.fill(theta_sorted, r_vru_nvp, vru_fill_colors[vru_index],
                label=f"{vru_label[vru-1]} blindzone")
        ''' ------------------------------------
      End calculate NVPs for seeing vru_selected
      ---------------------------------------'''

        ''' ---------------------------------------------------------
      Begin note minimum distance from hood to VRU in front of driver
      ------------------------------------------------------------'''
        # find nvp in front of driver (with tolerance)
        # b/w 88 and 92deg (taking ind0 since returns array inside variable)
        front_range_indices = np.where(np.logical_and(
            theta_sorted >= (mth.pi/2)-mth.radians(2),
            theta_sorted <= (mth.pi/2)+mth.radians(2)))[0]
        # find index of minimum of selected entries
        front_r_min_index = front_range_indices[np.argmin(
            r_sorted[front_range_indices])]
        # store r value that meets the conditions above (absolute location)
        r_vru_fit = r_vru_nvp[front_r_min_index]
        print(f"distance from eye to hood: {eye_point_full}")
        print(f"distance from eye to {vru_label[vru-1]}: {r_vru_fit}")
        # minimum distance from HOOD to first visible VRU in front of driver (relative distance)
        front_vru_dist = r_vru_fit-eye_point_full  # [ft]
        if front_vru_dist < 0: # prevent negativ results
            front_vru_dist = 0
        # print(f"distance from hood to {vru_label[vru-1]}: {front_vru_dist}")
        # store note (str) of distance to closest forward-visible VRU to pass to site
        graph_str[vru_index] = ('The closest forward-visible ' +
                                vru_label[vru-1] + ' is ' +
                                str(round(front_vru_dist)) + 'ft in front of the vehicle.')

        ''' -------------------------------------------------------
      End note minimum distance from hood to VRU in front of driver
      ----------------------------------------------------------'''
        vru_index += 1

    # restrict angles of plot (switching min and max moves tick labels)
    ax.set_thetamin(plot_end)
    ax.set_thetamax(plot_start)

    # make plot axes match background divisions
    # generate markers range(0,round(max(r)),round(max(r)/7))
    tick_list = np.arange(0, max_distance+1, max_distance/7)
    ax.set_ylim(0, max_distance)  # [0,round(max(r))]
    plt.yticks(tick_list)  # range(0,round(max(r)),round(max(r)/7))

    # label the radial axis
    label_position = ax.get_rlabel_position()
    ax.text(np.radians(plot_end + 15), 5 + ax.get_rmax()/2., 'Distance from Vehicle [ft]',
            rotation=-1 * label_position, horizontalalignment='right', ha='center', va='center')

    ax.grid(True, color='#fff')
    ax.spines['polar'].set_visible(False)

    ''' ---------------------------
  Begin car image scaling/plotting
  -----------------------------'''
    # Choose whether to show a car or truck-sized vehicle on the plot.
    # Numbers taken from VIEW 1.0: eye_height_full < 70 [in] = car, eye_height_full >= 70 [in] = truck

    image_file = "Vehicle-Overhead-09.png"  # import car image
    # create s3 client to  access digital ocean space bucket for image
    s3_client = create_s3_client()

    # Get recently uploaded scan from the bucket
    response = s3_client.get_object(
        Bucket='vehicle-scans', Key=f'static/lidar/images/{image_file}')

    img = Image.open(response['Body'])

    # Change scaling and position based on vehicle size (convert height to [in] for comparison)
    # image placement is in polar (theta, r) and will only plot angles included in the axes.
    # NEED TO FIGURE OUT HOW TO SHIFT IMAGE DOWN AND HAVE IT SHOW UP
    if eye_height_full*12 >= 70:
        # change image zoom to fit truck-sized vehicle
        imagebox = OffsetImage(img, zoom=0.07)
        # position to likely eye position for truck
        ab = AnnotationBbox(imagebox, (0, 1.5), frameon=False)
        # currently not shifted down but needs to be
    else:  # assumes all other cases are cars
        # change image zoom to fit car-sized vehicle
        imagebox = OffsetImage(img, zoom=0.045)
        # position to likely eye position for car
        ab = AnnotationBbox(imagebox, (0, 0.9), frameon=False)

    ax.add_artist(ab)
    ax.patch.set_alpha(0)
    ''' ------------------------
  End car image scaling/plotting
  ---------------------------'''

    # shift plot over to the right by editing its bbox
    '''pos = ax.get_position()
    pos.x0 += .11  # increase value by 11% of figure size
    pos.x1 += .11  # must mach value for x0 for shift, otherwise it narrows the box
    ax.set_position(pos)'''

    # make plot fill entire figure
    pos = ax.get_position()
    pos.x0=0 # units of percentage of fig
    pos.x1=1 
    pos.y0=0 
    pos.y1=1 
    ax.set_position(pos)

    # dislaimer that vehicle pictured is not to scale
    # ax.text(0.75, 0, '*vehicle pictured is not to scale', transform=ax.transAxes,
    ax.text(-0.15,0.02, '*vehicle not shown to scale', transform=ax.transAxes,
            fontsize=10, verticalalignment='center', bbox=dict(boxstyle='square',
                                                               facecolor='#fff', alpha=0))

    # legend in bottom left corner of FIGURE, not PLOT
    #fig.legend(loc='lower right', fontsize="12", fancybox=False)

    # title for the graph
    '''plt.title(
        f"Blindzones for {height_percentile} Driver in {vehicle}", fontsize=15)'''

    imgdata = StringIO()
    # save file as SVG
    # plt.savefig('/content/viz_overhead.svg', transparent=False, dpi='figure',
    #             pad_inches=0, facecolor='#fff', edgecolor='#5c5c5c')
    fig.savefig(imgdata, format='svg', transparent=False, dpi='figure',
                pad_inches=0, facecolor='#fff', edgecolor='#5c5c5c')

    imgdata.seek(0)

    data = imgdata.getvalue()

    return [data, graph_str]
