import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid
from secrets import choice
import streamlit as st

import face_recognition
from datetime import datetime
from PIL import Image
import pandas as pd
import numpy as np
import time
import cv2
import os

# JUDUL WEBSITE
st.set_page_config (page_title= "Kelas Pak Sapta", page_icon="📷",)

# HIDE "Made with Streamlit"
hhide_st_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>"""
st.markdown (hhide_st_style, unsafe_allow_html=True)

# MENAMPILKAN KAMERA
FRAME_WINDOW = st.image ([])

# DEKLARASI
with st.sidebar:
    listMenu = option_menu(
        menu_title = "Welcome",
        menu_icon = "door-open",
        options = ["Home", "Absen", "Daftar", "Kehadiran", "About"],
        icons = ["house-fill", "camera", "file-earmark-arrow-up", "person-check", "people-fill"],
        default_index = 0,
    )

path = "daftarmahasiwa"
images = []
classNames = []
myList = os.listdir (path)

kamera = cv2.VideoCapture (0)
col1, col2, col3 = st.columns (3)

# TAMPILAN HOME
if listMenu == "Home":
    st.title ("Absensi Sederhana Menggunakan")
    st.subheader ("Pengenalan Wajah (OpenCV)")
    image = Image.open ("gambar\\Confirmed attendance-rafiki.png")
    st.image (image, caption = "Face Recognition")

# LOGIN
elif listMenu == "Absen": 
    st.markdown ("<h1 style='text-align: center; color: black;'>Absensi</h1>", unsafe_allow_html=True)
    st.subheader ("Login")
    tekan = st.checkbox ("Kamera")
    if tekan == True:
        print (st.warning ("Maaf Menunggu Lama, Sedang Encoding Data Wajah!"))
        for cl in myList:
            curlImg = cv2.imread (f'{path}/{cl}')
            images.append (curlImg)
            classNames.append (os.path.splitext (cl)[0])
        print (classNames)

        def findEncodings (images):
            encodeList = []
            for img in images:
                img = cv2.cvtColor (img, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings (img)[0]
                encodeList.append (encode)
            return encodeList

        def faceList (name):
            with open ("absensi.csv", "r+") as f:
                myDataList = f.readlines()
                nameList = []
                for line in myDataList:
                    entry = line.split (',')
                    nameList.append (entry[0])
                #if name in nameList:
                if name not in nameList:
                    now = datetime.now()
                    dtString = now.strftime ("%D,%H:%M:%S")
                    f.writelines (f'\n{name},{dtString}')
                    
        encodeListKnown = findEncodings (images)
        print ("Proses Encoding Selesai!")
        
        while True:
            success, img = kamera.read()
            imgS = cv2.resize (img, (0,0), None, 0.25, 0.25)
            imgS = cv2.cvtColor (imgS, cv2.COLOR_BGR2RGB)
            faceCurFrame = face_recognition.face_locations (imgS)
            encodeCurFrame = face_recognition.face_encodings (imgS, faceCurFrame)

            for encodeFace, faceLoc in zip (encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces (encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance (encodeListKnown, encodeFace)
                
                matchesIndex = np.argmin (faceDis)

                if matches [matchesIndex]:
                    name = classNames [matchesIndex].upper()
                    y1,x2,y2,x1 = faceLoc
                    y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                    print (name)
                    cv2.rectangle (img, (x1,y1), (x2,y2), (0,255,0), 2)
                    cv2.putText (img, "Terdeteksi", (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                    faceList (name)
                    time.sleep(3)
                
                else:
                    y1,x2,y2,x1 = faceLoc
                    y1,x2,y2,x1 = y1*4, x2*4, y2*4, x1*4
                    cv2.rectangle (img, (x1,y1), (x2,y2), (0,255,0), 2)
                    cv2.putText (img, "Tak DiKenal", (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            
            FRAME_WINDOW.image(img)   
            cv2.waitKey(1)   
    else:
        pass
    
# DAFTAR
elif listMenu == "Daftar":
    st.title ("Masukkan Gambar")
    def load_image (image_file):
        img = Image.open (image_file)
        return img

    image_file = st.file_uploader ("Unggah Gambar", type=["png", "jpeg", "jpg"])
    if image_file is not None:
        file_details = {"FileName":image_file.name, "FileType":image_file.type}
        st.write (file_details)
        img = load_image (image_file)
        with open (os.path.join ("daftarmahasiwa", image_file.name), "wb") as f: 
            f.write (image_file.getbuffer())         
        st.success ("Saved File")
    st.warning ("Pastikan Format Foto Anda Seperti Di Bawah ini")
    st.caption ('\"Nama Lengkap_NIM.jpg/jpeg/png/\"')
    
# DATA KEHADIRAN
elif listMenu == "Kehadiran":
    df = pd.read_csv ("absensi.csv")
    st.title ("Daftar Hadir")
    st.subheader("Kelas B : Pak Sapta Nugraha")
    AgGrid (df)
    st.info (len(df))
    # DOWNLOAD
    st.download_button (label = "Download Data", data = df.to_csv(), mime = "text/csv")
 
# TENTANG
elif listMenu == "About":
    st.markdown ("<h1 style='text-align: center; color: black;'>Tentang Kami</h1>", unsafe_allow_html=True)
    #st.title ("Tentang Kami")
    st.subheader ("Anggota (Kelompok 7) : ")
    st.write ("Thantawi 2201030015 : Ketua Kelompok")
    st.write ("Nurafni Nadalita Syahfitri 2201020030 : Anggota")
    st.write ("Yuliani Syah Putri 2201020036 : Anggota")
    st.write ("Rizki Afandi Rambe 2201010020 : Anggota")
    st.write ("Rifana Bima Pradifa 2201020026 : Anggota")

# SELESAI