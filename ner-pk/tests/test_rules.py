"""
Unit tests for deterministic regex engine (rules.py).
Contains 35+ test cases covering complex Pakistani formats, variations,
and negative counter-examples across all pattern categories.
"""

import unittest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rules import extract_regex_entities


class TestRegexEntityExtraction(unittest.TestCase):

    def _assert_entity(self, text, expected_label, expected_substr):
        entities = extract_regex_entities(text)
        found = [e for e in entities if e["label"] == expected_label and expected_substr in e["text"]]
        self.assertTrue(
            len(found) > 0,
            f"Expected {expected_label} containing '{expected_substr}' in text: '{text}'. Found: {entities}"
        )

    # --------------------------------------------------------------------------
    # 1. PHONE_NUMBER TESTS (Mobile, Landline, Toll-Free)
    # --------------------------------------------------------------------------
    def test_phone_plus_92_mobile(self):
        self._assert_entity("Contact us at +92 300 1234567 for inquiries.", "PHONE_NUMBER", "+92 300 1234567")

    def test_phone_0092_mobile(self):
        self._assert_entity("Direct line is 0092 321 7654321.", "PHONE_NUMBER", "0092 321 7654321")

    def test_phone_standard_mobile_hyphen(self):
        self._assert_entity("His cell number is 0300-1234567.", "PHONE_NUMBER", "0300-1234567")

    def test_phone_standard_mobile_space(self):
        self._assert_entity("Helpline mobile: 0333 9876543.", "PHONE_NUMBER", "0333 9876543")

    def test_phone_karachi_landline(self):
        self._assert_entity("Call head office on 021-34567890.", "PHONE_NUMBER", "021-34567890")

    def test_phone_lahore_landline(self):
        self._assert_entity("Lahore office: 042-99201234.", "PHONE_NUMBER", "042-99201234")

    def test_phone_islamabad_landline_parens(self):
        self._assert_entity("Secretariat telephone (051) 9201234.", "PHONE_NUMBER", "(051) 9201234")

    def test_phone_toll_free(self):
        self._assert_entity("For free complaints dial 0800-12345.", "PHONE_NUMBER", "0800-12345")

    # --------------------------------------------------------------------------
    # 2. ID_NUMBER (CNIC) TESTS
    # --------------------------------------------------------------------------
    def test_cnic_standard_hyphenated_1(self):
        self._assert_entity("Candidate CNIC: 42101-1234567-1 was confirmed.", "ID_NUMBER", "42101-1234567-1")

    def test_cnic_standard_hyphenated_2(self):
        self._assert_entity("Registered voter 35201-7654321-9.", "ID_NUMBER", "35201-7654321-9")

    def test_cnic_standard_hyphenated_3(self):
        self._assert_entity("Identification code 61101-9876543-3 verified.", "ID_NUMBER", "61101-9876543-3")

    def test_cnic_unhyphenated_with_context(self):
        self._assert_entity("National identity CNIC: 3520112345671 verified.", "ID_NUMBER", "3520112345671")

    def test_cnic_unhyphenated_urdu_context(self):
        self._assert_entity("امیدوار کا شناختی کارڈ 4210198765432 تصدیق شدہ ہے۔", "ID_NUMBER", "4210198765432")

    # --------------------------------------------------------------------------
    # 3. MONEY TESTS (PKR, Rs, USD, lakh, crore, Urdu)
    # --------------------------------------------------------------------------
    def test_money_rs_crore(self):
        self._assert_entity("The project budget is Rs 45.8 crore.", "MONEY", "Rs 45.8 crore")

    def test_money_rs_dot_billion(self):
        self._assert_entity("Allocated Rs. 1.5 billion for reconstruction.", "MONEY", "Rs. 1.5 billion")

    def test_money_pkr_numeric(self):
        self._assert_entity("Penalty imposed was PKR 500,000.", "MONEY", "PKR 500,000")

    def test_money_pkr_crore(self):
        self._assert_entity("Revenues reached PKR 12.5 crore this quarter.", "MONEY", "PKR 12.5 crore")

    def test_money_rs_lakh(self):
        self._assert_entity("The loan totaled Rs 50 lakh.", "MONEY", "Rs 50 lakh")

    def test_money_usd_billion(self):
        self._assert_entity("Remittances reached USD 50 billion.", "MONEY", "USD 50 billion")

    def test_money_dollar_symbol(self):
        self._assert_entity("International grant of $100 million was approved.", "MONEY", "$100 million")

    def test_money_urdu_crore(self):
        self._assert_entity("حکومت نے 15 کروڑ روپے جاری کر دیے۔", "MONEY", "15 کروڑ روپے")

    def test_money_urdu_arab_dollar(self):
        self._assert_entity("کل مالیاتی حجم 2 ارب ڈالر رہا۔", "MONEY", "2 ارب ڈالر")

    # --------------------------------------------------------------------------
    # 4. PERCENT TESTS (%, per cent, percentage points, Urdu فیصد)
    # --------------------------------------------------------------------------
    def test_percent_symbol(self):
        self._assert_entity("Inflation dropped to 17.5% in September.", "PERCENT", "17.5%")

    def test_percent_per_cent_phrase(self):
        self._assert_entity("The discount rate was cut by 5.2 per cent.", "PERCENT", "5.2 per cent")

    def test_percent_word(self):
        self._assert_entity("Growth rate forecast is 12 percent.", "PERCENT", "12 percent")

    def test_percent_points(self):
        self._assert_entity("A decrease of 3.8 percentage points was noted.", "PERCENT", "3.8 percentage points")

    def test_percent_urdu(self):
        self._assert_entity("صنعتی شرح میں 4.8 فیصد اضافہ دیکھا گیا۔", "PERCENT", "4.8 فیصد")

    # --------------------------------------------------------------------------
    # 5. TIME TESTS (AM/PM, PST, o'clock, Urdu بجے)
    # --------------------------------------------------------------------------
    def test_time_pm_format(self):
        self._assert_entity("The blast occurred at 11:45 PM near the mall.", "TIME", "11:45 PM")

    def test_time_am_format(self):
        self._assert_entity("Court opens at 3:30 am.", "TIME", "3:30 am")

    def test_time_pst_timezone(self):
        self._assert_entity("Session scheduled at 02:00 PST.", "TIME", "02:00 PST")

    def test_time_oclock(self):
        self._assert_entity("The assembly adjourned at 5 o'clock.", "TIME", "5 o'clock")

    def test_time_urdu(self):
        self._assert_entity("اجلاس ٹھیک ساڑھے تین بجے شروع ہوگا۔", "TIME", "ساڑھے تین بجے")

    # --------------------------------------------------------------------------
    # 6. DATE TESTS (Full Gregorian, ISO, Day of week, Urdu)
    # --------------------------------------------------------------------------
    def test_date_day_month_year(self):
        self._assert_entity("Independence day on 14 August 2025.", "DATE", "14 August 2025")

    def test_date_month_day_year(self):
        self._assert_entity("Resolution passed on March 23, 1940.", "DATE", "March 23, 1940")

    def test_date_iso_format(self):
        self._assert_entity("Report due on 2025-10-21.", "DATE", "2025-10-21")

    def test_date_day_of_week(self):
        self._assert_entity("The court resumes hearing on Monday.", "DATE", "Monday")

    def test_date_urdu(self):
        self._assert_entity("اعلان 14 اگست 2025 کو کیا جائے گا۔", "DATE", "14 اگست 2025")

    # --------------------------------------------------------------------------
    # 7. NEGATIVE EXAMPLES & DISCRIMINATION
    # --------------------------------------------------------------------------
    def test_negative_isolated_year_not_phone(self):
        # A normal four-digit year (e.g., 2024) must never be extracted as a PHONE_NUMBER
        entities = extract_regex_entities("In 2024, the government launched reforms.")
        phones = [e for e in entities if e["label"] == "PHONE_NUMBER"]
        self.assertEqual(len(phones), 0, "Year was falsely identified as a phone number.")

    def test_negative_generic_number_not_cnic(self):
        # Arbitrary digits without CNIC context or format must not be ID_NUMBER
        entities = extract_regex_entities("The serial code was 98765432.")
        ids = [e for e in entities if e["label"] == "ID_NUMBER"]
        self.assertEqual(len(ids), 0, "Non-CNIC serial number was falsely matched as ID_NUMBER.")

    # --------------------------------------------------------------------------
    # 8. URDU & BILINGUAL SCRIPT TESTS (Eastern Arabic Digits, Hijri Dates, Urdu Currency)
    # --------------------------------------------------------------------------
    def test_urdu_phone_eastern_digits(self):
        self._assert_entity("رابطہ نمبر ۰۳۰۰-۱۲۳۴۵۶۷ پر کال کریں۔", "PHONE_NUMBER", "۰۳۰۰-۱۲۳۴۵۶۷")

    def test_urdu_phone_country_code(self):
        self._assert_entity("ہیلپ لائن +۹۲ ۳۰۰ ۱۲۳۴۵۶۷ فعال ہے۔", "PHONE_NUMBER", "+۹۲ ۳۰۰ ۱۲۳۴۵۶۷")

    def test_urdu_cnic_eastern_digits(self):
        self._assert_entity("امیدوار کا شناختی کارڈ نمبر ۴۲۱۰۱-۱۲۳۴۵۶۷-۱ ہے۔", "ID_NUMBER", "۴۲۱۰۱-۱۲۳۴۵۶۷-۱")

    def test_urdu_money_eastern_digits(self):
        self._assert_entity("منصوبے کی لاگت ۱۵ کروڑ روپے ہے۔", "MONEY", "۱۵ کروڑ روپے")

    def test_urdu_percent_eastern_digits(self):
        self._assert_entity("مہنگائی میں ۵.۲ فیصد کمی واقع ہوئی۔", "PERCENT", "۵.۲ فیصد")

    def test_urdu_time_evening(self):
        self._assert_entity("ملاقات شام ۶ بجے طے پائی۔", "TIME", "شام ۶ بجے")

    def test_urdu_date_eastern_digits(self):
        self._assert_entity("تقریب ۱۴ اگست ۲۰۲۵ کو منعقد ہوگی۔", "DATE", "۱۴ اگست ۲۰۲۵")

    def test_urdu_date_hijri_format(self):
        self._assert_entity("چھٹی ۱۰ محرم الحرام کو ہوگی۔", "DATE", "۱۰ محرم الحرام")


if __name__ == "__main__":
    unittest.main()
