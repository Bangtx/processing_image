from fastapi import APIRouter, File
import cv2
import numpy as np
from utils import utilities

router = APIRouter()


@router.post('/')
async def create_file(file: bytes = File()):

    # with open("16.jpg", 'rb') as fp:
    #     img = fp.read()
    img = np.frombuffer(file, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    # im_cv = cv2.imread(im_path)
    img2 = img.copy()
    img3 = img.copy()
    # print(img)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # img_gray = cv2.resize(img_gray, (350, 550))

    blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_canny = cv2.Canny(blur, 10, 100)

    contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img.copy(), contours, -1, (0, 255, 0), 2)
    rect_con = utilities.rect_contour(contours)

    bigContours = utilities.getCornerPoints(rect_con[0])
    mssvContours = utilities.getCornerPoints(rect_con[1])
    ma_De_Contours = utilities.getCornerPoints(rect_con[2])

    result = {}

    img_info = {
        'result': {
            'contours': utilities.getCornerPoints(rect_con[0]),
            'position': [[0, 0], [660, 0], [0, 1000], [660, 1000]],
            'size': {
                'img': (660, 1000), 'ans': (25, 11), 'resize': (330, 500)
            },
            'img': img.copy(),
            'img_cut': None
        },
        'student': {
            'contours': utilities.getCornerPoints(rect_con[1]),
            'position': [[0, 0], [800, 0], [0, 800], [800, 800]],
            'size': {
                'img': (800, 800), 'ans': (10, 8), 'resize': (150, 250)
            },
            'img': img.copy(),
            'img_cut': None
        },
        'code': {
            'contours': utilities.getCornerPoints(rect_con[2]),
            'position': [[0, 0], [660, 0], [0, 600], [660, 600]],
            'size': {
                'img': (660, 600), 'ans': (10, 3), 'resize': (150, 250)
            },
            'img': img.copy(),
            'img_cut': None
        }
    }

    if bigContours.size != 0 and mssvContours.size != 0 and ma_De_Contours.size != 0:
        for area, value in img_info.items():
            # if area != 'code': continue
            cv2.drawContours(value['img'], value['contours'], -1, (0, 255, 0), 10)
            pt1 = np.float32(utilities.reoder(value['contours']))
            pt2 = np.float32(value['position'])
            value['img_cut'] = cv2.warpPerspective(img_gray, cv2.getPerspectiveTransform(pt1, pt2),
                                                   value['size']['img'])
            # imgTraLoi_mau = cv2.warpPerspective(img2, matrix, value['size'])

            img_thersh = cv2.threshold(value['img_cut'], 100, 255, cv2.THRESH_BINARY_INV)[1]

            img_thersh_resize = cv2.resize(img_thersh, value['size']['resize'])
            cv2.imwrite(f"img_thersh{area}.jpg", img_thersh_resize)

            fill = ""

            if area == 'result':
                # crop image
                cell_width = value['size']['resize'][0] / value['size']['ans'][1]
                img_left = img_thersh_resize[0:value['size']['resize'][1], 0: int(cell_width*4)]
                img_right = img_thersh_resize[
                    0:value['size']['resize'][1],
                    int(value['size']['resize'][0] - int(cell_width*4)): value['size']['resize'][0]
                ]
                for col in [img_left, img_right]:
                    matrix = utilities.split_boxes(col, value['size']['ans'][0], 4)
                    fill += find_filled_cell(matrix, [25, 4], True)

                # imgRowDra = np.zeros_like(value['img_cut'])
                # ans = [
                #     {}
                # ]
                # imgRowDra = utilities.show_ans(imgRowDra, ans, value['size']['ans'])
            else:
                # index_c = 0
                # index_r = 0
                # count_non_zero = np.zeros(value['size']['ans'])
                #
                matrix = utilities.split_boxes(img_thersh, value['size']['ans'][0], value['size']['ans'][1])
                fill = find_filled_cell(matrix, value['size']['ans'], False)
                #
                # for image2 in matrix:
                #     # if area == 'code':
                #     #     print(cv2.countNonZero(image2), 124)
                #     count_non_zero[index_r][index_c] = cv2.countNonZero(image2)
                #     index_c += 1
                #     if index_c == value['size']['ans'][1]:
                #         index_r += 1
                #         index_c = 0
                #
                # count_non_zero = np.transpose(count_non_zero)
                #
                # for arr in count_non_zero:
                #     fill += str(np.where(arr == np.amax(arr))[0][0])

            result[area] = fill

    return result


