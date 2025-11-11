# Add package directory to path for debugging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest 
import enumex
from enumex import *
from enumex import autoex as auto
from abc import ABC, abstractmethod
from typing import Callable

class EnumExTests(unittest.TestCase):
    
    def test_enumex_auto_inheritance(self):
        class A(EnumEx):
            V1 = autoex()
            V2 = '2'
            V3 = 3
        class B(A):
            V4 = autoex()
            V5 = autoex()

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(B.V1,     A)
        self.assertIsInstance(B.V4,     A)
        self.assertNotIsInstance(A.V1,  B)
        self.assertEqual(1,             A.V1.value)
        self.assertEqual('2',           A.V2.value)
        self.assertEqual(3,             A.V3.value)
        self.assertEqual(1,             B.V1.value)
        self.assertEqual('2',           B.V2.value)
        self.assertEqual(3,             B.V3.value)
        self.assertEqual(4,             B.V4.value)
        self.assertEqual(5,             B.V5.value)
        self.assertEqual("A.V1",        str(A.V1))
        self.assertEqual("B.V1",        str(B.V1))

        self.assertListEqual([A.V1, A.V2, A.V3], list(A))
        self.assertListEqual([B.V1, B.V2, B.V3, B.V4, B.V5], list(B))

    def test_intenumex_auto_inheritance(self):
        class A(IntEnumEx):
            V1 = autoex()
            V2 = autoex()
            V3 = 3
        class B(A):
            V4 = autoex()
            V5 = autoex()

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(B.V1,     A)
        self.assertIsInstance(B.V4,     A)
        self.assertNotIsInstance(A.V1,  B)
        self.assertEqual(1,             A.V1.value)
        self.assertEqual(2,             A.V2.value)
        self.assertEqual(3,             A.V3.value)
        self.assertEqual(1,             B.V1.value)
        self.assertEqual(2,             B.V2.value)
        self.assertEqual(3,             B.V3.value)
        self.assertEqual(4,             B.V4.value)
        self.assertEqual(5,             B.V5.value)
        self.assertGreater(B.V3,        A.V2)

        self.assertListEqual([A.V1, A.V2, A.V3], list(A))
        self.assertListEqual([A.V1, A.V2, A.V3, B.V4, B.V5], list(B))

    def test_intflagex_auto_inheritance(self):
        class A(IntFlagEx):
            F1 = autoex()
            F2 = autoex()
            F3 = 0b1100
        class B(A):
            F4 = autoex()
            F5 = autoex()

        self.assertIsInstance(A.F1,     A)
        self.assertIsInstance(B.F1,     A)
        self.assertIsInstance(B.F4,     A)
        self.assertIsInstance(B.F1,     B)
        self.assertNotIsInstance(A.F1,  B)
        self.assertEqual(1,             A.F1.value)
        self.assertEqual(2,             A.F2.value)
        self.assertEqual(0b1100,        A.F3.value)
        self.assertEqual(1,             A.F1.value)
        self.assertEqual(2,             B.F2.value)
        self.assertEqual(0b1100,        B.F3.value)
        self.assertEqual(0b10000,       B.F4.value)
        self.assertEqual(0b100000,      B.F5.value)

        print(", ".join(str(v) for v in list(A)))
        print(", ".join(str(v) for v in list(B)))

        self.assertListEqual([A.F1, A.F2], list(A))
        self.assertListEqual([A.F1, A.F2, B.F4, B.F5], list(B))

    def test_strenumex_auto_inheritance(self):
        class A(StrEnumEx):
            V1 = autoex()
            V2 = '2'
            V3 = V2
        class B(A):
            V4 = autoex()
            V5 = autoex()

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(B.V1,     A)
        self.assertIsInstance(B.V4,     A)
        self.assertIsInstance(B.V1,     B)
        self.assertNotIsInstance(A.V1,  B)
        self.assertEqual('v1',          A.V1.value)
        self.assertEqual('2',           A.V2.value)
        self.assertEqual('2',           A.V3.value)
        self.assertEqual('v1',          B.V1.value)
        self.assertEqual('2',           B.V2.value)
        self.assertEqual('2',           B.V3.value)
        self.assertEqual('v4',          B.V4.value)
        self.assertEqual('v5',          B.V5.value)

        self.assertListEqual([A.V1, A.V3], list(A))
        self.assertListEqual([A.V1, A.V3, B.V4, B.V5], list(B))

    def test_errors(self):
        class A(EnumEx):
            V1 = autoex()
            V2 = '2'
            V3 = 3
        class B(A):
            V4 = autoex()
            V5 = autoex()

        with self.assertRaises(TypeError) as ec:
            class A(EnumEx):
                V1 = autoex()
                V2 = '2'
                V3 = 3
            class B(A):
                V3 = A.V3
        self.assertEqual("'V3' already defined as 3", ec.exception.args[0])
        
    def test_instance_methods(self):
        class A(EnumEx):
            V1 = autoex()
            V2 = autoex()

            def custom_format(self):
                return f"A.{self.name} : {self.value}"
        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def custom_format(self):
                return f"B.{self.name} : {self.value}"
        
        self.assertEqual("A.V1 : 1", A.V1.custom_format())
        self.assertEqual("B.V1 : 1", B.V1.custom_format())

    def test_abstract_methods(self):
        class A(EnumEx):
            V1 = autoex()
            
            def fee(cls):
                pass

            @abstractmethod
            def foo(self):
                pass

            def bar(self):
                pass
                return "A"
            
            @abstractmethod
            def foe(self):
                return
            
            @abstractmethod
            def fum():
                ...
            
        class B(A):
            V2 = autoex()

            def fee(self):
                return "B"
            
            def foo(self):
                return "B"            

        class C(B):     
            def fee(self):
                return "C"
                   
            def bar(self):
                return "C"
            
            def fum():
                return "C"

        class X(EnumEx):
            V1 = autoex()

            def foo(self):
                return "X"
            
        self.assertTrue(is_method_empty(A.fee),             msg="A fee is empty")
        self.assertTrue(is_method_empty(A.foo),             msg="A foo is empty")
        self.assertTrue(is_method_empty(A.fum),             msg="A fum is empty")
        self.assertFalse(is_method_empty(A.bar),            msg="A bar not empty")
        self.assertFalse(is_method_empty(A.foe),            msg="A foe not empty")

        self.assertTrue(is_method_empty(B.fum),             msg="B fum is empty")
        self.assertFalse(is_method_empty(B.fee),            msg="B fee not empty")
        self.assertFalse(is_method_empty(B.foo),            msg="B foo not empty")
        self.assertFalse(is_method_empty(B.bar),            msg="B bar not empty")
        self.assertFalse(is_method_empty(B.foe),            msg="B foe not empty")

        self.assertFalse(is_method_empty(C.fee),            msg="C fee not empty")
        self.assertFalse(is_method_empty(C.foo),            msg="C foo not empty")
        self.assertFalse(is_method_empty(C.bar),            msg="C bar not empty")
        self.assertFalse(is_method_empty(C.foe),            msg="C foe not empty")
        self.assertFalse(is_method_empty(C.fum),            msg="C fum not empty")

        self.assertTrue(is_abstract_enum(A),                msg="A abstract is enum")
        self.assertTrue(is_abstract_enum(B),                msg="B abstract is enum")
        self.assertTrue(is_abstract_enum(C),                msg="C abstract is enum")
        self.assertFalse(is_abstract_enum(X),               msg="X abstract not enum")
        
        self.assertTrue(is_unimplemented_abstract_enum(A),  msg="A is unimplemented abstract enum")
        self.assertTrue(is_unimplemented_abstract_enum(B),  msg="B is unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(C), msg="C not unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(X), msg="X not unimplemented abstract enum")

        def assert_all_in(col, prefix, *args):
            count = len(args)
            self.assertEqual(count, len(col), msg=f"{prefix} count")
            for arg in args:
                self.assertIn(arg, col, msg=f"{prefix} {arg} in")

        a_abstracts = get_abstract_methods(A)
        b_abstracts = get_abstract_methods(B)
        c_abstracts = get_abstract_methods(C)
        x_abstracts = get_abstract_methods(X)

        assert_all_in(a_abstracts, "A abstracts ", 'foo', 'fum')
        assert_all_in(b_abstracts, "B abstracts ", 'foo', 'fum')
        assert_all_in(c_abstracts, "C abstracts ", 'foo', 'fum')
        assert_all_in(x_abstracts, "X abstracts ")

        a_unimp = get_unimplemented_abstract_methods(A)
        b_unimp = get_unimplemented_abstract_methods(B)
        c_unimp = get_unimplemented_abstract_methods(C)
        x_unimp = get_unimplemented_abstract_methods(X)

        assert_all_in(a_unimp, "A unimplemented abstracts ", 'foo', 'fum')
        assert_all_in(b_unimp, "B unimplemented abstracts ", 'fum')
        assert_all_in(c_unimp, "C unimplemented abstracts ")
        assert_all_in(x_unimp, "X unimplemented abstracts ")

    def test_abstract_static_methods(self):
        class A(EnumEx):
            V1 = autoex()

            @staticmethod
            @abstractmethod
            def fee():
                pass

            @staticmethod
            @abstractmethod
            def foo():
                pass
            
            @staticmethod
            @abstractmethod
            def bar():
                pass
            
        class B(A):
            V2 = autoex()    

            @staticmethod
            def fee():
                return "B"   
            
            @staticmethod
            def foo():
                return "B"  

        class C(B):     
            @staticmethod       
            def foo():
                return "C"
            
            @staticmethod
            def bar():
                return "C"
            

        class X(EnumEx):
            V1 = autoex()

            @staticmethod
            @abstractmethod
            def soo(self):
                return "X"
        
        self.assertTrue(is_method_empty(A.fee),             msg="A fee is empty")
        self.assertTrue(is_method_empty(A.foo),             msg="A foo is empty")
        self.assertTrue(is_method_empty(A.bar),             msg="A bar is empty")

        self.assertTrue(is_method_empty(B.bar),             msg="B bar is empty")
        self.assertFalse(is_method_empty(B.fee),            msg="B fee is empty")
        self.assertFalse(is_method_empty(B.foo),            msg="B foo is empty")

        self.assertFalse(is_method_empty(C.fee),            msg="C fee not empty")
        self.assertFalse(is_method_empty(C.foo),            msg="C foo not empty")
        self.assertFalse(is_method_empty(C.bar),            msg="C bar not empty")
        self.assertFalse(is_method_empty(X.soo),            msg="X soo not empty")

        self.assertTrue(is_abstract_enum(A),                msg="A abstract is enum")
        self.assertTrue(is_abstract_enum(B),                msg="B abstract is enum")
        self.assertTrue(is_abstract_enum(C),                msg="C abstract is enum")
        self.assertFalse(is_abstract_enum(X),               msg="X abstract not enum")
        
        self.assertTrue(is_unimplemented_abstract_enum(A),  msg="A is unimplemented abstract enum")
        self.assertTrue(is_unimplemented_abstract_enum(B),  msg="B is unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(C), msg="C not unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(X), msg="X not unimplemented abstract enum")

        def assert_all_in(col, prefix, *args):
            count = len(args)
            self.assertEqual(count, len(col), msg=f"{prefix} count")
            for arg in args:
                self.assertIn(arg, col, msg=f"{prefix} {arg} in")

        a_abstracts = get_abstract_methods(A)
        b_abstracts = get_abstract_methods(B)
        c_abstracts = get_abstract_methods(C)
        x_abstracts = get_abstract_methods(X)

        assert_all_in(a_abstracts, "A abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(b_abstracts, "B abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(c_abstracts, "C abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(x_abstracts, "X abstracts ")

        a_unimp = get_unimplemented_abstract_methods(A)
        b_unimp = get_unimplemented_abstract_methods(B)
        c_unimp = get_unimplemented_abstract_methods(C)
        x_unimp = get_unimplemented_abstract_methods(X)

        assert_all_in(a_unimp, "A unimplemented abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(b_unimp, "B unimplemented abstracts ", 'bar')
        assert_all_in(c_unimp, "C unimplemented abstracts ")
        assert_all_in(x_unimp, "X unimplemented abstracts ")

        with self.assertRaises(TypeError) as ec:
            v = A(1)
        _assert_invalidabstract(self, ec, A.__name__, 'fee', 'foo', 'bar')

        with self.assertRaises(TypeError) as ec:
            v = B(1)
        _assert_invalidabstract(self, ec, B.__name__, 'bar')

        v = C(1)
        x = X(1)

    def test_abstract_class_methods(self):
        class A(EnumEx):
            V1 = autoex()

            @classmethod
            @abstractmethod
            def fee():
                pass

            @classmethod
            @abstractmethod
            def foo():
                pass
            
            @classmethod
            @abstractmethod
            def bar():
                pass
            
        class B(A):
            V2 = autoex()    

            @classmethod
            def fee():
                return "B"   
            
            @classmethod
            def foo():
                return "B"  

        class C(B):  
            @classmethod          
            def foo():
                return "C"
            
            @classmethod
            def bar():
                return "C"
            

        class X(EnumEx):
            V1 = autoex()

            @classmethod
            @abstractmethod
            def coo(self):
                return "coo"
        
        self.assertTrue(is_method_empty(A.fee),             msg="A fee is empty")
        self.assertTrue(is_method_empty(A.foo),             msg="A foo is empty")
        self.assertTrue(is_method_empty(A.bar),             msg="A bar is empty")

        self.assertTrue(is_method_empty(B.bar),             msg="B bar is empty")
        self.assertFalse(is_method_empty(B.fee),            msg="B fee is empty")
        self.assertFalse(is_method_empty(B.foo),            msg="B foo is empty")

        self.assertFalse(is_method_empty(C.fee),            msg="C fee not empty")
        self.assertFalse(is_method_empty(C.foo),            msg="C foo not empty")
        self.assertFalse(is_method_empty(C.bar),            msg="C bar not empty")
        self.assertFalse(is_method_empty(X.coo),            msg="X coo not empty")

        self.assertTrue(is_abstract_enum(A),                msg="A abstract is enum")
        self.assertTrue(is_abstract_enum(B),                msg="B abstract is enum")
        self.assertTrue(is_abstract_enum(C),                msg="C abstract is enum")
        self.assertFalse(is_abstract_enum(X),               msg="X abstract not enum")
        
        self.assertTrue(is_unimplemented_abstract_enum(A),  msg="A is unimplemented abstract enum")
        self.assertTrue(is_unimplemented_abstract_enum(B),  msg="B is unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(C), msg="C not unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(X), msg="X not unimplemented abstract enum")

        def assert_all_in(col, prefix, *args):
            count = len(args)
            self.assertEqual(count, len(col), msg=f"{prefix} count")
            for arg in args:
                self.assertIn(arg, col, msg=f"{prefix} {arg} in")

        a_abstracts = get_abstract_methods(A)
        b_abstracts = get_abstract_methods(B)
        c_abstracts = get_abstract_methods(C)
        x_abstracts = get_abstract_methods(X)

        assert_all_in(a_abstracts, "A abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(b_abstracts, "B abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(c_abstracts, "C abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(x_abstracts, "X abstracts ")

        a_unimp = get_unimplemented_abstract_methods(A)
        b_unimp = get_unimplemented_abstract_methods(B)
        c_unimp = get_unimplemented_abstract_methods(C)
        x_unimp = get_unimplemented_abstract_methods(X)

        assert_all_in(a_unimp, "A unimplemented abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(b_unimp, "B unimplemented abstracts ", 'bar')
        assert_all_in(c_unimp, "C unimplemented abstracts ")
        assert_all_in(x_unimp, "X unimplemented abstracts ")

        with self.assertRaises(TypeError) as ec:
            v = A(1)
        _assert_invalidabstract(self, ec, A.__name__, 'fee', 'foo', 'bar')

        with self.assertRaises(TypeError) as ec:
            v = B(1)
        _assert_invalidabstract(self, ec, B.__name__, 'bar')

        v = C(1)
        x = X(1)
        

    def test_abstract_properties(self):
        class A(EnumEx):
            V1 = autoex()

            @property
            @abstractmethod
            def pie(self):
                pass
            
            @property
            @abstractmethod
            def poo(self):
                pass

            @abstractmethod
            def get_poof(self):
                pass

            @abstractmethod
            def set_poof(self, value):
                pass

            @abstractmethod
            def del_poof(self):
                pass

            poof = property(get_poof, set_poof, del_poof)  
            
        class B(A):
            V2 = autoex()

            def __init__(self, *args, **kwds):
                super().__init__(*args, **kwds)
                self._poof = 'B'

            @property
            def pie(self):
                return 'B'

            def get_poof(self):
                return 'B'
            
            def set_poof(self, value):
                return

            poof = property(get_poof)   

        class C(B):       
            @property
            def pie(self):
                return 'C'

            @property
            def poo(self):
                return "C"
            
            def get_poof(self):
                return self._poof

            def set_poof(self, value):
                self.__setattr__('_poof', value)

            def del_poof(self):
                del self._poof

            def get_goof(self):
                return super().get_goof()

            poof = property(get_poof, set_poof, del_poof)  

        class D(A):
            V2 = autoex()

            def __init__(self, *args, **kwds):
                super().__init__(*args, **kwds)
                self._poof = 'B'

            @property
            def pie(self):
                return 'B'

            def get_poof(self):
                return 'B'
            
            def set_poof(self, value):
                return
            
            def del_poof(self, value):
                return

            poof = property(get_poof)   
            
        self.assertTrue(is_method_empty(A.get_poof),            msg="A get_poof is empty")
        self.assertTrue(is_method_empty(A.set_poof),            msg="A set_poof is empty")
        self.assertTrue(is_method_empty(A.del_poof),            msg="A del_poof is empty")
        self.assertTrue(is_method_empty(A.__dict__['pie']),     msg="A pie is empty")
        self.assertTrue(is_method_empty(A.__dict__['poo']),     msg="A poo is empty")
        self.assertTrue(is_method_empty(A.__dict__['poof']),    msg="A poof is empty")

        self.assertTrue(is_method_empty(B.del_poof),            msg="B del_poof is empty")
        try:
            self.assertTrue(is_method_empty(B.__dict__['poo']),     msg="B poo is empty")
        except:
            pass
        self.assertFalse(is_method_empty(B.get_poof),           msg="B get_poof not empty")
        self.assertFalse(is_method_empty(B.set_poof),           msg="B set_poof not empty")
        self.assertFalse(is_method_empty(B.__dict__['pie']),    msg="B pie not empty")
        self.assertFalse(is_method_empty(B.__dict__['poof']),   msg="B poof not empty")

        self.assertFalse(is_method_empty(C.get_poof),            msg="C get_poof not empty")
        self.assertFalse(is_method_empty(C.set_poof),            msg="C set_poof not empty")
        self.assertFalse(is_method_empty(C.del_poof),            msg="C del_poof not empty")
        self.assertFalse(is_method_empty(C.__dict__['pie']),     msg="C pie not empty")
        self.assertFalse(is_method_empty(C.__dict__['poo']),     msg="C poo not empty")
        self.assertFalse(is_method_empty(C.__dict__['poof']),    msg="C poof not empty")

        try:
            self.assertTrue(is_method_empty(D.__dict__['poo']),     msg="D poo is empty")
        except:
            pass
        self.assertFalse(is_method_empty(D.get_poof),           msg="D get_poof not empty")
        self.assertFalse(is_method_empty(D.set_poof),           msg="D set_poof not empty")
        self.assertFalse(is_method_empty(D.del_poof),            msg="D del_poof not empty")
        self.assertFalse(is_method_empty(D.__dict__['pie']),    msg="D pie not empty")
        self.assertFalse(is_method_empty(D.__dict__['poof']),   msg="D poof not empty")

        self.assertTrue(is_abstract_enum(A),                    msg="A abstract is enum")
        self.assertTrue(is_abstract_enum(B),                    msg="B abstract is enum")
        self.assertTrue(is_abstract_enum(C),                    msg="C abstract is enum")

        self.assertTrue(is_unimplemented_abstract_enum(A),      msg="A is unimplemented abstract enum")
        self.assertTrue(is_unimplemented_abstract_enum(B),      msg="B is unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(C),     msg="C not unimplemented abstract enum")

        def assert_all_in(col, prefix, *args):
            count = len(args)
            self.assertEqual(count, len(col), msg=f"{prefix} count")
            for arg in args:
                self.assertIn(arg, col, msg=f"{prefix} {arg} in")

        a_abstracts = get_abstract_methods(A)
        b_abstracts = get_abstract_methods(B)
        c_abstracts = get_abstract_methods(C)
        d_abstracts = get_abstract_methods(D)

        assert_all_in(a_abstracts, "A abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')
        assert_all_in(b_abstracts, "B abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')
        assert_all_in(c_abstracts, "C abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')
        assert_all_in(d_abstracts, "D abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')

        a_unimp = get_unimplemented_abstract_methods(A)
        b_unimp = get_unimplemented_abstract_methods(B)
        c_unimp = get_unimplemented_abstract_methods(C)
        d_unimp = get_unimplemented_abstract_methods(D)

        assert_all_in(a_unimp, "A unimplemented abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')
        assert_all_in(b_unimp, "B unimplemented abstracts ", 'poo', 'del_poof')
        assert_all_in(c_unimp, "C unimplemented abstracts ")
        assert_all_in(d_unimp, "B unimplemented abstracts ", 'poo')

        with self.assertRaises(TypeError) as ec:
            v = A(1)
        _assert_invalidabstract(self, ec, A.__name__, 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')

        with self.assertRaises(TypeError) as ec:
            v = B(1)
        _assert_invalidabstract(self, ec, B.__name__, 'poo', 'del_poof')

        v = C(1)

        with self.assertRaises(TypeError) as ec:
            v = D(1)
        _assert_invalidabstract(self, ec, D.__name__, 'poo')


    def test_abstract_enumex(self):        
        class A(ABC, EnumEx, metaclass=EnumExMeta):
            V1 = autoex()
            V2 = autoex()

            @abstractmethod
            def foo(self):
                pass

            @classmethod
            @abstractmethod
            def cfoo(cls):
                pass

            @staticmethod
            @abstractmethod
            def sfoo():
                pass
        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"
                pass

            def cfoo(cls):
                return "cfoo"

            def sfoo():
                return "sfoo"
            
        class C(B):
            pass
        
        class D(C):
            pass
            
        class X(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                pass

            def cfoo(cls):
                pass

            def sfoo():
                pass

        class Y(X):
            pass
        
        class Z(Y):
            pass

        v = B(1 | 2)
        v = C(1 | 2)
        v = D(1 | 2)

        with self.assertRaises(TypeError) as ec:
            v = Z(1 | 2)
        _assert_invalidabstract(self, ec, Z.__name__, 'foo', 'cfoo', 'sfoo')

        with self.assertRaises(TypeError) as ec:
            v = A(1 | 2)
        _assert_invalidabstract(self, ec, A.__name__, 'foo', 'cfoo', 'sfoo')

    def test_abstract_intenum(self):        
        class A(IntEnumEx):
            V1 = autoex()
            V2 = autoex()

            @abstractmethod
            def foo(self):
                pass

            @classmethod
            @abstractmethod
            def cfoo(cls):
                pass

            @staticmethod
            @abstractmethod
            def sfoo():
                pass
        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"
                pass

            def cfoo(cls):
                return "cfoo"

            def sfoo():
                return "sfoo"
            
        class C(B):
            pass
        
        class D(C):
            pass
            
        class X(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                pass

            def cfoo(cls):
                pass

            def sfoo():
                pass

        class Y(X):
            pass
        
        class Z(Y):
            pass

        v = B(1 | 2)
        v = C(1 | 2)
        v = D(1 | 2)

        with self.assertRaises(TypeError) as ec:
            v = Z(1 | 2)
        _assert_invalidabstract(self, ec, Z.__name__, 'foo', 'cfoo', 'sfoo')

        with self.assertRaises(TypeError) as ec:
            v = A(B.V1 | X.V2)
        _assert_invalidabstract(self, ec, A.__name__, 'foo', 'cfoo', 'sfoo')

    def test_abstract_intflag(self):
        class A(ABC, IntFlagEx, metaclass=EnumExMeta):
            V1 = autoex()
            V2 = autoex()

            @abstractmethod
            def foo(self):
                pass

            @classmethod
            @abstractmethod
            def cfoo(cls):
                pass

            @staticmethod
            @abstractmethod
            def sfoo():
                pass

        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"

            def cfoo(cls):
                return "cfoo"

            def sfoo():
                return "sfoo"
            
        class C(B):
            pass
        
        class D(C):
            pass
            
        class X(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"

            def cfoo(cls):
                pass

            def sfoo():
                pass

        class Y(X):
            pass
        
        class Z(Y):
            pass

        v = B(1 | 64)
        v = C(1 | 64)
        v = D(1 | 64)

        with self.assertRaises(TypeError) as ec:
            v = Z(1 | 64)
        _assert_invalidabstract(self, ec, Z.__name__, 'cfoo', 'sfoo')

        with self.assertRaises(TypeError) as ec:
            v = A(B.V3 | X.V4)
        _assert_invalidabstract(self, ec, A.__name__, 'foo', 'cfoo', 'sfoo')

        v = ~B.V1

        with self.assertRaises(TypeError) as ec:
            v = ~X.V4
        _assert_invalidabstract(self, ec, X.__name__, 'cfoo', 'sfoo')
        
    def test_abstract_strenumex(self):        
        class A(ABC, StrEnumEx, metaclass=EnumExMeta):
            V1 = autoex()
            V2 = autoex()

            @abstractmethod
            def foo(self):
                pass

            @classmethod
            @abstractmethod
            def cfoo(cls):
                pass

            @staticmethod
            @abstractmethod
            def sfoo():
                pass
        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"
                pass

            def cfoo(cls):
                return "cfoo"

            def sfoo():
                return "sfoo"
            
        class C(B):
            pass
        
        class D(C):
            pass
            
        class X(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                pass

            def cfoo(cls):
                pass

            def sfoo():
                pass

        class Y(X):
            pass
        
        class Z(Y):
            pass

        v = B('v3')
        v = C('v4')
        v = D('v4')

        with self.assertRaises(TypeError) as ec:
            v = Z('v4')
        _assert_invalidabstract(self, ec, Z.__name__, 'foo', 'cfoo', 'sfoo')

        with self.assertRaises(TypeError) as ec:
            v = A('v2')
        _assert_invalidabstract(self, ec, A.__name__, 'foo', 'cfoo', 'sfoo')

def _assert_invalidabstract(case:unittest.TestCase, ec:unittest.case._AssertRaisesContext, class_name:str, *args):
        count = len(args)
        case.assertEqual(count + 1, len(ec.exception.args))
        case.assertEqual(f"Can't instantiate abstract class {class_name} with abstract method{'' if count == 1 else 's'}", ec.exception.args[0])
        method_args = ec.exception.args[1:]
        for arg in args:
            case.assertIn(arg, method_args)

if __name__ == "__main__":
    unittest.main()