

## Sistem Pembacaan Nomor Ijazah dan Deteksi Tanda Tangan

### 1. Deskripsi Proyek

Proyek ini dibuat untuk membaca nomor ijazah menggunakan OCR (*Optical Character Recognition*) dan mendeteksi keberadaan tanda tangan. Program menggunakan beberapa metode pengolahan citra untuk memperbaiki kualitas gambar dan membandingkan hasil pembacaan nomor ijazah berdasarkan nilai CER.

### 2. Metode yang Digunakan

* **Grayscale:** Mengubah gambar berwarna menjadi gambar keabuan.
* **Global Thresholding:** Memisahkan objek dan latar belakang menggunakan nilai ambang tetap.
* **Otsu Thresholding:** Menentukan nilai ambang secara otomatis.
* **Morphological Opening:** Mengurangi noise kecil pada gambar.
* **Morphological Closing:** Membantu menyambungkan bagian objek yang terputus.
* **OCR:** Membaca angka pada nomor ijazah menggunakan Tesseract OCR.
* **CER (Character Error Rate):** Mengukur tingkat kesalahan hasil OCR dibandingkan dengan nomor ijazah yang benar.

### 3. Struktur Folder

```text
Tugas7_PCD_F1G124005_Citra/
├── Nomor_Ijazah/
├── Tanda_Tangan/
├── output/
│   ├── nomor_ijazah/
│   │   ├── 1_citra_asli/
│   │   ├── 2_grayscale/
│   │   ├── 3_global_thresh/
│   │   ├── 4_global_opening/
│   │   ├── 5_global_closing/
│   │   ├── 6_otsu_thresh/
│   │   ├── 7_otsu_opening/
│   │   ├── 8_otsu_closing/
│   │   └── 9_perbandingan/
│   └── ttd/
│       ├── 1_citra_asli/
│       ├── 2_grayscale/
│       ├── 3_global_thresh/
│       ├── 4_global_opening/
│       ├── 5_global_closing/
│       ├── 6_otsu_thresh/
│       ├── 7_otsu_opening/
│       ├── 8_otsu_closing/
│       └── 9_perbandingan/
├── main.py
└── README.md
```

Folder `Nomor_Ijazah` berisi gambar yang digunakan untuk pengujian OCR, sedangkan folder `Tanda_Tangan` berisi gambar untuk pengujian deteksi tanda tangan. Folder `output` digunakan untuk menyimpan hasil setiap tahap pengolahan dan gambar perbandingan.

### 4. Cara Menjalankan Program

**Langkah 1.** Pastikan Python dan Tesseract OCR sudah terpasang di komputer.

**Langkah 2.** Buka terminal di folder proyek, kemudian instal pustaka yang diperlukan:

```bash
python -m pip install opencv-python numpy pytesseract
```

**Langkah 3.** Periksa lokasi Tesseract OCR pada kode `main.py`. Sesuaikan dengan lokasi instalasi di komputer.

**Langkah 4.** Jalankan program melalui terminal:

```bash
python main.py
```

**Langkah 5.** Setelah program selesai, periksa folder `output` untuk melihat gambar hasil pengolahan dan perbandingan.

### 5. Hasil dan Evaluasi

Program menampilkan nomor ijazah hasil OCR, nilai CER, metode enhancement terbaik, serta status tanda tangan berupa `PRESENT` atau `ABSENT`.

Metode enhancement yang dibandingkan adalah Contrast Stretching, CLAHE, dan Gamma Correction. Metode dengan nilai CER terendah dipilih sebagai metode terbaik untuk setiap gambar yang diuji. Semakin rendah nilai CER, semakin sedikit kesalahan karakter pada hasil OCR.

### 6. Kesimpulan

Program ini menerapkan pengolahan citra digital untuk membantu membaca nomor ijazah dan mendeteksi keberadaan tanda tangan. Hasil pengujian digunakan untuk membandingkan metode enhancement berdasarkan nilai CER serta melihat hasil deteksi tanda tangan pada gambar yang dimasukkan.