def find_filled_cell(matrix, size_ans, is_result):
    fill = ''
    index_c = 0
    index_r = 0
    count_non_zero = np.zeros(size_ans)

    for image2 in matrix:
        # if area == 'code':
        #     print(cv2.countNonZero(image2), 124)
        count_non_zero[index_r][index_c] = cv2.countNonZero(image2)
        index_c += 1
        if index_c == size_ans[1]:
            index_r += 1
            index_c = 0
    if not is_result:
        count_non_zero = np.transpose(count_non_zero)

    for arr in count_non_zero:
        if list(filter(lambda x: x > 100, arr)):
            fill += str(np.where(arr == np.amax(arr))[0][0])

    return fill
        #     if area == 'result':
        #         imgRowDra = np.zeros_like(value['img'])
        #         imgRowDra = utilities.showAns(imgRowDra, [1, 3, 2, 1], [1, 1, 0, 1], [1, 3, 1, 1], row, column)
        # cv2.imshow('img', imgRowDra)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    ################################# new code #######################################

    """if bigContours.size != 0 and mssvContours.size != 0 and ma_De_Contours.size != 0:
        ##################################
        # cv2.drawContours(img.copy(), bigContours, -1, (0, 255, 0), 10)
        # bigContours = utilities.reoder(bigContours)
        # pt1 = np.float32(bigContours)
        # pt2 = np.float32([[0, 0], [660, 0], [0, 1000], [660, 1000]])
        # matrix = cv2.getPerspectiveTransform(pt1, pt2)
        # imgTraLoi = cv2.warpPerspective(img_gray, matrix, (660, 1000))
        # imgTraLoi_mau = cv2.warpPerspective(img2, matrix, (660, 1000))
        #
        # cv2.drawContours(img.copy(), mssvContours, -1, (0, 255, 0), 10)
        # mssvContours = utilities.reoder(mssvContours)
        # pt3 = np.float32(mssvContours)
        # pt4 = np.float32([[0, 0], [800, 0], [0, 800], [800, 800]])
        # matrix1 = cv2.getPerspectiveTransform(pt3, pt4)
        # imgMSSV = cv2.warpPerspective(img_gray, matrix1, (800, 800))
        # img_MSSV_mau = cv2.warpPerspective(img2, matrix1, (800, 800))
        #
        # cv2.drawContours(img.copy(), ma_De_Contours, -1, (0, 255, 0), 10)
        # ma_De_Contours = utilities.reoder(ma_De_Contours)
        # pt5 = np.float32(ma_De_Contours)
        # pt6 = np.float32([[0, 0], [660, 0], [0, 600], [660, 600]])
        # matrix2 = cv2.getPerspectiveTransform(pt5, pt6)
        # # img_Ma_De = cv2.warpPerspective(img_gray, matrix2, (90, 100))
        # img_Ma_De = cv2.warpPerspective(img_gray, matrix2, (660, 600))
        # img_Ma_De_mau = cv2.warpPerspective(img2, matrix2, (660, 600))

        #######################################

        imgThersh_ma_de = cv2.threshold(img_Ma_De, 100, 255, cv2.THRESH_BINARY_INV)[1]
        matran_ma_de = utilities.split_boxes(imgThersh_ma_de, 10, 3)

        imgThersh_ma_de_tem = cv2.resize(imgThersh_ma_de, (150, 150))
        cv2.imwrite("imgThersh_ma_de.jpg", imgThersh_ma_de_tem)

        toado_ma_deC = 0
        toado_ma_deR = 0
        myPixel_ma_de = np.zeros((10, 3))

        for image2 in matran_ma_de:
            total_mssv = cv2.countNonZero(image2)
            myPixel_ma_de[toado_ma_deR][toado_ma_deC] = total_mssv
            toado_ma_deC += 1
            if toado_ma_deC == 3:
                toado_ma_deR += 1
                toado_ma_deC = 0

        myPixel_ma_de = np.transpose(myPixel_ma_de)

        myIndex_ma_de = []
        for x in range(0, 3):
            arr = myPixel_ma_de[x]
            myIndex_ma_de_val = np.where(arr == np.amax(arr))

            myIndex_ma_de.append(myIndex_ma_de_val[0][0])

        ma_de = ""
        for u in range(len(myIndex_ma_de)):
            ma_de = ma_de + str(myIndex_ma_de[u])

        # for i in range(len(made_goc)):
        #
        #     if int(ma_de) == made_goc[i]:
        #         ans = dapAn_goc[i]
        #         trongSo = trongSo_goc[i]
        #         diemSai = dsdiemTru[i]
        print(ma_de)

        ######################################

        # imgThersh_tra_loi = cv2.threshold(imgTraLoi, 100, 255, cv2.THRESH_BINARY_INV)[1]
        #
        # imgThersh_tra_loi = imgThersh_tra_loi[10: 990, 15:640]
        # imgThersh_tra_loi = cv2.resize(imgThersh_tra_loi, (660, 600))
        # # cv2.imshow("show", imgThersh_tra_loi)
        #
        # imgThersh_tra_loi_tem = cv2.resize(imgThersh_tra_loi, (150, 150))
        # cv2.imwrite("imgThersh_tra_loi.jpg", imgThersh_tra_loi_tem)
        #
        # boxes = utilities.split_boxes(imgThersh_tra_loi, 25, 11)
        #
        # myPixelVal = np.zeros((row, column))
        # contC = 0
        # contR = 0
        # for image in boxes:
        #
        #     totalPixels = cv2.countNonZero(image)
        #     myPixelVal[contR][contC] = totalPixels
        #     contC += 1
        #     if contC == column:
        #         contR += 1
        #         contC = 0

        # myIndex = []
        # if soCau >= 25:
        #     cauHoiCot1 = 25
        #     cauHoiCot2 = soCau - cauHoiCot1
        #
        # if soCau < 25:
        #     cauHoiCot1 = soCau
        #     cauHoiCot2 = 0
        #
        # if soCau >= 25:
        #
        #     for x in range(0, row):
        #
        #         arr = myPixelVal[x]
        #
        #         ok = 0
        #
        #         for i in range(len(arr)):
        #             if arr[i] < 500:
        #                 ok += 1
        #
        #         myIndexAns = [0] * 4
        #
        #         ok1 = 0
        #
        #         for r in range(0, 4):
        #             myIndexAns[r] = arr[r]
        #
        #         for r in range(0, 4):
        #             if arr[r] < 400:
        #                 ok1 += 1
        #
        #         if ok1 != 3:
        #             myIndex.append(4)
        #
        #         if ok1 == 3:
        #
        #             for ri in range(0, 4):
        #
        #                 if myIndexAns[ri] == np.max(myIndexAns):
        #                     myIndex.append(ri)
        #
        #         ok1 = 0
        #
        #         if x <= cauHoiCot2 and cauHoiCot1 == 25:
        #
        #             for r in range(7, 11):
        #                 myIndexAns[r - 7] = arr[r]
        #
        #             for r in range(7, 11):
        #                 if arr[r] < 400:
        #                     ok1 += 1
        #
        #             if ok1 != 3:
        #                 myIndex.append(6)
        #             if ok1 == 3:
        #                 for ri in range(0, 4):
        #
        #                     if myIndexAns[ri] == np.max(myIndexAns):
        #                         myIndex.append(ri + 7)
        #
        #         if x > cauHoiCot2 and cauHoiCot1 == 25:
        #             myIndex.append(6)
        #
        # if soCau < 25:
        #     for x in range(0, cauHoiCot1 + 1):
        #
        #         arr = myPixelVal[x]
        #
        #         ok = 0
        #
        #         for i in range(len(arr)):
        #             if arr[i] < 500:
        #                 ok += 1
        #
        #         myIndexAns = [0] * 4
        #
        #         ok1 = 0
        #
        #         for r in range(0, 4):
        #             myIndexAns[r] = arr[r]
        #
        #         for r in range(0, 4):
        #             if arr[r] < 400:
        #                 ok1 += 1
        #
        #         if ok1 != 3:
        #             myIndex.append(4)
        #
        #         if ok1 == 3:
        #
        #             for ri in range(0, 4):
        #
        #                 if myIndexAns[ri] == np.max(myIndexAns):
        #                     myIndex.append(ri)
        #
        #         ok1 = 0
        #
        #         myIndex.append(6)
        #
        #     for add in range(cauHoiCot1 + 1, 25):
        #         myIndex.append(4)
        #         myIndex.append(6)
        #
        # grading = []
        # score = 0
        #
        # for x in range(0, 50):
        #
        #     if int(ans[x]) == myIndex[x]:
        #         grading.append(1)
        #         score += float(trongSo[x])
        #
        #     if int(ans[x]) != myIndex[x]:
        #
        #         if myIndex[x] != 4 and myIndex[x] != 6:
        #
        #             score = score - float(diemSai[x])
        #
        #         grading.append(0)
        #
        # cv2.putText(img3, str(score) + "->", (100, 100), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
        #
        # if score <= 12:
        #     score = 1.5
        # if 12 < score <= 17:
        #     score = 2
        # if 17 < score <= 22:
        #     score = 2.5
        # if 22 < score <= 27:
        #     score = 3
        # if 27 < score <= 32:
        #     score = 3.5
        # if 32 < score <= 37:
        #     score = 4
        # if 37 < score <= 42:
        #     score = 4.5
        # if 42 < score <= 47:
        #     score = 5
        # if 47 < score <= 52:
        #     score = 5.5
        # if 52 < score <= 57:
        #     score = 6
        # if 57 < score <= 62:
        #     score = 6.5
        # if 62 < score <= 67:
        #     score = 7
        # if 67 < score <= 72:
        #     score = 7.5
        # if 72 < score <= 77:
        #     score = 8
        # if 77 < score <= 82:
        #     score = 8.5
        # if 82 < score <= 87:
        #     score = 9
        # if 87 < score <= 92:
        #     score = 9.5
        # if 92 < score:
        #     score = 10
        #
        #
        # #########################################
        #
        # imgThersh_mssv = cv2.threshold(imgMSSV, 100, 255, cv2.THRESH_BINARY_INV)[1]
        # matran_mssv = utilities.split_boxes(imgThersh_mssv, 10, 8)
        #
        # imgThersh_mssv_tem = cv2.resize(imgThersh_mssv, (150, 150))
        # cv2.imwrite("imgThersh_mssv_tem.jpg", imgThersh_mssv_tem)
        #
        # toadoC = 0
        # toadoR = 0
        # myPixel_mssv = np.zeros((10, 8))
        #
        # for image1 in matran_mssv:
        #     total_mssv = cv2.countNonZero(image1)
        #     myPixel_mssv[toadoR][toadoC] = total_mssv
        #     toadoC += 1
        #     if toadoC == 8:
        #         toadoR += 1
        #         toadoC = 0
        #
        # myPixel_mssv = np.transpose(myPixel_mssv)
        #
        # myIndex_mssv = []
        # for x in range(0, 8):
        #     arr = myPixel_mssv[x]
        #     myIndex_mssv_val = np.where(arr == np.amax(arr))
        #     # myIndexVal = np.where(arr == np.max(arr))
        #     myIndex_mssv.append(myIndex_mssv_val[0][0])
        #
        # ma_so = ""
        # for u in range(len(myIndex_mssv)):
        #     ma_so = ma_so + str(myIndex_mssv[u])
        # # print(ma_so)
        #
        # ###########################################
        # temp2.ma_so = ma_so
        # temp2.ma_de = ma_de
        # temp2.diem = score
        # ########################################
        #
        # imgRowDra = np.zeros_like(imgTraLoi_mau)
        # imgRowDra = utilities.showAns(imgRowDra, myIndex, grading, ans, row, column)
        #
        # matrixBaithi = cv2.getPerspectiveTransform(pt2, pt1)
        # imgBaiThi = cv2.warpPerspective(imgRowDra, matrixBaithi, (660, 600))
        # cv2.putText(img3, str(score) + "", (350, 100), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 2)
        #
        # cv2.putText(img3, "MSSV:" + str(ma_so), (100, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        #
        # cv2.putText(img3, "Ma De: " + str(ma_de), (100, 300), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        # img3 = cv2.addWeighted(img3, 1, imgBaiThi, 1, 0)
        #
        # imgtl = cv2.resize(img3, (550, 500))
        #
        # cv2.imwrite("img3.jpg", imgtl)"""

# import cv2
#
#
# img = cv2.imread('2023-02-09_22-09.png')
#
# cv2.imshow('im', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
