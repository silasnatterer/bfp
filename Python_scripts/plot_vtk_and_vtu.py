#!/usr/bin/env python

import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import numpy as np

vtk1_file = "/home/arltpl/Documents/FEBio Studio Models/jobs/muscle_no_fibers_1.t"
vtk_file_scaled = "/home/arltpl/Documents/FEBio Studio Models/jobs/muscle_no_fibers_scaled_z.t"
vtu1_file = "/home/arltpl/git-repos/opendihu/examples/bfp/muscle_no_fibers/build_release/out/2d_0000"

def is_close(a, b, rel_tolerance):
    return abs(a - b) <= b * rel_tolerance

def parse_vtk_scaled(filename, digits):
    files = []
    for i in range(10 ** digits):
        appendix = str(i)
        while (len(appendix) != digits):
            appendix = "0" + appendix
        next_vtk_file = filename + appendix + ".vtk"

        try:
            file = open(next_vtk_file, "r")
            files.append(file)
        except:
            break
    print(str(len(files)) + " files were read")

    base_x = 0

    # identify data points that refer to the right hand-side of the muscle
    relevant_indices = []
    appendix = str(0) * digits
    try:
        file = open(filename + appendix + ".vtk", "r")
    except:
        print("error while opening first file")
        return [ 0.0 ]
    # 0 if x-value is read, 1 for y, 2 for z
    xyz_index = 0
    x_values = []

    # skip header
    for i in range(5):
        file.readline()
    
    while True:
        line = file.readline()

        # end of data points
        if (len(line) == 1):
            break
        
        for word in line.split():
            if xyz_index == 2:
                x_values.append(float(word))
            xyz_index = (xyz_index + 1) % 3
    
    # identify all indices that have a maximum x-value
    base_x = min(x_values)
    max_value = max(x_values)
    for i in range(len(x_values)):
        if is_close(x_values[i] - base_x, max_value - base_x, 0.05):
            relevant_indices.append(i * 3 + 2)
        
    # read data for plotting
    relevant_x_values_over_time = []
    for fileindex in range(len(files)):
        file = files[fileindex]

        index = 0
        relevant_index_counter = 0

        relevant_x_values = []

        # skip header
        for i in range(5):
            file.readline()
        
        while True:
            line = file.readline()

            # end of data points
            if (len(line) == 1):
                break
            
            for word in line.split():
                if relevant_index_counter < len(relevant_indices) and index == relevant_indices[relevant_index_counter]:
                    relevant_x_values.append((float(word) - base_x) * 100.0)
                    relevant_index_counter += 1
                index += 1
        
        relevant_x_values_over_time.append(relevant_x_values)
    
    mean_of_x_over_time = []
    for relevant_x_values in relevant_x_values_over_time:
        mean_of_x_over_time.append(np.mean(relevant_x_values))
        
    for file in files:
        file.close()
    
    return mean_of_x_over_time

def parse_vtk(filename, digits):
    files = []
    for i in range(10 ** digits):
        appendix = str(i)
        while (len(appendix) != digits):
            appendix = "0" + appendix
        next_vtk_file = filename + appendix + ".vtk"

        try:
            file = open(next_vtk_file, "r")
            files.append(file)
        except:
            break
    print(str(len(files)) + " files were read")

    base_x = 0

    # identify data points that refer to the right hand-side of the muscle
    relevant_indices = []
    appendix = str(0) * digits
    try:
        file = open(filename + appendix + ".vtk", "r")
    except:
        print("error while opening first file")
        return [ 0.0 ]
    # 0 if x-value is read, 1 for y, 2 for z
    xyz_index = 0
    x_values = []

    # skip header
    for i in range(5):
        file.readline()
    
    while True:
        line = file.readline()

        # end of data points
        if (len(line) == 1):
            break
        
        for word in line.split():
            if xyz_index == 2:
                x_values.append(float(word))
            xyz_index = (xyz_index + 1) % 3
    
    # identify all indices that have a maximum x-value
    base_x = min(x_values)
    max_value = max(x_values)
    for i in range(len(x_values)):
        if is_close(x_values[i] - base_x, max_value - base_x, 0.05):
            relevant_indices.append(i * 3 + 2)
        
    # read data for plotting
    relevant_x_values_over_time = []
    for fileindex in range(len(files)):
        file = files[fileindex]

        index = 0
        relevant_index_counter = 0

        relevant_x_values = []

        # skip header
        for i in range(5):
            file.readline()
        
        while True:
            line = file.readline()

            # end of data points
            if (len(line) == 1):
                break
            
            for word in line.split():
                if relevant_index_counter < len(relevant_indices) and index == relevant_indices[relevant_index_counter]:
                    relevant_x_values.append(float(word) - base_x)
                    relevant_index_counter += 1
                index += 1
        
        relevant_x_values_over_time.append(relevant_x_values)
    
    mean_of_x_over_time = []
    for relevant_x_values in relevant_x_values_over_time:
        mean_of_x_over_time.append(np.mean(relevant_x_values))
        
    for file in files:
        file.close()
    
    return mean_of_x_over_time

