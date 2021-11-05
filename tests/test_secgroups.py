import unittest
import mpyc.fingroups as fg
from mpyc.runtime import mpc


class Arithmetic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    # TODO: test caching

    def test_Sn(self):
        group = fg.SymmetricGroup(5)
        a = group([3, 4, 2, 1, 0])
        b = a @ a
        secgrp = mpc.SecGrp(group)
        c = secgrp(a)
        d = a @ c
        self.assertEqual(mpc.run(mpc.output(d)), b)
        e = ~c
        f = e @ b
        self.assertEqual(mpc.run(mpc.output(f)), a)
        self.assertTrue(mpc.run(mpc.output(f == c)))

        group = fg.SymmetricGroup(11)
        secgrp = mpc.SecGrp(group)
        a = group([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0])
        secfld = mpc.SecFld(11)  # ord(a) = 11
        a7 = secgrp.repeat(a, secfld(7))
        self.assertEqual(mpc.run(mpc.output(a7)), a^7)
        a7 = secgrp.repeat_public(a, secfld(7))
        self.assertEqual(mpc.run(a7), a^7)
        a6 = a^6
        a12 = a6 @ a6
        self.assertEqual(mpc.run(mpc.output(secgrp(a6).inverse())), a^5)
        self.assertEqual(mpc.run(mpc.output((secgrp(a)^6) @ secgrp.identity)), a6)
        self.assertEqual(mpc.run(mpc.output(secgrp.repeat(a6, secfld(2)))), a12)

    def test_QR(self):
        group = fg.QuadraticResidues(l=768)
        secgrp = mpc.SecGrp(group)
        g = group.generator
        g2 = mpc.run(mpc.output(secgrp(g) * g))
        self.assertEqual(int(g), int(group.identity * g))
        self.assertEqual(g2, g * g)
        secfld = mpc.SecFld(modulus=secgrp.group.order)
        self.assertEqual(mpc.run(mpc.output(secgrp.repeat(g, secfld(2)))), g2)
        self.assertEqual(mpc.run(mpc.output(secgrp.repeat(secgrp(g), 2))), g2)
        m, z = group.encode(42)
        self.assertEqual(mpc.run(mpc.output(secgrp.decode(secgrp(m), secgrp(z)))), 42)
        h = secgrp.if_else(secgrp.sectype(0), g, secgrp(g2))
        self.assertEqual(mpc.run(mpc.output(h)), g2)

    def test_EC(self):
        curves = (fg.EllipticCurve('ED25519'),  # affine coordinates
                  fg.EllipticCurve('ED25519', coordinates='projective'),
                  fg.EllipticCurve('ED25519', coordinates='extended'),
                  fg.EllipticCurve('ED448', coordinates='projective'),
                  fg.EllipticCurve('BN256', coordinates='projective'),
                  fg.EllipticCurve('BN256_twist', coordinates='projective'))
        for group in curves:
            secgrp = mpc.SecGrp(group)
            secfld = mpc.SecFld(modulus=secgrp.group.order)
            g = group.generator
            b = secgrp(g.value)
            self.assertEqual(mpc.run(mpc.output(b - b)), group.identity)
            c = secgrp(g)
            self.assertEqual(mpc.run(mpc.output(b)), mpc.run(mpc.output(c)))
            self.assertEqual(mpc.run(mpc.output(g^secfld(2))), g^2)
            bp4 = 4*g
            sec_bp4 = 4*secgrp(g) + secgrp.identity
            self.assertEqual(mpc.run(mpc.output(sec_bp4)), bp4)
            sec_bp8 = secgrp.repeat(bp4, secfld(2))
            self.assertEqual(mpc.run(mpc.output(sec_bp8)), bp4 + bp4)
            self.assertEqual(mpc.run(mpc.output(secgrp.repeat(bp4, secfld(3)))), 3*bp4)
            self.assertEqual(mpc.run(mpc.output(b - b)), group.identity)
            if group.curvename != 'BN256_twist':
                m, z = group.encode(42)
                self.assertEqual(mpc.run(mpc.output(secgrp.decode(secgrp(m), secgrp(z)))), 42)

    def test_Cl(self):
        Cl23 = fg.ClassGroup(Delta=-23)
        secgrp = mpc.SecGrp(Cl23)
        secfld = secgrp.sectype
        g = Cl23.generator
        self.assertEqual(mpc.run(mpc.output(g^secfld(3))), Cl23.identity)
        self.assertEqual(mpc.run(mpc.output(g * secgrp(g))), Cl23((2, -1, 3)))

        Cl227 = fg.ClassGroup(Delta=-227)  # Example 9.6.2 from Buchman&Vollmer
        secgrp = mpc.SecGrp(Cl227)
        g = Cl227((3, 1, 19))
        self.assertEqual(mpc.run(mpc.output(secgrp(g)^5)), g^5)

        Cl1123 = fg.ClassGroup(Delta=-1123)  # Example 9.7.5 from Buchman&Vollmer
        secgrp = mpc.SecGrp(Cl1123)
        self.assertEqual(Cl1123((1, 1, 281)), Cl1123.identity)
        g = Cl1123((7, 5, 41))
        self.assertEqual(mpc.run(mpc.output(secgrp(g)^5)), g^5)
        self.assertEqual(mpc.run(mpc.output(secgrp(g)**3)), g^3)

        group = fg.ClassGroup(l=28)
        secgrp = mpc.SecGrp(group)
        g = group.generator
        a = secgrp(g)^6
        self.assertEqual(mpc.run(mpc.output(a)), g^6)
        self.assertEqual(mpc.run(mpc.output(a * (a^-1))), group.identity)
        m, z = group.encode(5)
        self.assertEqual(mpc.run(mpc.output(secgrp.decode(secgrp(m), secgrp(z)))), 5)


if __name__ == "__main__":
    unittest.main()
