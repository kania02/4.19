# Instruksi untuk Copilot: Port kernel 4.19.325 ke Samsung A02

Update terakhir: 25 Nov 2026. Baca SEMUA sebelum menjawab.

## Gaya jawaban (WAJIB)
- Bahasa Indonesia santai (gw/lu), super singkat.
- User bilang: "ga perlu penjelasan apapun, gw ga ngerti, cuma command aja biar cepet ping-pong".
- Balasan = SATU command dalam blok kode siap salin, tanpa penjelasan. Info hanya kalau krusial, maks 1-2 kalimat.
- Label setiap klaim: **TERBUKTI** (terlihat di output/file) atau **DUGAAN** (belum terbukti). Jangan mengarang. Jangan klaim sebelum ada bukti.
- Penutup: "Copas hasilnya dari terminal." atau "Upload <file> setelah selesai".
- Kalau user bilang "jangan kasih command", turuti.
- Jangan ulang langkah yang sudah selesai. Jangan salah sebut versi kernel (cek `uname -v`).
- JANGAN pernah minta atau tulis PAT/token.

## Di mana command dijalankan
- **Codespaces (bash)**: build, edit file, git. Awali dengan `clear && `. `adb` TIDAK ada di Codespaces.
- **PC Windows 7 (cmd, BUKAN PowerShell)**: semua `adb`. Awali dengan `cls && ` (kecuali output perlu terlihat setelah findstr/redirect). Kerja di `D:\DAPUR_GODOG`, file di `D:\Downloads_Baru`.
- **adb shell di HP**: tanpa `clear`.
- Selalu tulis jelas command itu untuk Codespaces atau cmd. JANGAN kasih sintaks bash (`for`, `$()`) untuk dipaste di cmd.

## Aturan cmd Windows
- Jangan pakai `\"` di dalam `adb shell "..."`; pakai kutip tunggal.
- Jangan awk dengan kutip di cmd. Jangan nested kutip di findstr.
- Pakai `( a & b )`, bukan `{ }`.
- Jangan `2>&1` di cmd. `2>/dev/null` untuk `dd` lewat `adb exec-out` WAJIB.
- findstr: JANGAN pakai `[PWM]` (dibaca regex); pakai kata polos `PWM`.
- Jangan paste beberapa command sekaligus di cmd. Jangan bikin .bat/skrip debug.
- JANGAN pakai `adb wait-for-device` (macet di OFox). Reboot manual oleh user. JANGAN `timeout /t` lama.
- `grep` DI HP RUSAK (hasil bisa 0/salah): filter output di sisi PC pakai findstr.

## Tujuan
- Kernel 4.19 hasil build Codespaces harus boot sampai homescreen stabil: layar BISA DISENTUH, navbar muncul, TIDAK hang/reboot sendiri, tanpa popup peringatan.
- Pembanding yang beres: kernel 4.14.336 (`boot_64_336.img`). `boot_k419_mmc43.img` dipakai HANYA sebagai base repack (ramdisk + header).
- Target "adb terbaca < 67 dtk" di-skip dulu.
- Driver/HAL A02 dipertahankan. Aturan user: stop kalau 3x trial gagal per perubahan.

## Lingkungan
**HP**: A02 stock (adb model SM_A125F, device a02xx), Android 12 One UI Core 4.1, root Magisk, OrangeFox (OFox). Boot = `/dev/block/mmcblk0p35` (tanpa A/B). Serial adb RR8R2003LWP. Di Android `su` TIDAK ada di adb: pakai `adb shell` langsung. Flash/tarik boot hanya bisa di OFox (adb di OFox sudah root). `sys.boot.reason` selalu "wdt". `/sys/class/power_supply`, `/sys/class/thermal`, `/sys/class/leds` KOSONG.

