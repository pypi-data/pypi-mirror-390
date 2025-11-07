#   _____      _    _            _ _   _           
#  / ____|    | |  | |          | | | | |          
# | |   ______| |__| | ___  __ _| | |_| |__  _   _ 
# | |  |______|  __  |/ _ \/ _` | | __| '_ \| | | |  Healthy library for Python
# | |____     | |  | |  __/ (_| | | |_| | | | |_| |  Version 0.2.6
#  \_____|    |_|  |_|\___|\__,_|_|\__|_| |_|\__, |  Github: https:github.com/trgchinhh/library-C_healthy
#                                             __/ |
#                                            |___/ 
# (!) PROGRAM: BODY INDEX CALCULATOR
# (!) AUTHOR: NGUYEN TRUONG CHINH (NTC++)

# /**************************************************************************\
#  * Update new version [0.2.5] -> [0.2.6]
#  * Feature: including indexing and giving advice
#  * This URL lib C-heathy: https://github.com/trgchinhh/library-C_healthy
#  * We will update this library soon
# \**************************************************************************/


import math, os


def BMI(can_nang : int, chieu_cao : float):
    try:
        if(can_nang > 0 and chieu_cao > 0):
            return round(can_nang / (chieu_cao ** 2), 2)
        else:
            return "Invalid input"   
    except Exception as e:
        raise ValueError(f"[{e}]")


def BMR(gioi_tinh ,can_nang, chieu_cao, tuoi):
    if(not GenderTest(gioi_tinh)):
        return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
    try:
        if(can_nang > 0 and chieu_cao > 0 and tuoi > 0):
            chieu_cao = chieu_cao * 100
            if(gioi_tinh.lower() == "nu"):
                #BMR = 655 + (9,6 × trọng lượng tính bằng kg) + (1,8 × chiều cao tính bằng cm) – (4,7 × tuổi tính theo năm)
                return round((655 + (9.6 * can_nang) + (1.8 * chieu_cao) - (4.7 * tuoi)), 2)
            else:
                #Nam giới: BMR = 66 + (13,7 × trọng lượng tính bằng kg) + (5 × chiều cao tính bằng cm) – (6,8 × tuổi tính theo năm)
                return round((66 + (13.7 * can_nang) + (5 * chieu_cao) - (6.8 * tuoi)), 2) 
        else:
            return "Invalid input"
    except Exception as e:
        raise ValueError(f"[{e}]")


