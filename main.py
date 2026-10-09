
import os
import re
import glob
import cv2
import numpy as np
import pytesseract

# KONFIGURASI FOLDER
FOLDER_NOMOR = "Nomor_Ijazah"
FOLDER_TTD = "Tanda_Tangan"
GROUND_TRUTH = "571012022000056"

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

SUB_FOLDERS = [
    "1_citra_asli", "2_grayscale", "3_global_thresh",
    "4_global_opening", "5_global_closing",
    "6_otsu_thresh", "7_otsu_opening",
    "8_otsu_closing", "9_perbandingan"
]

DIR_NO = os.path.join("output", "nomor_ijazah")
DIR_TTD = os.path.join("output", "ttd")

for base in [DIR_NO, DIR_TTD]:
    for sub in SUB_FOLDERS:
        os.makedirs(os.path.join(base, sub), exist_ok=True)


# METODE ENHANCEMENT
def contrast_stretch(img):
    mn, mx = img.min(), img.max()
    if mx == mn:
        return img.copy()
    return ((img.astype(np.float32) - mn) * 255 / (mx - mn)).astype(np.uint8)


def clahe(img):
    return cv2.createCLAHE(
        clipLimit=2.0, tileGridSize=(8, 8)
    ).apply(img)


def gamma_correction(img, gamma=1.5):
    table = np.array([
        ((i / 255.0) ** (1 / gamma)) * 255
        for i in range(256)
    ]).astype(np.uint8)
    return cv2.LUT(img, table)


# MENGHITUNG CER
def hitung_cer(prediksi):
    prediksi = re.sub(r"\D", "", prediksi)
    benar = GROUND_TRUTH
    dp = list(range(len(benar) + 1))

    for i, a in enumerate(prediksi, 1):
        baris = [i]
        for j, b in enumerate(benar, 1):
            baris.append(min(
                baris[-1] + 1,
                dp[j] + 1,
                dp[j - 1] + (a != b)
            ))
        dp = baris

    return dp[-1] / len(benar) * 100


# PIPELINE CITRA
def pipeline(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, global_thresh = cv2.threshold(
        gray, 127, 255, cv2.THRESH_BINARY
    )
    _, otsu_thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    kernel = np.ones((3, 3), np.uint8)
    global_open = cv2.morphologyEx(
        global_thresh, cv2.MORPH_OPEN, kernel
    )
    global_close = cv2.morphologyEx(
        global_thresh, cv2.MORPH_CLOSE, kernel
    )
    otsu_open = cv2.morphologyEx(
        otsu_thresh, cv2.MORPH_OPEN, kernel
    )
    otsu_close = cv2.morphologyEx(
        otsu_thresh, cv2.MORPH_CLOSE, kernel
    )

    steps = {
        "1_citra_asli": img,
        "2_grayscale": gray,
        "3_global_thresh": global_thresh,
        "4_global_opening": global_open,
        "5_global_closing": global_close,
        "6_otsu_thresh": otsu_thresh,
        "7_otsu_opening": otsu_open,
        "8_otsu_closing": otsu_close
    }
    return steps, gray


# MENYIMPAN GRID PERBANDINGAN
def simpan_grid(steps, folder, nama):
    gambar_list = []

    for judul, gambar in steps.items():
        if gambar.ndim == 2:
            gambar = cv2.cvtColor(gambar, cv2.COLOR_GRAY2BGR)
        gambar = gambar.copy()
        cv2.putText(
            gambar, judul, (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
        )
        gambar_list.append(gambar)

    h, w = gambar_list[0].shape[:2]
    canvas = np.full((h * 3, w * 3, 3), 255, np.uint8)

    for i, gambar in enumerate(gambar_list):
        r, c = divmod(i, 3)
        canvas[r*h:(r+1)*h, c*w:(c+1)*w] = cv2.resize(gambar, (w, h))

    cv2.imwrite(os.path.join(folder, nama), canvas)


# MEMPROSES FOLDER NOMOR ATAU TANDA TANGAN
def proses_folder(folder_input, folder_output, jenis):
    files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
        files.extend(glob.glob(os.path.join(folder_input, ext)))

    if not files:
        print(f"Gambar tidak ditemukan di folder {folder_input}")
        return

    for path in sorted(files):
        img = cv2.imread(path)
        if img is None:
            continue

        nama = os.path.basename(path)
        steps, gray = pipeline(img)

        for sub, hasil in steps.items():
            cv2.imwrite(
                os.path.join(folder_output, sub, nama), hasil
            )

        simpan_grid(
            steps,
            os.path.join(folder_output, "9_perbandingan"),
            nama
        )

        if jenis == "nomor":
            metode = {
                "Contrast Stretching": contrast_stretch(gray),
                "CLAHE": clahe(gray),
                "Gamma Correction": gamma_correction(gray)
            }

            hasil_ocr = []
            for nama_metode, citra in metode.items():
                _, biner = cv2.threshold(
                    citra, 0, 255,
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
                teks = pytesseract.image_to_string(
                    biner,
                    config="--psm 6 -c tessedit_char_whitelist=0123456789"
                )
                angka = re.sub(r"\D", "", teks)
                nilai_cer = hitung_cer(angka)
                hasil_ocr.append((nama_metode, angka, nilai_cer))

            terbaik = min(hasil_ocr, key=lambda x: x[2])
            print(
                f"{nama} | Nomor Ijazah: {terbaik[1]} | "
                f"CER: {terbaik[2]:.2f}% | "
                f"Metode terbaik: {terbaik[0]}"
            )

        else:
            # Thresholding dan morphology untuk deteksi tanda tangan
            _, biner = cv2.threshold(
                gray, 0, 255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
            kernel = np.ones((3, 3), np.uint8)
            bersih = cv2.morphologyEx(
                biner, cv2.MORPH_OPEN, kernel
            )
            bersih = cv2.morphologyEx(
                bersih, cv2.MORPH_CLOSE, kernel
            )

            rasio = cv2.countNonZero(bersih) / bersih.size
            status = "PRESENT" if rasio > 0.005 else "ABSENT"
            print(f"{nama} | Tanda Tangan: {status}")


if __name__ == "__main__":
    proses_folder(FOLDER_NOMOR, DIR_NO, "nomor")
    proses_folder(FOLDER_TTD, DIR_TTD, "ttd")
    print("\nPemrosesan selesai. Periksa folder output.")