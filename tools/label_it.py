from tkinter import *
from PIL import ImageTk, Image
import os



dir_path = '/Users/Norman/SourceCode/Break12306Captcha/testsets/test_set_1/'
files = ["2016_11_30_01_22_39_zb4LT.jpg","2016_11_30_01_22_41_EJAPB.jpg","2016_11_30_01_22_43_0JyHG.jpg","2016_11_30_01_22_45_RtGPH.jpg","2016_11_30_01_22_48_TNkTu.jpg","2016_11_30_01_22_50_4Yujn.jpg","2016_11_30_01_22_53_3ssrq.jpg","2016_11_30_01_22_55_ywk4T.jpg","2016_11_30_01_22_58_DNzjo.jpg","2016_11_30_01_23_01_jFiwO.jpg","2016_11_30_01_23_04_4IFzt.jpg","2016_11_30_01_23_08_fAZYd.jpg","2016_11_30_01_23_10_5ti05.jpg","2016_11_30_01_23_13_FbCQq.jpg","2016_11_30_01_23_17_eys7c.jpg","2016_11_30_01_23_19_4re4X.jpg","2016_11_30_01_23_21_TfnCJ.jpg","2016_11_30_01_23_24_3lNhj.jpg","2016_11_30_01_23_27_a4pGA.jpg","2016_11_30_01_23_30_QO9Kq.jpg","2016_11_30_01_23_33_UX3dY.jpg","2016_11_30_01_23_35_9s0GS.jpg","2016_11_30_01_23_39_1IBTA.jpg","2016_11_30_01_23_41_aXMss.jpg","2016_11_30_01_23_44_Wsh0V.jpg","2016_11_30_01_23_47_nICua.jpg","2016_11_30_01_23_52_xVvbO.jpg","2016_11_30_01_23_59_GAVNj.jpg","2016_11_30_01_24_01_1Amqm.jpg","2016_11_30_01_24_03_286E9.jpg","2016_11_30_01_24_05_s344n.jpg","2016_11_30_01_24_07_6WAId.jpg","2016_11_30_01_24_11_OUyjq.jpg","2016_11_30_01_24_13_znX6r.jpg","2016_11_30_01_24_15_NBNO7.jpg","2016_11_30_01_24_18_q0Ed6.jpg","2016_11_30_01_24_20_lLvzb.jpg","2016_11_30_01_24_22_wDYcW.jpg","2016_11_30_01_24_24_7920t.jpg","2016_11_30_01_24_26_YYayr.jpg","2016_11_30_01_24_28_8Gdb6.jpg","2016_11_30_01_24_30_dt6JO.jpg","2016_11_30_01_24_33_JXkju.jpg","2016_11_30_01_24_35_jNSSY.jpg","2016_11_30_01_24_37_7SUKc.jpg","2016_11_30_01_24_40_cuPdk.jpg","2016_11_30_01_24_42_cnII4.jpg","2016_11_30_01_24_44_UsZZN.jpg","2016_11_30_01_24_46_HrldT.jpg","2016_11_30_01_24_48_MoOtd.jpg","2016_11_30_01_24_50_UKkrB.jpg","2016_11_30_01_24_53_GYuct.jpg","2016_11_30_01_24_55_VkZDH.jpg","2016_11_30_01_24_58_HVYbc.jpg","2016_11_30_01_25_00_n3m3G.jpg","2016_11_30_01_25_03_ub1mM.jpg","2016_11_30_01_25_06_9yEpC.jpg","2016_11_30_01_25_09_Wt9E2.jpg","2016_11_30_01_25_12_a2MSj.jpg","2016_11_30_01_25_15_K9MxK.jpg","2016_11_30_01_25_17_IJuqj.jpg","2016_11_30_01_25_20_ZDf8t.jpg","2016_11_30_01_25_22_aaS2o.jpg","2016_11_30_01_25_25_oWuuL.jpg","2016_11_30_01_25_27_GGa07.jpg","2016_12_05_19_22_49_HmJtL.jpg","2016_12_05_19_22_52_fC782.jpg","2016_12_05_19_22_54_CL2xu.jpg","2016_12_05_19_22_56_M0bfS.jpg","2016_12_05_19_22_58_VHhdo.jpg","2016_12_05_19_23_00_X0dXO.jpg","2016_12_05_19_23_02_TghZY.jpg","2016_12_05_19_23_04_4gIF1.jpg","2016_12_05_19_23_06_kcXRY.jpg","2016_12_05_19_23_08_KFJPs.jpg","2016_12_05_19_23_10_iEW2C.jpg","2016_12_05_19_23_13_2OWBV.jpg","2016_12_05_19_23_15_jOzpu.jpg","2016_12_05_19_23_17_eeKOr.jpg","2016_12_05_19_23_19_k870M.jpg","2016_12_05_19_23_21_xFiiD.jpg","2016_12_05_19_23_24_VZiV7.jpg","2016_12_05_19_23_26_6pRG7.jpg","2016_12_05_19_23_28_WrNjk.jpg","2016_12_10_18_33_40_J3wVS.jpg","2016_12_10_18_33_43_csWfv.jpg","2016_12_10_18_33_45_v5g8O.jpg","2016_12_10_18_33_47_u3i2W.jpg","2016_12_10_18_33_49_Awu4f.jpg","2016_12_10_18_33_51_HAn8d.jpg","2016_12_10_18_33_53_wKHFO.jpg","2016_12_10_18_33_55_OZe1R.jpg","2016_12_10_18_33_57_ftf9M.jpg","2016_12_10_18_33_59_kGfSv.jpg","2016_12_10_18_34_01_QVmug.jpg","2016_12_10_18_34_04_39tZN.jpg","2016_12_10_18_34_06_kv3bD.jpg","2016_12_10_18_34_08_mku5Y.jpg","2016_12_10_18_34_10_tYZl5.jpg","2016_12_10_18_34_12_DhZ2f.jpg","2016_12_10_18_34_14_wxTLI.jpg"]


def find_pos(event):
    positions = [(41, 78), (106, 77), (179, 79), (260, 79), (41, 150), (111,154), (178, 154), (252, 155)]
    dist = lambda x, y: abs(x[0] - y[0]) + abs(x[1] - y[1])
    clicked_pos = (event.x, event.y)
    cur_dist = dist(positions[0], clicked_pos)
    result = 0
    for i, pos in enumerate(positions):
        if dist(pos, clicked_pos) <= cur_dist:
            cur_dist = dist(pos, clicked_pos)
            result = i
    return result



file = iter(files)

chosen = list()

def click_callback(event):
    global chosen
    chosen.append(find_pos(event))


def button_callback(event):
    fpath = os.path.join(dir_path, next(file))
    img = ImageTk.PhotoImage(Image.open(fpath))
    panel.configure(image = img)
    panel.image = img
    global chosen
    result = sorted(list(set(chosen)))
    print ("{}\t{}".format(fpath, " ".join(map(lambda x: str(x), result))))
    chosen = list()

root = Tk()
img = ImageTk.PhotoImage(Image.open(os.path.join(dir_path, next(file))))
panel = Label(root, image = img)
panel.bind("<Button-1>", click_callback)
b = Button(root, text="next!")
b.bind("<Button-1>", button_callback)
panel.pack(side = "bottom", fill = "both", expand = "yes")
b.pack(fill=BOTH, expand=1)
root.mainloop()
