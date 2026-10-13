# SPDX-License-Identifier: GPL-2.0-or-later
"""Pair multiply-accumulate (e1fc): signed and unsigned, both pair encodings."""
from pathlib import Path
import tempfile
import unittest

from support import ROOT, Guest, guest_state


class MultiplyAccumulateTests(unittest.TestCase):
    def setUp(self):
        directory = ROOT / ".cache/tests"
        directory.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=directory)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def extension(self, pair_word, left, right, signed):
        return (pair_word << 13) | (0x1000 if signed else 0) | \
               (right << 8) | (left << 4)

    def accumulate(self, ext, pair, left_reg, left, right_reg, right,
                   initial=(0, 0)):
        guest = Guest()
        guest.literal(pair, initial[0])
        guest.literal(pair + 1, initial[1])
        guest.literal(left_reg, left)
        guest.literal(right_reg, right)
        guest.emit(0xe1fc, ext)
        return guest_state(self.directory, guest)

    def test_unsigned_product_accumulates_into_the_pair(self):
        # Vendor E1FC 02F0: r1_r0 += r15 * r2 (u).
        state = self.accumulate(self.extension(0, 2, 3, False), 0, 2,
                                0x80000000, 3, 2)
        self.assertEqual(state["registers"][0], 0x00000000)
        self.assertEqual(state["registers"][1], 0x00000001)

    def test_signed_product_differs(self):
        # Vendor E1FC DA30: r13_r12 += r3 * r10 (s); the extension's bit
        # 12 selects the signed product and bits 15-13 name the pair.
        state = self.accumulate(self.extension(6, 3, 10, True), 12, 3,
                                0x80000000, 10, 2)
        self.assertEqual(state["registers"][12], 0x00000000)
        self.assertEqual(state["registers"][13], 0xffffffff)

    def test_accumulate_extends_an_existing_pair(self):
        state = self.accumulate(self.extension(0, 2, 3, False), 0, 2,
                                0x10, 3, 2, initial=(0xf0, 0))
        self.assertEqual(state["registers"][0], 0x110)
        self.assertEqual(state["registers"][1], 0)

    def test_high_words_resolve_the_pair(self):
        # The unsigned form with the pair named by bits 15-13 = 7 writes
        # r15_r14 (vendor E1FC E650 reads r15_r14).
        state = self.accumulate(self.extension(7, 2, 3, False), 14, 2,
                                0x80000000, 3, 2)
        self.assertEqual(state["registers"][14], 0x00000000)
        self.assertEqual(state["registers"][15], 0x00000001)


if __name__ == "__main__":
    unittest.main()