def parse_vtu(filename):
    trees = []
    for i in range(1000):
        next_vtu_file = filename + "{:03d}".format(i) + ".vtu"

        try:
            tree = ET.parse(next_vtu_file)
            trees.append(tree)
        except:
            break
    print(str(len(trees)) + " files were read")

    base_x = 0

    # identify data points that refer to the right hand-side of the muscle
    relevant_indices = []
    tree = ET.parse(filename + "000.vtu")
    # 0 if x-value is read, 1 for y, 2 for z
    xyz_index = 0
    x_values = []

    # awkward way to navigate to relevant data
    string_listing = trees[0].getroot()[0][1][2][0].text.split()

    for string in string_listing:
        value = float(string)
        if xyz_index == 2:
            x_values.append(float(value))
        xyz_index = (xyz_index + 1) % 3
    
    # identify all indices that have a maximum x-value
    base_x = min(x_values)
    max_value = max(x_values)
    for i in range(len(x_values)):
        if is_close(x_values[i] - base_x, max_value - base_x, 0.05):
            relevant_indices.append(i * 3 + 2)
        
    # read data for plotting
    relevant_x_values_over_time = []
    for treeindex in range(len(trees)):
        index = 0
        relevant_index_counter = 0

        relevant_x_values = []

        string_listing = trees[treeindex].getroot()[0][1][2][0].text.split()

        for string in string_listing:
            value = float(string)
            if relevant_index_counter < len(relevant_indices) and index == relevant_indices[relevant_index_counter]:
                relevant_x_values.append((float(value) - base_x) / 1.0)
                relevant_index_counter += 1
            index += 1
        
        relevant_x_values_over_time.append(relevant_x_values)
    
    mean_of_x_over_time = []
    for relevant_x_values in relevant_x_values_over_time:
        mean_of_x_over_time.append(np.mean(relevant_x_values))
    
    return mean_of_x_over_time

def main():
    vtk1_x_means = parse_vtk(vtk1_file, 3)
    vtk2_x_means = parse_vtk_scaled(vtk_file_scaled, 3)
    vtu1_x_means = parse_vtu(vtu1_file)

    x_vtk = np.linspace(0, len(vtk1_x_means) / 10.0, len(vtk1_x_means))
    x_vtu = np.linspace(0, len(vtu1_x_means) / 10.0, len(vtu1_x_means))

    plt.plot(x_vtk, vtk1_x_means, label="FEBio - OpenDiHu units", linewidth=0.5, marker='x',markevery=10)
    plt.plot(x_vtk, vtk2_x_means, label="FEBio - SI units", linewidth=0.5, marker='_',markevery=10)
    plt.plot(x_vtu, vtu1_x_means, label="OpenDiHu", linewidth=0.5, marker='|',markevery=10)

    y12 = [abs(x-y)**2 for x,y in zip (vtk1_x_means, vtu1_x_means)]
    print("mean = " + str(sum(y12) / len(y12)))

    plt.xlabel("time (ms)")
    plt.ylabel("free end position (cm)")
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
