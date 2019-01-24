import os
import pandas as pd
import numpy as np
import csv
import shutil
import bisect
from decimal import Decimal
import datetime
import matplotlib
import matplotlib.pyplot as plt


def hms_to_seconds(tIn):
    if tIn is None or tIn is np.nan:
        return None
    elif isinstance(tIn, datetime.time):
        return tIn.hour * 3600 + tIn.minute * 60 + tIn.second
    else:
        tCells = tIn.split(':')
        if len(tCells) == 3:
            return int(tCells[0]) * 3600 + int(tCells[1]) * 60 + float(tCells[2])
        else:
            if len(tCells) == 2:
                return int(tCells[0]) * 60 + float(tCells[1])
            else:
                return float(tCells[0])


def seconds_to_hms(seconds):
    input = Decimal(seconds)
    m, s = divmod(input, 60)
    h, m = divmod(m, 60)
    hms = "%02d:%02d:%05.2f" % (h, m, s)
    return hms


def main():
    data_dir = "C:\Users\Stoves\Desktop\ergo_data\ergo_jan2017_23_2017123_92816619"
    body_dir = os.path.join(data_dir, "bodies")
    if not os.path.isdir(body_dir):
        os.makedirs(body_dir)
    n = 0
    for body in [p for p in os.listdir(data_dir) if "Position" in p]:
        n += 1
        print body
        body_path = os.path.join(data_dir, body)
        data = pd.read_csv(body_path, header=0)
        data["Time"] = data["Time"].apply(hms_to_seconds)
        with open(body_path, 'rb') as in_body:
            csv_read = csv.reader(in_body)
            header = True
            priorTime = Decimal(0.0)
            startIndex = 0
            endIndex = 0
            for row in csv_read:
                if header:
                    header = False
                else:
                    row[0] = Decimal(hms_to_seconds(row[0]))
                    if priorTime == 0.0:
                        priorTime = row[0]
                    else:
                        diff = row[0] - priorTime
                        if diff > 1:
                            out_file = "body_" + str(n) + "_jointPosition.csv"
                            out_path = os.path.join(body_dir, out_file)
                            temp = data.ix[startIndex:endIndex-1]
                            if temp.shape[0] > 30:  # one second of data 30 fps
                                temp.to_csv(out_path, index=False)
                                print startIndex, endIndex
                                n += 1
                            startIndex = endIndex
                        priorTime = row[0]
                    endIndex += 1
    return


if __name__ == '__main__':
    main()