def TDEE(gioi_tinh, can_nang, chieu_cao, tuoi, chi_so_R):
    try:
        if(not GenderTest(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        he_so_van_dong = {
            1: 1.2,
            2: 1.375,
            3: 1.55,
            4: 1.725,
            5: 1.9
        }
        chi_so_bmr = BMR(gioi_tinh, can_nang, chieu_cao, tuoi)
        if(chi_so_R in he_so_van_dong):
            return round((chi_so_bmr * he_so_van_dong[chi_so_R]), 2)
        else:
            valid_keys = ", ".join(str(k) for k in he_so_van_dong.keys())
            raise ValueError(f"Chi so van dong khong hop le! Chon 1 trong cac gia tri: {valid_keys}")
    except Exception as e:
        raise ValueError(f"[{e}]")


def WHR(gioi_tinh, vong_eo, vong_hong):
    try:
        if(not GenderTest(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        if(vong_eo <= 0 or vong_hong <= 0):
            return "Invalid input"
        return round((vong_eo / vong_hong), 2)
    except Exception as e:
        raise ValueError(f"[{e}]") 


def LBM(gioi_tinh, can_nang, chieu_cao):
    try:
        if(not GenderTest(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        chieu_cao = chieu_cao * 100    
        if(gioi_tinh.lower() == "nam"):
            lbm = round(((0.32810 * can_nang) + (0.33929 * chieu_cao) - 29.5336), 2)
        else:
            lbm = round(((0.29569 * can_nang) + (0.41813 * chieu_cao) - 43.2933), 2) 
        return lbm    
    except Exception as e:
        raise ValueError(f"[{e}]")


def FFMI(gioi_tinh, can_nang, chieu_cao):
    try:
        if(not GenderTest(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        lbm = LBM(gioi_tinh, can_nang, chieu_cao)
        ffmi = round(lbm / (chieu_cao**2), 2)
        return ffmi
    except Exception as e:
        raise ValueError(f"[{e}]")


def RFM(vong_eo, chieu_cao):
    try:
        chieu_cao = chieu_cao * 100
        rfm = round(64 - (4 * (vong_eo / chieu_cao)), 2)
        return rfm
    except Exception as e:
        raise ValueError(f"[{e}]")


def BFP(gioi_tinh, can_nang, chieu_cao, tuoi):
    try:
        if(not GenderTest(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        bmi = BMI(can_nang, chieu_cao) 
        if(gioi_tinh.lower() == "nam"):
            bfp = round((1.20 * bmi) + (0.23 * tuoi) - 16.2, 2)
        else:
            bfp = round((1.20 * bmi) + (0.23 * tuoi) - 5.4, 2)
        return bfp
    except Exception as e:
        raise ValueError(f"[{e}]")


def BBW(can_nang):
    try:
        luong_nuoc = round(can_nang * 0.033, 2)
        return luong_nuoc
    except Exception as e:
        raise ValueError(f"[{e}]")


def IBW(gioi_tinh, chieu_cao):
    try:
        if(not GenderTest(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        chieu_cao = chieu_cao * 100
        if(gioi_tinh.lower() == "nam"):
            ibw = round(50 + 2.3 * (chieu_cao - 152.4) / 2.54, 2)
        else:
            ibw = round(45.5 + 2.3 * (chieu_cao - 152.4) / 2.54, 2)
        return ibw
    except Exception as e:
        raise ValueError(f"[{e}]")


def MA(gioi_tinh, can_nang, chieu_cao, tuoi):
    try:
        if(not GenderTest(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        bmr = BMR(gioi_tinh, can_nang, chieu_cao, tuoi)
        bmr_tb_nam = {
            (18, 30): 1900,
            (31, 50): 1800,
            (51, 70): 1700,
            (71, 150): 1600
        }
        bmr_tb_nu = {
            (18, 30): 1500,
            (31, 50): 1400,
            (51, 70): 1300,
            (71, 150): 1200
        }
        bang_bmr = bmr_tb_nam if gioi_tinh.lower() == "nam" else bmr_tb_nu
        bmr_tb = None
        for gioi_han_tuoi, tb_bmr in bang_bmr.items():
            if(gioi_han_tuoi[0] <= tuoi <= gioi_han_tuoi[1]):
                bmr_tb = tb_bmr
                break
        if bmr_tb is None:
            return(f"Tuoi '{tuoi}' khong duoc ho tro !") 
        he_so_dieu_chinh = (bmr - bmr_tb) / 100  
        ma = int(round(tuoi - he_so_dieu_chinh))  
        return ma
    except Exception as e:
        raise ValueError(f"[{e}]")


def VFR(vong_eo, vong_hong):
    try:
        vfr = round(vong_eo / vong_hong, 2)
        return vfr
    except Exception as e:
        raise ValueError(f"[{e}]")


def BSA(chieu_cao, can_nang):
    try: 
        chieu_cao = chieu_cao * 100
        bsa = round(math.sqrt((chieu_cao * can_nang) / 3600), 2)
        return bsa 
    except Exception as e:
        raise ValueError(f"[{e}]")


def VO2MAX(nhip_tim_toi_da, nhip_tim_nghi):
    try:
        Vo2max = 15 * (nhip_tim_toi_da / nhip_tim_nghi)
        return Vo2max            
    except Exception as e:
        raise ValueError(f"[{e}]")


def HSI(gioi_tinh, can_nang, chieu_cao, tuoi, cholesterol, huyet_ap):
    try:
        if(not GenderTest(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        bmi = BMI(can_nang, chieu_cao)
        bfp = BFP(gioi_tinh, can_nang, chieu_cao, tuoi)
        hsi = round((bmi * 0.4 + bfp * 0.3 + huyet_ap * 0.2 + cholesterol * 0.1) / 4, 2)
        return hsi 
    except Exception as e:
        raise ValueError(f"[{e}]")     


def MMI(gioi_tinh, can_nang, chieu_cao):
    try:
        ffmi = FFMI(gioi_tinh, can_nang, chieu_cao)
        mmi = round(ffmi / can_nang, 2)
        return mmi 
    except Exception as e:
        raise ValueError(f"[{e}]")


def BFM(gioi_tinh, can_nang, chieu_cao, tuoi):
    try:
        if(not GenderTest(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        bfp = BFP(gioi_tinh, can_nang, chieu_cao, tuoi)
        bfm = round(can_nang * (bfp / 100), 2)
        return bfm 
    except Exception as e:
        raise ValueError(f"[{e}]")                   
     

def GenderTest(gioi_tinh):
    gioi_tinh_cho_phep = ["nam", "nu"]
    if isinstance(gioi_tinh, (int, float, complex)):  
        return False
    if gioi_tinh.lower() not in gioi_tinh_cho_phep:
        return False
    else: 
        return True      


def NABMI(bmi: float):
    if bmi < 18.5:
        return "Bổ sung thêm protein và tinh bột"
    elif bmi < 25:
        return "Duy trì chế độ ăn cân bằng và luyện tập đều đặn"
    elif bmi < 30:
        return "Giảm tinh bột và chất béo, tăng cường luyện tập"
    else:
        return "Cần giảm cân ngay"


def NABMR(gender: str, bmr: float):
    return f"Đảm bảo lượng calo tiêu thụ phù hợp với BMR: {bmr} kcal/ngày"


def NATDEE(gender: str, tdee: float):
    return f"Ăn uống theo TDEE: {tdee} kcal/ngày để duy trì cân nặng"


def NAWHR(whr: float):
    if whr < 0.9:
        return "Tỷ lệ eo/hông bình thường"
    else:
        return "Chú ý giảm mỡ vùng bụng"


def NALBM(lbm: float):
    return f"Duy trì cơ bắp: {lbm} kg"


def NAFFMI(ffmi: float):
    return f"Kiểm tra cơ bắp chuẩn: {ffmi}"


def NARFM(rfm: float):
    return f"Theo dõi mỡ cơ thể: {rfm}%"


def NABFP(bfp: float):
    return f"Tỷ lệ mỡ cơ thể: {bfp}%, điều chỉnh chế độ ăn uống luyện tập"


def NABBW(bbw: float):
    return f"Cân nặng cơ bản: {bbw} kg"


def NAIBW(ibw: float):
    return f"Cân nặng lý tưởng: {ibw} kg"


def NAMA(ma: float):
    return f"Mức độ trao đổi chất: {ma}"


def NAVFR(vfr: float):
    return f"Chỉ số mỡ nội tạng: {vfr}"


def NABSA(bsa: float):
    return f"Diện tích cơ thể: {bsa} m²"


def NAVO2MAX(vo2max: float):
    return f"Khả năng hô hấp: {vo2max} ml/kg/phút"


def NAHSI(hsi: float):
    return f"Chỉ số gan: {hsi}"


def NAMMI(mmi: float):
    return f"Chỉ số cơ bắp: {mmi}"


def NABFM(bfm: float):
    return f"Khối lượng mỡ cơ thể: {bfm} kg"


def INSTRUCT():
    instruct = """Hướng dẫn sử dụng các hàm tính toán chỉ số cơ thể và lời khuyên dinh dưỡng:

1. **BMI**: Nhập theo cú pháp BMI([cân nặng] [chiều cao]).
   Ví dụ: BMI(60, 1.75)
   Lời khuyên: NABMI(BMI)

2. **BMR**: Nhập theo cú pháp BMR([giới tính] [cân nặng], [chiều cao], [tuổi]).
   Ví dụ: BMR('nam', 70, 1.75, 25)
   Lời khuyên: NABMR(giới tính, BMR)

3. **TDEE**: Nhập theo cú pháp TDEE([giới tính] [cân nặng], [chiều cao], [tuổi], [chỉ số vận động]).
   Ví dụ: TDEE('nam', 70, 1.75, 25, 3)
   Lời khuyên: NATDEE(giới tính, TDEE)

4. **WHR**: Nhập theo cú pháp WHR([giới tính] [vòng eo] [vòng hông]).
   Ví dụ: WHR('nữ', 70, 90)
   Lời khuyên: NAWHR(WHR)

5. **LBM**: Nhập theo cú pháp LBM([giới tính] [cân nặng] [chiều cao]).
   Ví dụ: LBM('nam', 70, 1.75)
   Lời khuyên: NALBM(LBM)

6. **FFMI**: Nhập theo cú pháp FFMI([giới tính] [cân nặng] [chiều cao]).
   Ví dụ: FFMI('nam', 70, 1.75)
   Lời khuyên: NAFFMI(FFMI)

7. **RFM**: Nhập theo cú pháp RFM([vòng eo] [chiều cao]).
   Ví dụ: RFM(70, 1.75)
   Lời khuyên: NARFM(RFM)

8. **BFP**: Nhập theo cú pháp BFP([giới tính] [cân nặng] [chiều cao] [tuổi]).
   Ví dụ: BFP('nam', 70, 1.75, 25)
   Lời khuyên: NABFP(BFP)

9. **BBW**: Nhập theo cú pháp BBW([cân nặng]).
   Ví dụ: BBW(70)
   Lời khuyên: NABBW(BBW)

10. **IBW**: Nhập theo cú pháp IBW([giới tính] [chiều cao]).
    Ví dụ: IBW('nam', 1.75)
    Lời khuyên: NAIBW(IBW)

11. **MA**: Nhập theo cú pháp MA([giới tính] [cân nặng] [chiều cao] [tuổi]).
    Ví dụ: MA('nam', 70, 1.75, 25)
    Lời khuyên: NAMA(MA)

12. **VFR**: Nhập theo cú pháp VFR([vòng eo] [vòng hông]).
    Ví dụ: VFR(70, 90)
    Lời khuyên: NAVFR(VFR)

13. **BSA**: Nhập theo cú pháp BSA([chiều cao] [cân nặng]).
    Ví dụ: BSA(1.75, 70)
    Lời khuyên: NABSA(BSA)

14. **VO2MAX**: Nhập theo cú pháp VO2MAX([nhịp tim tối đa] [nhịp tim nghỉ]).
    Ví dụ: VO2MAX(200, 70)
    Lời khuyên: NAVO2MAX(VO2MAX)

15. **HSI**: Nhập theo cú pháp HSI([giới tính] [cân nặng] [chiều cao] [tuổi] [cholesterol] [huyết áp]).
    Ví dụ: HSI('nam', 70, 1.75, 25, 200, 120)
    Lời khuyên: NAHSI(HSI)

16. **MMI**: Nhập theo cú pháp MMI([khối lượng cơ bắp] [cân nặng]).
    Ví dụ: MMI(30, 70)
    Lời khuyên: NAMMI(MMI)

17. **BFM**: Nhập theo cú pháp BFM([giới tính] [cân nặng] [chiều cao] [tuổi]).
    Ví dụ: BFM('nam', 70, 1.75, 25)
    Lời khuyên: NABFM(BFM)
"""

    file_name = "huong_dan_su_dung.txt"
    try:
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                content = f.read()
                if content == instruct:
                    return "Đã có file hướng dẫn"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(instruct)
        full_path = os.path.abspath(file_name)
        return f"Đã tạo file hướng dẫn tại đường dẫn: {full_path}"
    except Exception as e:
        return f"Không thể tạo file hướng dẫn: {e}"

# ---------------------------------------------------- 
# Copyright by NTC++ 11/07/2025 
# ---------------------------------------------------- 