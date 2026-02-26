#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import base64
import xml.etree.ElementTree as ET
from PIL import Image
from io import BytesIO
from urllib.request import url2pathname

def saveCover(cover_raw, outputFile, size):
    try:
        cover_decoded = base64.b64decode(cover_raw)
        cover = Image.open(BytesIO(cover_decoded))
        cover.thumbnail((size, size), Image.BILINEAR)
        cover.save(outputFile,"PNG")
    except Exception as e:
        print(e)
        return False
    return True

def getCoverId(root):
    cover_page = root.find('.//description/title-info/coverpage/image')
    if cover_page is None:
        cover_page = root.find('.//{*}description/{*}title-info/{*}coverpage/{*}image')
    if cover_page is None:
        cover_page = root.find('.//body/image')
    if cover_page is None:
        cover_page = root.find('.//{*}body/{*}image')
    if cover_page is None or cover_page.attrib is None:
        return None
    cover_id = None
    for k, v in cover_page.attrib.items():
        if v and len(v) > 0 and k.endswith('href'):
            cover_id = v[1:]
            break
    return cover_id

def try_without_cover_id(root, outputFile, size):
    # a worse case
    for i in root.iter():
        if (i.tag.split('}')[1] == 'binary') and ('id' in i.attrib) and (i.attrib['id'].split('.')[0] == 'cover'):
            print("Found by cover attribute")
            if saveCover(i.text, outputFile, size):
                return True
    # the worst case. trying to find anything
    for i in root.iter():
        if (i.tag.split('}')[1] == 'binary') and ('content-type' in i.attrib) and (i.attrib['content-type'].split('/')[0] == 'image'):
            print("Found by image type")
            if saveCover(i.text, outputFile, size):
                return True
    for i in root.iter():
        if (i.tag.split('}')[1] == 'binary') and ('content-type' in i.attrib) and (i.attrib['id'].split('.')[1].lower() in ['jpg', 'png']):
            print("Found by image type")
            if saveCover(i.text, outputFile, size):
                return True
    return False

def main():
    if len(sys.argv) < 3:
        print('Not enough actual parameters')
        return
    inputFile = sys.argv[1]
    outputFile = sys.argv[2]
    if len(sys.argv) > 3:
        size = int(sys.argv[3])
    else:
        size = 256
    inFile = url2pathname(inputFile).split('file://')[1]
    root = ET.parse(inFile).getroot()
    cover_id = getCoverId(root)
    if cover_id:
        for i in root.iter():
            if (i.tag.split('}')[1] == 'binary') and ('id' in i.attrib) and (i.attrib['id'] == cover_id):
                print(f"Found by coverpage = #{cover_id}")
                if saveCover(i.text, outputFile, size):
                    return
    if not try_without_cover_id(root, outputFile, size):
        print('No cover inside')

if __name__ == '__main__':
    main()
