"""Test bổ sung Stage 4 (TC11-TC19). Đặt cùng thư mục với database.py, validators.py rồi chạy:
    python -m unittest test_extra_cases -v
File này KHÔNG sửa mã nguồn gốc; các test FAIL là lỗi còn tồn tại trong mã nguồn."""
import os, sys, unittest, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import Database
from validators import validate_contact_input


class Base(unittest.TestCase):
    def setUp(self):
        self.f = tempfile.mktemp(suffix=".db")
        self.db = Database(self.f)

    def tearDown(self):
        self.db.conn.close()
        if os.path.exists(self.f):
            os.remove(self.f)


class TestExtra(Base):
    def test_tc11_register_new_account(self):
        """TC11 Đăng ký tài khoản mới rồi đăng nhập"""
        ok, _ = self.db.register("sinhvien", "matkhau1", "Sinh Viên")
        user = self.db.authenticate("sinhvien", "matkhau1")
        self.assertTrue(ok)
        self.assertIsNotNone(user)
        self.assertEqual(len(self.db.get_user_groups(user[0])), 4)

    def test_tc12_register_duplicate_username(self):
        """TC12 Đăng ký trùng tên đăng nhập bị từ chối"""
        ok, msg = self.db.register("admin", "matkhau1")
        self.assertFalse(ok)
        self.assertEqual(msg, "Tên đăng nhập đã tồn tại!")

    def test_tc13_persistence(self):
        """TC13 Dữ liệu còn nguyên sau khi đóng và mở lại ứng dụng"""
        self.db.add_contact(1, "Trần Duy", "Kha", "0778016331", "", "")
        self.db.conn.close()
        self.db = Database(self.f)
        self.assertEqual(len(self.db.get_contacts(1, search_keyword="Kha")), 1)

    def test_tc14_sql_injection_login(self):
        """TC14 Chuỗi SQL injection ở màn hình đăng nhập không đăng nhập được"""
        self.assertIsNone(self.db.authenticate("' OR '1'='1", "' OR '1'='1"))
        self.assertIsNone(self.db.authenticate("admin' --", "x"))

    def test_tc15_other_user_cannot_update_contact(self):
        """TC15 User khác không được sửa liên hệ của người khác (BUG-08)"""
        self.db.add_contact(1, "A", "A", "0900000001", "", "")
        cid = self.db.get_contacts(1)[0][0]
        self.db.update_contact(cid, 2, "Hack", "Hack", "0999999999", "evil@x.com", "")
        self.assertEqual(self.db.get_contact(cid, 1)[3], "0900000001")

    def test_tc16_phone_accepts_only_ascii_digits(self):
        """TC16 SĐT chỉ chấp nhận chữ số 0-9 (BUG-09)"""
        for bad in ("٠٩١٢٣٤٥٦٧٨", "²²²²²²²²²²"):
            self.assertIsNotNone(validate_contact_input("An", bad, ""), repr(bad))

    def test_tc17_search_special_chars(self):
        """TC17 Tìm kiếm ký tự '%' không trả về toàn bộ danh bạ (BUG-10)"""
        self.db.add_contact(1, "A", "A", "0900000001", "", "")
        self.db.add_contact(1, "B", "B", "0900000002", "", "")
        self.assertEqual(len(self.db.get_contacts(1, search_keyword="%")), 0)

    def test_tc18_password_with_spaces_can_login(self):
        """TC18 Mật khẩu có khoảng trắng đầu/cuối: đăng ký xong phải đăng nhập được (BUG-11)"""
        ok, _ = self.db.register("tester", " abcdef ")
        if ok:   # main.py cắt khoảng trắng ô mật khẩu khi đăng nhập
            self.assertIsNotNone(self.db.authenticate("tester", " abcdef ".strip()))

    def test_tc19_email_double_dot(self):
        """TC19 Email có hai dấu chấm liên tiếp 'a@b..c' bị từ chối (BUG-12)"""
        self.assertIsNotNone(validate_contact_input("An", "0912345678", "a@b..c"))


if __name__ == "__main__":
    unittest.main()