**Codespaces** (akun @kania02): `/workspaces/4.19`, branch `port`, origin `https://github.com/kania02/4.19`. Commit terakhir ter-push: `13f92e20f` ("br2: defconfig + I2C_MTK").
- Root repo = kernel 4.14.336. `kernel-4.19.325/` = tree 4.19.325. `ref_oc/` = pembanding 4.14 yang jalan (defconfig: `ref_oc/arch/arm64/configs/a02_64_defconfig`).
- `out/` di-gitignore. Backup config: `/workspaces/4.19/config_br2_backup` (ter-commit), `out/.config.pre_i2c`, `out/.config.pre_*`. Setelah build berhasil: savedefconfig + commit/push, backup `out/.config`.
- `Kconfig.bak_aee1` untracked (abaikan).
- defconfig: `arch/arm64/configs/a02_64_bootstrap_defconfig`. Toolchain: clang 18.1.3, ld.lld, aarch64-linux-gnu-gcc.

**Boot image**: header v2, page 2048, 25165824 byte. Base repack `boot_k419_mmc43.img` ada di `/workspaces/4.19/`. Kernel string `4.19.325-a02-4.19-port-bootstrap`; angka `#N` di `uname -v` memastikan image yang jalan.

**Image di `D:\Downloads_Baru`**:
- `boot_backup_rm2.img` (MD5 54f9d60d029c88c652c77e50d4bf200f, kernel #42, fallback aman, layar nyala)
- `boot_k419_br1.img` (MD5 005c1673a8e212a5f205562f056085f8, kernel #5, layar GELAP)
- `boot_k419_br2.img` (MD5 8b99ea60f5c5286b1d9725fb81fe33bc, kernel #6, layar NYALA) <- SEKARANG ter-flash di p35
- Image tes berikutnya: `boot_k419_br3.img`, `br4`, dst.

## Aturan edit file (WAJIB)
- Backup dulu sebelum edit: `cp --update=none file file.bak_<kode>`. Jangan timpa skrip asli.
- Edit pakai `python3` heredoc dengan cek pola (count harus pas) sebelum menulis.
- Jangan edit file otomatis tanpa user lihat; tampilkan sebagai command.

## Build (MANUAL INCREMENTAL)
- JANGAN pakai `build_kernel.sh`/skrip/z64. JANGAN `make clean`. Jalankan build sendiri lewat agent.
- User WAJIB melihat progres build penuh (tanpa grep/head/tail di proses build), tapi di akhir ada ringkasan error.
- Ubah CONFIG apa pun = rebuild hampir penuh (user benci nunggu): gabungkan perubahan config jadi satu build.

Pola 1 command (Codespaces). Bagian `[...]` opsional untuk ubah config:

```bash
clear && cd /workspaces/4.19/kernel-4.19.325 && [scripts/config --file out/.config ... && make O=out ARCH=arm64 CC=clang LD=ld.lld CROSS_COMPILE=aarch64-linux-gnu- olddefconfig &&] rm -f out/arch/arm64/boot/Image.gz /workspaces/4.19/build_err.log && make -k O=out ARCH=arm64 CC=clang LD=ld.lld CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc) Image.gz mediatek/mt6739.dtb 2> >(tee /workspaces/4.19/build_err.log >&2); sleep 2; echo; echo "=== ERROR SAJA (tanpa warning)"; grep -n -E "error:|undefined symbol|Error [0-9]+|\*\*\*" /workspaces/4.19/build_err.log | head -n 40; [ -f out/arch/arm64/boot/Image.gz ] && cat out/arch/arm64/boot/Image.gz out/arch/arm64/boot/dts/mediatek/mt6739.dtb > out/arch/arm64/boot/Image.gz-dtb && cd /workspaces/4.19 && python3 repack_a02.py boot_k419_mmc43.img kernel-4.19.325/out/arch/arm64/boot/Image.gz-dtb boot_k419_<nama>.img && md5sum boot_k419_<nama>.img
```

Savedefconfig + commit (Codespaces):

```bash
cd kernel-4.19.325 && cp out/.config /workspaces/4.19/config_<nama>_backup && make O=out ARCH=arm64 CC=clang LD=ld.lld CROSS_COMPILE=aarch64-linux-gnu- savedefconfig && cp out/defconfig arch/arm64/configs/a02_64_bootstrap_defconfig && cd /workspaces/4.19 && git add ... && git commit && git push origin port
```

Cmdline repack: `bootopt=64S3,32N2,64N2 androidboot.selinux=permissive ignore_loglevel nohlt panic=0 clk_ignore_unused`. Apakah `repack_a02.py` bisa ganti cmdline: BELUM dicek.

## Command adb standar (cmd Windows, user yang jalankan)
Reboot ke OFox:

```
cls && adb reboot recovery
```

Tarik boot dari HP (di OFox; ukuran harus 25165824):

```
cls && adb exec-out "dd if=/dev/block/mmcblk0p35 bs=4M count=6 2>/dev/null" > D:\Downloads_Baru\<nama>.img && dir D:\Downloads_Baru\<nama>.img && certutil -hashfile D:\Downloads_Baru\<nama>.img MD5
```

Flash boot (HP di OFox) + cek MD5 p35 + timer boot sampai adb terdeteksi (ganti `<img>`):

```
cls && ( adb exec-in "dd of=/dev/block/mmcblk0p35 bs=4M conv=fsync" < D:\Downloads_Baru\<img> & echo ERRORLEVEL_FLASH=%errorlevel% & adb shell "sync; dd if=/dev/block/mmcblk0p35 bs=4M count=6 2>/dev/null | md5sum" & certutil -hashfile D:\Downloads_Baru\<img> MD5 ) > D:\DAPUR_GODOG\md5_flash.txt && type D:\DAPUR_GODOG\md5_flash.txt && del /f /q D:\DAPUR_GODOG\log\*.* & ( for /d %i in (D:\DAPUR_GODOG\log\*) do rd /s /q "%i" ) && @echo off & adb reboot & echo Pencet bareng (power di HP dan tombol apapun di PC) & pause >nul & cmd /v:on /c "@echo off & set S=!time: =0! & set /a a=1!S:~0,2!-100 >nul & set /a b=1!S:~3,2!-100 >nul & set /a c=1!S:~6,2!-100 >nul & set /a SS=a*3600+b*60+c >nul & for /l %n in (1,1,900) do ( set E=!time: =0! & set /a a=1!E:~0,2!-100 >nul & set /a b=1!E:~3,2!-100 >nul & set /a c=1!E:~6,2!-100 >nul & set /a T=a*3600+b*60+c-SS >nul & (if !T! lss 0 set /a T+=86400 >nul) & cls & type D:\DAPUR_GODOG\md5_flash.txt & echo WAKTU MULAI : !S:~0,2!.!S:~3,2!.!S:~6,2! & echo WAKTU BOOTING : !T! detik & adb devices -l 2>nul | findstr transport_id >nul && (echo. & echo FINISH..!! WAKTU SELESAI : !E:~0,2!.!E:~3,2!.!E:~6,2! - dalam !T! detik & adb devices -l & adb shell uname -mr & exit ) || ( ping -n 2 127.0.0.1 >nul ) )" & echo on
```

## Aturan tes (WAJIB)
- USER BENCI NUNGGU: jangan suruh tes yang butuh nunggu ratusan detik tanpa alasan kuat. Hindari ubah config kecuali perlu. Hindari tes yang memaksa hang (tombol power user mulai aus).
- Android lemot/RAM mepet: utamakan baca `/proc`, `/sys`, `dmesg`, `getprop`; output pendek.
- HP sering hang: ambil data segera setelah adb terdeteksi. Ambil `dmesg` SEBELUM ~100 dtk (ring buffer cepat tertimpa).
- Cek nama file image yang benar sebelum kasih command flash.
- Pastikan `adb reboot recovery` tetap masuk OFox di tiap image (sec_rr sudah beres).
- JANGAN ulang dump_reg massal modul 0-15 lewat dispsys (memicu hang).

## Kemajuan (TERBUKTI)
- Layar gelap br1 SELESAI. Penyebab: `CONFIG_I2C_MTK=y` ada di ref_oc tapi TIDAK ada di `out/.config` 4.19, jadi bus I2C0 tidak ada dan IC backlight lm36274@11 tidak pernah probe. Setelah `scripts/config -e I2C_MTK`: br2 boot, dmesg `lcd panel: lm36274_probe: i2c-0 lm36274@11` muncul, layar NYALA, peringatan manufaktur hilang.
- Pelajaran: filter config sebelumnya meloloskan I2C_MTK. Bandingkan menyeluruh semua `=y` di `ref_oc/arch/arm64/configs/a02_64_defconfig` yang tidak ada/beda di `out/.config`.
- `lcd_ldo: disabling` (~31-35 dtk) sama di rm2 dan br1: BUKAN penyebab layar gelap.
- adb terdeteksi br2: 79 dtk. Boot_completed jalan.

## Masalah terbuka: popup "SSRM Warning"
- TERBUKTI: `dumpsys window` mCurrentFocus = `com.sec.android.sdhms` saat popup tampil.
- TERBUKTI (logcat sdhms): "Error occurred while parsing siop doc : limiter(GPUFreqMax) has invalid value - 395000" dan "- 482500", lalu "Fails to parse policy XML".
- TERBUKTI: `/sys/class/power_supply/battery/capacity` dan `.../prev_battery_info` ENOENT; `/sys/class/switch/uart3/state` ENOENT; `/dev/cpuset/audio-app/cpus` ENOENT; "WPC_EXIST_CHECKING_PATH isExist=false". Connect ke `vendor.samsung.hardware.thermal@1.0::ISehThermal` sukses; "TM limiter size: 0".
- TERBUKTI: tabel OPP GPU 4.19 (`cat /proc/gpufreq/gpufreq_opp_dump`): 450000/400000/350000/290000 KHz. Policy sdhms minta 395000 & 482500, tidak ada yang cocok.
- TERBUKTI: file OPP = `drivers/misc/mediatek/base/power/mt6739/mtk_gpufreq.c` (di ref_oc dan kernel-4.19.325). Baris 188: ref_oc `#define GPU_DVFS_MAX_FREQ      GPU_DVFS_FREQ0 /* KHz */` vs 4.19 `#define GPU_DVFS_MAX_FREQGPU_DVFS_FREQ0 /* KHz */` (whitespace hilang; kemungkinan file ter-reformat).
- DUGAAN: popup dipicu (a) GPU OPP/limiter tidak cocok dgn policy sdhms, dan/atau (b) baterai/thermal sysfs tidak ada. Belum dicek: apakah rm2 juga menampilkan popup, dan tabel OPP GPU rm2/ref_oc.

## Sisa masalah lain (dari rm2, belum dicek ulang di br2)
- HP hang/mati acak ~176-700 dtk (adb hilang, force reboot Vol Down+Power). Tidak ada panic/oops, pstore kosong.
- Navbar hilang (`user_setup_complete=0`).
- PMIC mt6358 irq=199 err -524, `PWM` Cannot find LED node (di rm2 juga ada, bukan penyebab), cmdq ioctl -22, eMMC hanya HS 52MHz.
- Modul power ref_oc belum dibawa: cpuidle_v3, cpuhotplug, eem_v2, upower_v2, mcdi, dcm_v1, spm_v4. Baterai/charger/RTC belum jalan.

## Langkah berikut (urut)
1. Diff tabel OPP GPU (Codespaces), hasilnya BELUM dilihat:
   ```bash
   clear && cd /workspaces/4.19 && diff ref_oc/drivers/misc/mediatek/base/power/mt6739/mtk_gpufreq.c kernel-4.19.325/drivers/misc/mediatek/base/power/mt6739/mtk_gpufreq.c | head -n 60 ; diff ref_oc/drivers/misc/mediatek/base/power/mt6739/mtk_gpufreq.c kernel-4.19.325/drivers/misc/mediatek/base/power/mt6739/mtk_gpufreq.c | grep -c "^[<>]"
   ```
2. Bandingkan menyeluruh semua CONFIG `=y` ref_oc defconfig vs `out/.config` (cari yang hilang seperti I2C_MTK). Gabungkan perbaikan jadi SATU build (br3).
3. Cek apakah popup SSRM juga muncul di rm2 / OPP GPU ref_oc (`cat /proc/gpufreq/gpufreq_opp_dump` di rm2).
4. Baterai/power_supply dan thermal sysfs: bandingkan modul ref_oc (battery/charger/fuel gauge) yang belum dibawa.
5. Setelahnya: pstore/ramoops, hang acak (modul power ref_oc, PMIC irq -524, DVFS), navbar, eMMC hs200, RTC.
