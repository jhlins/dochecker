import cv2
from pdf2image import convert_from_path
from pathlib import Path
import numpy as np

def imgproc(path):
    img = cv2.imread(path)
    # print(img.shape)
    imggray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('imggray.jpg', imggray)
    thresh, img_bin = cv2.threshold(imggray, 225, 255, cv2.THRESH_BINARY)
    cv2.imwrite('img_bin.jpg', img_bin)
    Hkernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    Vkernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
    img_combine = cv2.morphologyEx(~img_bin, cv2.MORPH_OPEN, Hkernel) + cv2.morphologyEx(~img_bin, cv2.MORPH_OPEN, Vkernel)
    cv2.imwrite('img_combine.jpg', img_combine)

    # # Find contours for image, which will detect all the boxes
    contours, hierarchy = cv2.findContours(img_combine, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img_combine, contours, -1, (0, 255, 0), 3)

    # cv2.imwrite('contoured.jpg', contoured)

    idx = 0
    boundRect = [None] * len(contours)
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        boundRect[idx] = [x, y, w, h]
        idx += 1

    # finalimg = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    finalimg = img

    for i in range(1, len(boundRect)):
        if boundRect[i][0]>5 and boundRect[i][1]>5 and int(boundRect[i][2])*int(boundRect[i][3]) > 1200:
            x = boundRect[i][0] + 4
            y = boundRect[i][1] + 4
            w = boundRect[i][2] - 8
            h = boundRect[i][3] - 8
            roiimg = img[y:y + h, x:x + w]
            roiimg = roiimg[:,:,0]-roiimg[:,:,1]-roiimg[:,:,2]
            ret, opening = cv2.threshold(roiimg, 100, 255, cv2.THRESH_BINARY)
            # cv2.imshow('',opening)
            # cv2.waitKey()
            try:
                nzpercent = (cv2.countNonZero(opening) / (w * h)) * 100
                # print(nzpercent)
            except:
                nzpercent = 0

            if nzpercent < 1:
                color = (0, 0, 255)
                cv2.rectangle(finalimg, (x, y), (x + w, y + h), color, 3)
            else:
                color = (0, 255, 0)
                cv2.rectangle(finalimg, (x, y), (x + w, y + h), color, 3)

        elif boundRect[i][0]>5 and boundRect[i][1]>5 and int(boundRect[i][2])*int(boundRect[i][3]) < 1201 and int(boundRect[i][2])*int(boundRect[i][3]) > 500:
            x = boundRect[i][0]
            y = boundRect[i][1] 
            w = boundRect[i][2] 
            h = boundRect[i][3] 
            roiimg = img[y:y + h, x:x + w]
            diagkern = np.array([[0, 0, 0, 0, 1], [0, 0, 0, 1, 0], [0, 0, 1, 0, 0], [0, 1, 0, 0, 0], [1, 0, 0, 0, 0]],
                                np.uint8)

            roiimg = roiimg[:, :, 0] - roiimg[:, :, 1] - roiimg[:, :, 2]

            ret, opening_temp = cv2.threshold(roiimg, 150, 255, cv2.THRESH_BINARY)
            opening_temp = cv2.morphologyEx(~opening_temp, cv2.MORPH_OPEN, diagkern)
            opening_temp = cv2.erode(~opening_temp, diagkern, iterations=1)
            opening = cv2.dilate(opening_temp, diagkern, iterations=1)
            # cv2.imshow('',opening)
            # cv2.waitKey()

            try:
                nzpercent = (cv2.countNonZero(opening) / (w * h)) * 100
                print(nzpercent)
            except:
                nzpercent = 0
            # print(str(nzpercent) + '%')

            if nzpercent < 7:
                color = (0, 100, 255)
                cv2.rectangle(finalimg, (x, y), (x + w, y + h), color, 3)
            else:
                color = (200, 255, 0)
                cv2.rectangle(finalimg, (x, y), (x + w, y + h), color, 3)

    cv2.imwrite(path, finalimg)
    print(path)

def pdfconvert(filename):
    # Store Pdf with convert_from_path function
    images = convert_from_path(str(Path(__file__).parent) + '\\PDFUpload\\' + filename,poppler_path= str(Path(__file__).parent)+'\\poppler\\bin')

    for i in range(len(images)):
        # logging.debug('Saving page' + str(i))
        # Save pages as images in the pdf
        path = str(Path(__file__).parent) + '\\static\\Tempimgstore\\'+ 'page' + str(i) + '.jpg'
        images[i].save(path, 'JPEG')
        imgproc(path)

if __name__ == '__main__':
    # pdfconvert('834012_SB0008_0041.pdf')
    pdfconvert('TestDoc.pdf')


