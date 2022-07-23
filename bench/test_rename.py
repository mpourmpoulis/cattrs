import attr
import pytest
from attrs import fields, has

from cattr import BaseConverter, Converter, UnstructureStrategy
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn, override


def to_camel_case(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def change(converter):
    def to_camel_case_unstructure(cls):
        return make_dict_unstructure_fn(
            cls,
            converter,
            **{
                a.name: override(rename=to_camel_case(a.name))
                for a in fields(cls)
            }
        )

    def to_camel_case_structure(cls):
        return make_dict_structure_fn(
            cls,
            converter,
            **{
                a.name: override(rename=to_camel_case(a.name))
                for a in fields(cls)
            }
        )

    converter.register_unstructure_hook_factory(
        has, to_camel_case_unstructure
    )
    converter.register_structure_hook_factory(
        has, to_camel_case_structure
    )


"""Benchmark attrs containing other attrs classes."""


@pytest.mark.parametrize("converter_cls", [Converter])
@pytest.mark.parametrize("rename", [True, False])
@pytest.mark.parametrize(
    "unstructure_strat", [UnstructureStrategy.AS_DICT,
                          # UnstructureStrategy.AS_TUPLE
                          ]
)
def test_unstructure_attrs_nested(benchmark, converter_cls, rename, unstructure_strat):
    c = converter_cls(unstruct_strat=unstructure_strat)
    if rename:
        change(c)

    @attr.define
    class InnerA:
        a_big_cat: int
        b_big_cat: float
        c_big_cat: str
        d_big_cat: bytes

    @attr.define
    class InnerB:
        a_big_cat: int
        b_big_cat: float
        c_big_cat: str
        d_big_cat: bytes

    @attr.define
    class InnerC:
        a_big_cat: int
        b_big_cat: float
        c_big_cat: str
        d_big_cat: bytes

    @attr.define
    class InnerD:
        a_big_cat: int
        b_big_cat: float
        c_big_cat: str
        d_big_cat: bytes

    @attr.define
    class InnerE:
        a_big_cat: int
        b_big_cat: float
        c_big_cat: str
        d_big_cat: bytes

    @attr.define
    class Outer:
        a_big_cat: InnerA
        b_big_cat: InnerB
        c_big_cat: InnerC
        d_big_cat: InnerD
        e: InnerE

    inst = Outer(
        InnerA(1, 1.0, "one", "one".encode()),
        InnerB(2, 2.0, "two", "two".encode()),
        InnerC(3, 3.0, "three", "three".encode()),
        InnerD(4, 4.0, "four", "four".encode()),
        InnerE(5, 5.0, "five", "five".encode()),
    )
    c.unstructure(inst)
    benchmark(c.unstructure, inst)


@pytest.mark.parametrize("converter_cls", [Converter])
@pytest.mark.parametrize("rename", [True, False])
@pytest.mark.parametrize(
    "unstructure_strat", [UnstructureStrategy.AS_DICT,
                          # UnstructureStrategy.AS_TUPLE
                          ]
)
def test_unstruct_attrs_deep_nest(benchmark, converter_cls, rename, unstructure_strat):
    c = converter_cls(unstruct_strat=unstructure_strat)
    if rename:
        change(c)

    @attr.define
    class InnerA:
        a_big_cat: int
        b_big_cat: float
        c_big_cat: str
        d_big_cat: bytes

    @attr.define
    class InnerB:
        a_big_cat: InnerA
        b_big_cat: InnerA
        c_big_cat: InnerA
        d_big_cat: InnerA

    @attr.define
    class InnerC:
        a_big_cat: InnerB
        b_big_cat: InnerB
        c_big_cat: InnerB
        d_big_cat: InnerB

    @attr.define
    class InnerD:
        a_big_cat: InnerC
        b_big_cat: InnerC
        c_big_cat: InnerC
        d_big_cat: InnerC

    @attr.define
    class InnerE:
        a_big_cat: InnerD
        b_big_cat: InnerD
        c_big_cat: InnerD
        d_big_cat: InnerD

    @attr.define
    class Outer:
        a_small_dog: InnerE
        b_small_dog: InnerE
        c_small_dog: InnerE
        d_small_dog: InnerE

    def make_inner_a(): return InnerA(1, 1.0, "one", "one".encode())
    def make_inner_b(): return InnerB(*[make_inner_a() for _ in range(4)])
    def make_inner_c(): return InnerC(*[make_inner_b() for _ in range(4)])
    def make_inner_d(): return InnerD(*[make_inner_c() for _ in range(4)])
    def make_inner_e(): return InnerE(*[make_inner_d() for _ in range(4)])

    inst = Outer(*[make_inner_e() for _ in range(4)])
    result = benchmark(c.unstructure, inst)
    if rename:
        assert "aSmallDog" in result
    else:
        assert "a_small_dog" in result
