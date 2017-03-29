# import unittest
#
# from mock import patch
#
#
# @patch('musicleague.notify.flash.flash')
# class FlashTestCase(unittest.TestCase):
#
#     def setUp(self):
#         self.message = "This is a test message"
#
#     def test_flash_error(self, flash):
#         from musicleague.notify.flash import flash_error
#
#         flash_error(self.message)
#
#         flash.assert_called_once_with(self.message, "danger")
#
#     def test_flash_info(self, flash):
#         from musicleague.notify.flash import flash_info
#
#         flash_info(self.message)
#
#         flash.assert_called_once_with(self.message, "info")
#
#     def test_flash_success(self, flash):
#         from musicleague.notify.flash import flash_success
#
#         flash_success(self.message)
#
#         flash.assert_called_once_with(self.message, "success")
#
#     def test_flash_warning(self, flash):
#         from musicleague.notify.flash import flash_warning
#
#         flash_warning(self.message)
#
#         flash.assert_called_once_with(self.message, "warning")
