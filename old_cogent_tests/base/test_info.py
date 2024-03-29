#!/usr/bin/env python
#file evo/test_info.py

"""Unit tests for Info class and associated objects (DbRef, DbRefs, etc.).

Revision History

11/6/03 Rob Knight: initially written for PyEvolve.
"""

from old_cogent.util.unit_test import TestCase, main
from old_cogent.base.info import DbRef, DbRefs, Info, _make_list

class DbRefTests(TestCase):
    """Tests of the DbRef object."""
    def setUp(self):
        """Define a standard DbRef object"""
        self.data = dict(Accession='xyz',Db='abc',Name='qwe',Description='blah',
            Data = range(20))
        self.db = DbRef(**self.data)
    
    def test_init_minimal(self):
        """DbRef minimal init should fill fields as expected"""
        d = DbRef('abc')
        self.assertEqual(d.Accession, 'abc')
        self.assertEqual(d.Db, '')
        self.assertEqual(d.Name, '')
        self.assertEqual(d.Description, '')
        self.assertEqual(d.Data, None)
        #empty init not allowed
        self.assertRaises(TypeError, DbRef)

    def test_init(self):
        """DbRef init should insert correct data"""
        for attr, val in self.data.items():
            self.assertEqual(getattr(self.db, attr), val)

    def test_str(self):
        """DbRef str should be the same as the accession str"""
        self.assertEqual(str(self.db), 'xyz')
        self.db.Accession = 12345
        self.assertEqual(str(self.db), '12345')

    def test_int(self):
        """DbRef int should be the same as the accession int"""
        self.assertRaises(ValueError, int, self.db)
        self.db.Accession = '12345'
        self.assertEqual(int(self.db), 12345)

    def test_cmp(self):
        """DbRef cmp should first try numeric, then alphabetic, cmp."""
        assert DbRef('abc') < DbRef('xyz')
        assert DbRef('abc') == DbRef('abc')
        assert DbRef('123') > DbRef('14')
        assert DbRef('123') < DbRef('abc')
        #check that it ignores other attributes
        assert DbRef('x','y','z','a','b') == DbRef('x')

class infoTests(TestCase):
    """Tests of top-level functions."""
    def test_make_list(self):
        """_make_list should always return a list"""
        self.assertEqual(_make_list('abc'), ['abc'])
        self.assertEqual(_make_list([]), [])
        self.assertEqual(_make_list(None), [None])
        self.assertEqual(_make_list({'x':'y'}), [{'x':'y'}])
        self.assertEqual(_make_list([1,2,3]), [1,2,3])

class DbRefsTests(TestCase):
    """Tests of the DbRefs class."""
    def test_init_empty(self):
       """DbRefs empty init should work as expected"""
       self.assertEqual(DbRefs(), {})

    def test_init_data(self):
        """DbRefs init with data should produce expected results"""
        d = DbRefs({'GenBank':'ab', 'GO':(3,44), 'PDB':['asdf','ghjk']})
        self.assertEqual(d,{'GenBank':['ab'],'GO':[3,44],'PDB':['asdf','ghjk']})
        d.GenBank = 'xyz'
        self.assertEqual(d['GenBank'], ['xyz'])

class InfoTests(TestCase):
    """Tests of the Info class."""
    def test_init_empty(self):
        """Info empty init should work as expected"""
        d = Info()
        self.assertEqual(len(d), 1)
        assert 'Refs' in d
        self.assertEqual(d.Refs, DbRefs())
        assert isinstance(d.Refs, DbRefs)

    def test_init_data(self):
        """Info init with data should put items in correct places"""
        #need to check init, setting, and resetting of attributes that belong
        #in the Info object and attributes that belong in Info.Refs. Also need
        #to check __getitem__, __setitem__, and __contains__.
        d = Info({'x':3, 'GO':12345})
        self.assertEqual(d.x, 3)
        self.assertEqual(d.GO, [12345])
        self.assertEqual(d.Refs.GO, [12345])
        try:
            del d.Refs
        except AttributeError:
            pass
        else:
            raise Exception, "Failed to prevent deletion of required key Refs"""
        d.GenBank = ('qaz', 'wsx')
        self.assertEqual(d.GenBank, ['qaz', 'wsx'])
        assert 'GenBank' in d.Refs
        assert 'GenBank' in d
        d.GenBank = 'xyz'
        self.assertEqual(d.GenBank, ['xyz'])
        assert d.GenBank is d.Refs.GenBank
        d.GO = 'x'
        self.assertEqual(d.GO, ['x'])
        d.GO.append('y')
        self.assertEqual(d.GO, ['x', 'y'])
        d.ZZZ = 'zzz'
        self.assertEqual(d.ZZZ, 'zzz')
        assert 'ZZZ' not in d.Refs
        assert 'XXX' not in d
        self.assertEqual(d.XXX, None)

    def test_identity(self):
        """Info should get its own new Refs when created"""
        i = Info()
        j = Info()
        assert i is not j
        assert i.Refs is not j.Refs

#run the following if invoked from command-line
if __name__ == "__main__":
    main()
