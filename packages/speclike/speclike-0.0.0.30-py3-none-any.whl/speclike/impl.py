from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
import sys
from types import GenericAlias, MappingProxyType
from typing import Any, Callable, Generic, Iterator, Protocol, Self, Type, TypeVar, cast, get_type_hints

import inspect

import pytest


MOD_NAME = "speclike"

_CA = TypeVar("_CA", bound = Callable)

_TARGET_KIND = f"_{MOD_NAME}_target_kind"
_PARAMS_UNIT = f"_{MOD_NAME}_params_unit"
_REF_DISPATCHER = f"_{MOD_NAME}_dispatcher"
_NAME_ON_NS = f"_{MOD_NAME}_name_on_namespace"
_OWNER = f"_{MOD_NAME}_owner"
_ACT_SIGNATURE = f"_{MOD_NAME}_act_signature"
_PARAM_EXPECTED_EXCTYPE = f"_{MOD_NAME}_expected_exctype"

_ACTOR_FUNCTION_NAME = "_"


class TargetKind(Enum):
    _UNDETERMINED = 0 # not used at current implementation.
    EX_SPEC_ACT = auto()
    EX_SPEC_DISPATCHER = auto()
    EX_SPEC_DISPATCHER_IN_CLASS = auto()
    INDIVIDUAL_TEST_BODY = auto()


class _TailDecorator(Protocol):
    def __call__(self, target: _CA) -> _CA:
        ...

class _ExActorDecorator(_TailDecorator, Protocol):
    pass


class _AbstractPicker(ABC):
    @abstractmethod
    def _process_target(self, taraget: _CA, params: dict[str, Any]) -> _CA | None:
        ...

class _TestBodyAndActorPicker(_AbstractPicker):

    def __init__(self):
        self._ref_dispatcher = None

    def _process_target(self, target: _CA, params: dict[str, Any]) -> _CA | None:
        if target.__name__ == _ACTOR_FUNCTION_NAME:
            # If the name is "_", treat it as an actor and set reference to dispatcher.
            if self._ref_dispatcher is None:
                raise RuntimeError(
                    f"Missing dispatcher correspond to {target.__qualname__}."
                )
            if hasattr(target, "pytestmark"):
                raise ValueError(
                    f"Pytestmark can not be applied to actor. " + 
                    f"Actor name {target.__qualname__}"
                )
            setattr(target, _TARGET_KIND, TargetKind.EX_SPEC_ACT)
            setattr(target, _REF_DISPATCHER, self._ref_dispatcher)
            return target
        
        if _PARAM_EXPECTED_EXCTYPE in params:
            setattr(target, _PARAM_EXPECTED_EXCTYPE, params[_PARAM_EXPECTED_EXCTYPE])

        setattr(target, _TARGET_KIND, TargetKind.INDIVIDUAL_TEST_BODY)
        return None

    def _get_ex_actor_decorator(
        #self, deco: _Decorator, ex_dispatcher: Callable
        self, deco: _Specifier, ex_dispatcher: Callable
    ) -> _ExActorDecorator:
        m = getattr(ex_dispatcher, _TARGET_KIND, None)
        error = m is None
        # None leaves the result unchanged (below).
        error |= m not in (
            TargetKind.EX_SPEC_DISPATCHER, TargetKind.EX_SPEC_DISPATCHER_IN_CLASS
        )
        if error:
            raise TypeError(
                "ex_dispatcher function must be decorated as dispatcher. " +
                (f"but decorated '{m.name}'." if isinstance(m, TargetKind) else "")
            )
        self._ref_dispatcher = ex_dispatcher

        def ex_actor_decorator(target: _CA) -> _CA:
            return deco.__call__(target)
        
        return ex_actor_decorator

class PRM:
    """
    Parameter Prefix Rules
    
    The prefix determines the nature of each parameter:
    
    - AO (Actor-Only, prefix '_'):  
      Provided by dispatcher, passed to actor.  
      Not parametrized.  
      Example: `_obj=Message` - dispatcher creates obj, actor uses it  
    
    - AP (Actor-Parametrized, no prefix):  
      Parametrized value, passed to actor.  
      Example: `value=int` - test runs with different values  
    
    - PO (Parametrized-Only, prefix '__'):  
      Parametrized value, NOT passed to actor.  
      Example: `__expected=int` - dispatcher uses for assertion  
    
    Parameters must be ordered: AO -> AP -> PO  
    (any category can be omitted)  
    
    Usage:
        @ex.follows((1, 10), (2, 20))  
        def check(p = PRM(_ctx=Context, input=int, __expected=int)):  
            _ctx = Context()  
            result = p.act(_ctx, p.input)  
            assert result == __expected  
    """

    NON_PARAMETRIZE = "_"
    NON_ACTOR = "__"

    class ParamKind(Enum):
        AO = 0
        AP = 1
        PO = 2

        @classmethod
        def get(cls, param_name: str) -> "PRM.ParamKind":
            if param_name.startswith(PRM.NON_ACTOR):
                return cls.PO
            elif param_name.startswith(PRM.NON_PARAMETRIZE):
                return cls.AO
            else:
                return cls.AP
        
        @classmethod
        def ensure_order(
            cls, f: "PRM.ParamKind", t: "PRM.ParamKind"
        ):
            if f == cls.AP and t == cls.AO:
                pass
            elif f == cls.PO and (
                t == cls.AO or t == cls.AP
            ):
                pass
            else:
                return
            raise TypeError(
                "Parameter order is invalid. "
                f"It can not be specified '{t.name}' after '{f.name}'. "
                f"See {PRM.__name__} docustring."
            )
            


    __slots__ = ("_parameter_defs", "_act_param_defs", "_parametrize_names")

    def __init__(self, **parameter_defs):
        act_param_defs = {}
        parametrize_names = []

        Kind = PRM.ParamKind
        prev_kind = PRM.ParamKind.AO
        for k, v in parameter_defs.items():
            if not (isinstance(k, str) and k.isidentifier()):
                raise TypeError(
                    f"Parameter name must be str and python identifier. "
                    f"but received '{k}'."
                )
            if not isinstance(v, (type, GenericAlias)):
                raise TypeError(
                    f"Invalid type definition for act parameter '{k}': " + 
                    f"expected a type or generic type alias (e.g. list[int]), " + 
                    f"but received '{type(v).__name__}'."
                )
            
            current_kind = Kind.get(k)
            Kind.ensure_order(prev_kind, current_kind)
            _ensure_valid_param_names_as_param_bridge(k)
            
            if current_kind == Kind.AO or current_kind == Kind.AP:
                act_param_defs[k] = v
            
            if current_kind == Kind.PO or current_kind == Kind.AP:
                parametrize_names.append(k)

            prev_kind = current_kind
            
        self._parameter_defs = parameter_defs
        self._act_param_defs = act_param_defs
        self._parametrize_names = parametrize_names

    def ensure_actor_has_correct_signature(
        self, disp_name: str, act: Callable, actsig_formatter: Callable
    ) -> None:
        error_prefix = f"Invalid actor definition for '{disp_name}': "
        sig = inspect.signature(act)
        hints = get_type_hints(act)
        params = list(sig.parameters.values())[1:]  # skip 'self'

        # signatures string for error messages
        actual_sig = actsig_formatter(act)
        expected_sig = (
            "fn(self, " + ", ".join(
                f"{n}: {t.__name__}" for n, t in self._act_param_defs.items()
            ) + ")"
        )
        if expected_sig == "fn(self, )":
            expected_sig = "fn(self)"

        for i, (exp_name, exp_type) in enumerate(self._act_param_defs.items()):
            if i >= len(params):
                raise _ActorDefinitionError(
                    error_prefix +
                    f"It has fewer parameters " +
                    f"than expected (missing index {i}).\n" +
                    f"Expected signature: {expected_sig}\n" +
                    f"Actual signature: {actual_sig}"
                )

            param = params[i]

            # name check
            if param.name != exp_name:
                raise _ActorDefinitionError(
                    error_prefix +
                    f"Parameter name mismatch: " +
                    f"expected '{exp_name}', but received '{param.name}'.\n" +
                    f"Expected signature: {expected_sig}\n" +
                    f"Actual signature: {actual_sig}"
                )

            # type check (only if act annotates it)
            actual_type = hints.get(param.name)
            if actual_type is not None and actual_type != exp_type:
                raise _ActorDefinitionError(
                    error_prefix +
                    f"Type mismatch at parameter '{param.name}': " +
                    f"expected '{exp_type.__name__}', " +
                    f"but received '{actual_type.__name__}'.\n" +
                    f"Expected signature: {expected_sig}\n" +
                    f"Actual signature: {actual_sig}"
                )
        
        if len(params) > len(self._parameter_defs):
            extra_params = [p.name for p in params[len(self._parameter_defs):]]
            raise _ActorDefinitionError(
                error_prefix +
                f"It has unexpected extra parameter(s): " +
                f"{', '.join(extra_params)}.\n"
                f"Expected signature: {expected_sig}\n" + 
                f"Actual signature: {actual_sig}"
            )
    
    def get_test_signature(self, owner: str | None = None):
        """Specify owner when the signature for method. 'self' or "cls'."""
        Parameter = inspect.Parameter
        params = []
        if owner is not None:
            params.append(Parameter(owner, Parameter.POSITIONAL_OR_KEYWORD))
        for pname in self._parametrize_names:
            params.append(Parameter(pname, Parameter.POSITIONAL_OR_KEYWORD))
        return inspect.Signature(params)
    
    def add_implicitly_params(self, src: Callable, params: dict[str, Any]) -> None:
        if hasattr(src, _PARAM_EXPECTED_EXCTYPE):
            key = f"{_IMPLICITLY_ADDED_PARAM_PREFIX}exctype"
            value = getattr(src,_PARAM_EXPECTED_EXCTYPE)
            params[key] = value
    
    def get_bridge(self, act: Callable, params: dict[str, Any]):
        return _ParamsBridge(act, MappingProxyType(params))

    # ============================================================
    # These methods mimic the interface of _ParamsBridge that is
    # actually passed to the dispatcher. They exist solely to
    # propagate static type information and are never called at
    # runtime.
    # ============================================================
    @property
    def act(self, *args, **kwargs) -> Callable:
        raise RuntimeError("Unexpected call.")

    def type(self, t: type[_T]) -> _TypedGetter[_T]:
        raise RuntimeError("Unexpected call.")

    def __getattr__(self, key) -> Any:
        raise RuntimeError("Unexpected call.")
    # ============================================================
    # ============================================================

_T = TypeVar("_T")

class _TypedGetter(Generic[_T]):
    __slots__ = ("_src", "_type")
    def __init__(self, src:_ParamsBridge, t: Type[_T]):
        if not isinstance(t, type):
            raise TypeError(
                "t must be a type instance, "
                f"but received '{type(t).__name__}'."
            )
        self._src = src
        self._type = t
    
    def __getattr__(self, key) -> _T:
        src = object.__getattribute__(self, "_src")
        typ = object.__getattribute__(self, "_type")
        attr = getattr(src, key)
        if not isinstance(attr, typ):
            raise TypeError(
                "Parameter type missmatch, "
                f"expected type '{typ.__name__}', "
                f"but actual type '{type(attr).__name__}'."
            )
        return cast(_T, attr)

_RESERVED_PARAM_NAMES = (
    "act",
    "type",
    "_ParamsBridge_act",
    "_ParamsBridge_params",
)

_IMPLICITLY_ADDED_PARAM_PREFIX = "__sl_"

def _ensure_valid_param_names_as_param_bridge(pname: str):
    """Define it outside the _ParamsBridge class to avoid attribute definition."""

    if pname in _RESERVED_PARAM_NAMES or (
        pname.startswith(_IMPLICITLY_ADDED_PARAM_PREFIX)
    ):
        raise TypeError(
        f"Invalid parameter name '{pname}'. "
        f"The names {_RESERVED_PARAM_NAMES} are reserved and cannot be used, "
        f"and any parameter name starting with the prefix "
        f"'{_IMPLICITLY_ADDED_PARAM_PREFIX}' is also reserved."
)

@dataclass(slots = True, frozen = True)
class _ParamsBridge:

    _ParamsBridge_act: Callable[..., Any]
    _ParamsBridge_params: MappingProxyType[str, Any]

    @property
    def act(self):
        return self._ParamsBridge_act

    def __getattr__(self, key):
        params = object.__getattribute__(self, "_ParamsBridge_params")

        if key in params:
            return params[key]

        if key.startswith("_") and "__" in key and key.index("__") > 1:
            suffix = key[key.index("__"):]
            if suffix in params:
                return params[suffix]

        available = ", ".join(params.keys())
        raise AttributeError(
            f"'{type(self).__name__}' has no attribute '{key}'. "
            f"Available: {available}"
        )
    
    def type(self, t: type[_T]) -> _TypedGetter[_T]:
        return _TypedGetter(self, t)

    def __repr__(self) -> str:
        params = object.__getattribute__(self, "_ParamsBridge_params")
        items = ", ".join(f"{k}={v!r}" for k, v in params.items())
        return f"{type(self).__name__}({items})"



class _DispatcherPicker(_AbstractPicker):
    def _process_target(self, target: _CA, params: dict[str, Any]) -> _CA | None:
        if target.__name__ == _ACTOR_FUNCTION_NAME:
            raise NameError(
                "Dispatcher picker can not handle actor function."
                f"Function name '{_ACTOR_FUNCTION_NAME}' represents actor function."
            )
        sig = inspect.signature(target)
        if len(sig.parameters) > 2:
            raise TypeError(
                "Dispatcher function can only have 'owner' and/or one parameters"
                f"(Which must have '{PRM.__name__}' "
                "as its default or type annotation), "
                f"but received a dispatcher with 'fn{sig}'."
            )
        found_prm = False
        for k, v in sig.parameters.items():
            if isinstance(v.default, PRM):
                if found_prm:
                    raise TypeError(
                        f"Multiple {PRM.__name__} found. Last one is on '{k}'."
                    )
                found_prm = True
                setattr(target, _ACT_SIGNATURE, v.default)

        if not found_prm:
            setattr(target, _ACT_SIGNATURE, PRM())
        setattr(target, _TARGET_KIND, TargetKind.EX_SPEC_DISPATCHER)

        if _PARAM_EXPECTED_EXCTYPE in params:
            setattr(target, _PARAM_EXPECTED_EXCTYPE, params[_PARAM_EXPECTED_EXCTYPE])
        
        return None


class _Specifier:
    """
    single-use decorator.

    Each instance is disposable and cannot be reused once applied.  
    A function named "_" is treated as an actor of an externally defined spec.
    """

    def __init__(
        self,
        op: _AbstractPicker,
        label_objects: Iterator | None = None,
    ):
        self._op = op
        self._label_objects = label_objects
        self._parametrize_unit = None
        self._ptms = []
        self._returns_target_already = False
        self._expected_exctype = None

    def __call__(self, target: _CA) -> _CA:
        if self._returns_target_already:
            raise RuntimeError(
                f"Attempted to process {target.__qualname__}, "
                f"but the decorator has already finished."
            )
        
        shortcut = self._op._process_target(
            target, {
                _PARAM_EXPECTED_EXCTYPE: self._expected_exctype
            }
        )
        if shortcut is not None:
            self._returns_target_already = True
            return shortcut
        
        self._prepare_pytestmark_attr_as_list(target)

        if self._label_objects is not None:
            target.pytestmark.append(
                getattr(pytest.mark, MOD_NAME)(*self._label_objects)
            )
        if self._parametrize_unit:
            setattr(target, _PARAMS_UNIT, self._parametrize_unit)
        target.pytestmark.extend(self._ptms)

        self._returns_target_already = True
        return target

    def follows(self, *argvalues, **options) -> Self:
        self._parametrize_unit = argvalues, options
        return self
    
    @property
    def skip(self) -> Self:
        return self.ptm(pytest.mark.skip("User specified."))
    
    @property
    def SKIP(self) -> Self:
        return self.skip

    def raises(self, exctype: type[BaseException]):
        self._expected_exctype = exctype
        return self

    def ptm(self, *pytestmarks) -> Self:
        self._ptms.extend(pytestmarks)
        return self

    def _prepare_pytestmark_attr_as_list(self, target: Callable) -> None:
        ptm = getattr(target, "pytestmark", None)
        if ptm:
            if not isinstance(ptm, list):
                ptm = list(ptm)
        else:
            ptm = []
        setattr(target, "pytestmark", ptm)

class _ExSpecNamespace(dict):
    def __init__(self, cls_name: str):
        self.__cls_name = cls_name

    def __setitem__(self, key, value):
        if hasattr(value, _TARGET_KIND):
            kind = getattr(value, _TARGET_KIND)
            if  kind is TargetKind.EX_SPEC_DISPATCHER:
                setattr(value, _TARGET_KIND, TargetKind.EX_SPEC_DISPATCHER_IN_CLASS)
                setattr(value, _NAME_ON_NS, key)
            else:
                raise TypeError(
                    f"Marked method in {self.__cls_name} " + 
                    f"must be marked '{TargetKind.EX_SPEC_DISPATCHER.name}'. " + 
                    f"but it marked with '{kind.name}"
                )
        super().__setitem__(key, value)
            

class _ExSpecMeta(type):

    @classmethod
    def __prepare__(mcls, name, bases, **kwargs) -> _ExSpecNamespace:
        return _ExSpecNamespace(name)

    def __new__(mcls, name, bases, namespace: _ExSpecNamespace):
        cls = super().__new__(mcls, name, bases, namespace)
        for v in cls.__dict__.values():
            if hasattr(v, _TARGET_KIND):
                if getattr(v, _TARGET_KIND) in (
                    TargetKind.EX_SPEC_DISPATCHER,
                    TargetKind.EX_SPEC_DISPATCHER_IN_CLASS
                ):
                    setattr(v, _OWNER, cls)
        return cls

class ExSpec(metaclass = _ExSpecMeta):
    """
    Base class for externally defined spec dispatchers.

    "Ex" stands for "externally defined" (not "external test").
    Inherit this when grouping dispatcher functions defined
    outside of a Spec class.
    """
    pass


class SpecifierSeed(ABC):
    @classmethod
    @abstractmethod
    def _get_picker(cls) -> _AbstractPicker:
        ...

class Layer(ABC):
    _MAX_DEPTH = 10

    def __init__(self):
        self._assigned_name = ""
        self.__root = None

    def __set_name__(self, owner, name):
        self._assigned_name = name
    
    def __get__(self, ins, owner) -> Self:
        self.__root = ins
        return self
    
    @abstractmethod
    def _get_label(self) -> object:
        ...

    def _get_specifier_unit(self) -> tuple["Entry", Iterator[object]]:
        label_objects = []
        layer = self
        entry = None
        for _ in range(self._MAX_DEPTH):
            if isinstance(layer, Entry):
                entry = layer
            label = layer._get_label()
            label_objects.append(label)
            if layer.__root is not None:
                layer = layer.__root
                continue
            else:
                break
        else:
            raise RuntimeError(f"Too deep a layer structure: {self._MAX_DEPTH}")
        
        if entry is None:
            raise RuntimeError(f"Entry is missing.")

        return entry, reversed(label_objects)

class Minor(Layer):
    def _get_label(self) -> str:
        return self._assigned_name
    
    def _create_specifier(self) -> _Specifier:
        entry, label_objects = self._get_specifier_unit()
        picker = entry._get_picker()
        return _Specifier(picker, label_objects)
    
    def __call__(self, target: _CA) -> _CA:
        return self._create_specifier().__call__(target)

    def follows(self, *argsvalue, **options) -> _Specifier:
        return self._create_specifier().follows(*argsvalue, **options)

    @property
    def skip(self) -> _Specifier:
        return self._create_specifier().skip

    @property
    def SKIP(self) -> _Specifier:
        return self._create_specifier().SKIP

    def raises(self, exctype: type[BaseException]) -> _Specifier:
        return self._create_specifier().raises(exctype)

    def ptm(self, *pytestmarks) -> _Specifier:
        return self._create_specifier().ptm(*pytestmarks)

class Intermediate(Layer):

    def _get_label(self) -> str:
        return self._assigned_name
    
    scenario = Minor()
    performance = Minor()
    resource = Minor()
    network = Minor()
    concurrency = Minor()
    regression = Minor()
    experiment = Minor()
    tmp = Minor()

    usecase = Minor()
    api = Minor()
    input = Minor()
    output = Minor()
    io = Minor()
    feature = Minor()
    
    default = Minor()
    init = Minor()
    init_fail = Minor()
    cleanup = Minor()
    cleanup_fail = Minor()
    edge = Minor()
    edge_pass = Minor()
    edge_fail = Minor()
    stress = Minor()
    legacy = Minor()
    legacy_fail = Minor()
    violation = Minor()
    recovers = Minor()
    error = Minor()
    critical = Minor()
    silent = Minor()
    NOTE = Minor()
    IMPORTANT = Minor()

    security = Minor()
    compatibility = Minor()
    sync = Minor()
    async_ = Minor()
    timeout = Minor()

class Major(Minor, Layer):

    def _get_label(self) -> str:
        return self._assigned_name
    
    scenario = Intermediate()
    performance = Intermediate()
    resource = Intermediate()
    network = Intermediate()
    concurrency = Intermediate()
    regression = Intermediate()
    experiment = Intermediate()
    tmp = Intermediate()

    usecase = Intermediate()
    api = Intermediate()
    input = Intermediate()
    output = Intermediate()
    io = Intermediate()
    feature = Intermediate()
    
    default = Intermediate()
    init = Intermediate()
    init_fail = Intermediate()
    cleanup = Intermediate()
    cleanup_fail = Intermediate()
    edge = Intermediate()
    edge_pass = Intermediate()
    edge_fail = Intermediate()
    stress = Intermediate()
    legacy = Intermediate()
    legacy_fail = Intermediate()
    violation = Intermediate()
    recovers = Intermediate()
    error = Intermediate()
    critical = Intermediate()
    silent = Intermediate()
    NOTE = Intermediate()
    IMPORTANT = Intermediate()

    security = Intermediate()
    compatibility = Intermediate()
    sync = Intermediate()
    async_ = Intermediate()
    timeout = Intermediate()

class Entry(Minor, SpecifierSeed, Layer):
    def _get_label(self) -> str:
        raise RuntimeError("Unexpected call.")

    @abstractmethod
    def _get_picker(self) -> _AbstractPicker:
        ...
    
    scenario = Major()
    performance = Major()
    resource = Major()
    network = Major()
    concurrency = Major()
    regression = Major()
    experiment = Major()
    tmp = Major()

    usecase = Major()
    api = Major()
    input = Major()
    output = Major()
    io = Major()
    feature = Major()
    
    default = Major()
    init = Major()
    init_fail = Major()
    cleanup = Major()
    cleanup_fail = Major()
    edge = Major()
    edge_pass = Major()
    edge_fail = Major()
    stress = Major()
    legacy = Major()
    legacy_fail = Major()
    violation = Major()
    recovers = Major()
    error = Major()
    critical = Major()
    silent = Major()
    NOTE = Major()
    IMPORTANT = Major()

    security = Major()
    compatibility = Major()
    sync = Major()
    async_ = Major()
    timeout = Major()


class Case(Entry):
    @classmethod
    def _get_picker(cls) -> _TestBodyAndActorPicker:
        return _TestBodyAndActorPicker()
    
    def _get_label(self) -> str:
        return "case"

    def ex(self, ex_dispatcher: Callable) -> _ExActorDecorator:
        picker = self._get_picker()
        specifier = _Specifier(picker)
        return picker._get_ex_actor_decorator(specifier, ex_dispatcher)
    
class Ex(Entry):
    @classmethod
    def _get_picker(cls) -> _AbstractPicker:
        return _DispatcherPicker()
    
    def _get_label(self) -> str:
        return "ex"

    
class _SpecNamespace(dict):
    def __init__(self, cls_name: str):
        self.__cls_name = cls_name
        self.__actors = []
    
    def __setitem__(self, key, value):
        if hasattr(value, _TARGET_KIND):
            kind = getattr(value, _TARGET_KIND)
            if  kind is TargetKind.INDIVIDUAL_TEST_BODY:
                setattr(value, _NAME_ON_NS, key)
            elif kind is TargetKind.EX_SPEC_ACT:
                self.__actors.append(value)
                return
            else:
                raise TypeError(
                    f"Marked method in {self.__cls_name} " + 
                    f"must be marked '{TargetKind.INDIVIDUAL_TEST_BODY.name}'. " + 
                    f"but it marked with '{kind.name}"
                )
        super().__setitem__(key, value)
    
    def get_actors(self) -> list[Callable]:
        return list(self.__actors)

    def get_as_dict(self) -> dict[str, Any]:
        return dict(self)

    # override dict.clear()
    def clear(self):
        super().clear()
        self.__actors.clear()

class _ActorDefinitionError(TypeError):
    pass

class _SpecMeta(type):

    @classmethod
    def __prepare__(mcls, name, bases, **kwargs) -> _SpecNamespace:
        return _SpecNamespace(name)

    def __new__(mcls, name, bases, namespace: _SpecNamespace):

        if bases == (object,):
            return super().__new__(mcls, name, bases, namespace)

        generated_funcs: dict[str, Callable] = {}
        
        for v in namespace.values():
            if hasattr(v, _TARGET_KIND):
                kind = getattr(v, _TARGET_KIND)
                if kind is TargetKind.INDIVIDUAL_TEST_BODY:
                    test_body = v
                    test_body_name = getattr(test_body, _NAME_ON_NS)
                    test_name = mcls._get_test_name(test_body_name)
                    test = mcls._create_in_test(test_body)
                    # An individual test body is assumed to already have 
                    # a valid signature in the form of fn(self, p1, p2, ...).
                    test = mcls._copy_signature(test_body, test)
                    test = mcls._init_and_copy_pytestmark_attr(test_body, test)
                    test = mcls._synth_and_set_parametrize_mark(test_body, test)
                    test = mcls._copy_defined_lineno(test_body, test)
                    
                    generated_funcs[test_name] = test
        
        for act in namespace.get_actors():
            dispatcher = getattr(act, _REF_DISPATCHER)
            ex_param_def = getattr(dispatcher, _ACT_SIGNATURE)
            assert isinstance(ex_param_def, PRM)
            disp_name = mcls._get_dispatcher_name(dispatcher)
            act_name = mcls._get_act_name(disp_name)
            test_name = mcls._get_test_name(disp_name)

            try:
                # passes dipatcher name for structing error message.
                ex_param_def.ensure_actor_has_correct_signature(
                    disp_name, act, mcls._format_signature_with_types
                )
            except _ActorDefinitionError as e:
                try:
                    fftest = mcls._create_force_fail_test_function(e)
                    fftest = mcls._copy_defined_lineno(act, fftest)
                    generated_funcs[test_name] = fftest
                    continue
                except Exception as e:
                    raise e

            # Create a bridge to enable act_name to retrieve a bound method 
            # from the owner instance.
            act_bridge = mcls._create_act_bridge(act)
            generated_funcs[act_name] = act_bridge
            test = mcls._create_ex_test(
                disp_name, act_name, dispatcher, act, ex_param_def
            )
            #Passing through this method (below) normalizes 
            # the function signature to fn(self, p1, p2, ...).
            test.__signature__ = ex_param_def.get_test_signature("self")
            test = mcls._init_and_copy_pytestmark_attr(dispatcher, test)
            test = mcls._synth_and_set_parametrize_mark(dispatcher, test)
            test = mcls._copy_defined_lineno(act, test)
            
            generated_funcs[test_name] = test
        
        namespace_for_type = namespace.get_as_dict()
        namespace.clear()

        namespace_for_type.update(generated_funcs)
        # Add "Test" to class name if class name does not start with "Test".
        gen_cls_name = mcls._get_spec_class_name(name)
        
        cls = super().__new__(mcls, gen_cls_name, bases, namespace_for_type)

        if gen_cls_name != name:
            module = sys.modules[cls.__module__]
            setattr(module, gen_cls_name, cls)
            if name in module.__dict__:
                delattr(module, name)
            
        return cls
    
    @classmethod
    def _create_force_fail_test_function(mcls, e: Exception):
        def generated_force_fail_test(self):
            pytest.fail(f"This is FORCE FAILED test reason as below.\n{e}")
        return generated_force_fail_test

    @classmethod
    def _get_dispatcher_name(mcls, dispatcher: Callable):
        name_on_ns = getattr(dispatcher, _NAME_ON_NS, None)
        return name_on_ns if name_on_ns else dispatcher.__name__

    @classmethod
    def _get_test_name(mcls, name) -> str:
        return f"test_{name}"
    
    @classmethod
    def _get_act_name(mcls, disp_name) -> str:
        return f"act_for_{disp_name}"
    
    @classmethod
    def _get_spec_class_name(mcls, cls_name: str) -> str:
        if cls_name.startswith("Test"):
            return cls_name
        return f"Test{cls_name}"

    @classmethod
    def _format_signature_with_types(mcls, func: Callable) -> str:
        sig = inspect.signature(func)
        hints = get_type_hints(func)

        formatted_params = []
        for name in sig.parameters.keys():
            if name in hints:
                tp = hints[name]
                # Handle type or GenericAlias
                if isinstance(tp, type):
                    type_str = tp.__name__
                else:
                    type_str = repr(tp).replace("typing.", "")
                formatted_params.append(f"{name}: {type_str}")
            else:
                formatted_params.append(name)

        return f"fn({', '.join(formatted_params)})"
    
    @classmethod
    def _create_act_bridge(mcls, act: Callable) -> Callable:
        if inspect.iscoroutinefunction(act):
            async def act_for_dispatcher_async(self, *args, **kwargs):
                return await act(self, *args, **kwargs)
            generated_act = act_for_dispatcher_async
        else:
            def act_for_dispatcher(self, *args, **kwargs):
                return act(self, *args, **kwargs)
            generated_act = act_for_dispatcher
        
        return generated_act

    @classmethod
    def _create_ex_test(
            mcls,
            disp_name: str,
            act_name: str,
            dispatcher: Callable,
            act: Callable,
            ex_param_def: PRM
    ) -> Callable:
        is_d_async = inspect.iscoroutinefunction(dispatcher)
        is_a_async = inspect.iscoroutinefunction(act)
        if not is_d_async and is_a_async:
            raise TypeError("Ex test actor must be sync function.")
        disp_owner = getattr(dispatcher, _OWNER, None)
        if disp_owner:
            bound_disp_getter = lambda: getattr(disp_owner(), disp_name)
        else:
            # For dispatcher defined on top-level.
            bound_disp_getter = lambda: dispatcher
        generated_test = None
        if is_d_async:
            async def ex_test_async(self, **kwargs):
                bound_act = getattr(self, act_name)
                ex_param_def.add_implicitly_params(dispatcher, kwargs)
                params_bridge = ex_param_def.get_bridge(bound_act, kwargs)
                await bound_disp_getter()(params_bridge)
            generated_test = ex_test_async
        else:
            def ex_test(self, **kwargs):
                bound_act = getattr(self, act_name)
                ex_param_def.add_implicitly_params(dispatcher, kwargs)
                params_bridge = ex_param_def.get_bridge(bound_act, kwargs)
                bound_disp_getter()(params_bridge)
            generated_test = ex_test

        return generated_test
    
    @classmethod
    def _create_in_test(mcls, test_body: Callable):
        test_body_ns_name = getattr(test_body, _NAME_ON_NS)
        generated_test = None
        if inspect.iscoroutinefunction(test_body):
            async def in_test_async(self, *args, **kwargs):
                bound_act = getattr(self, test_body_ns_name)
                await self.dispatch_async(
                    test_body_ns_name, bound_act, *args, **kwargs
                )
            generated_test = in_test_async
        else:
            def in_test(self, *args, **kwargs):
                bound_act = getattr(self, test_body_ns_name)
                self.dispatch(
                    test_body_ns_name, bound_act, *args, **kwargs
                )
            generated_test = in_test
        
        return generated_test

    @classmethod
    def _copy_signature(mcls, src: Callable, dst: Callable) -> Callable:
        dst.__signature__ = inspect.signature(src)
        return dst
    
    @classmethod
    def _synth_and_set_parametrize_mark(mcls, src: Callable, dst: Callable) -> Callable:
        unit = getattr(src, _PARAMS_UNIT, ())
        if unit:
            valueargs, options = unit
            sig = inspect.signature(dst)
            params = list(sig.parameters.keys())[1:]
            argnames = ",".join(params)

            dst.pytestmark.append(
                pytest.mark.parametrize(argnames, valueargs, **options)
            )
        return dst

    @classmethod
    def _copy_defined_lineno(mcls, src: Callable, dst: Callable) -> Callable:
        code = dst.__code__.replace(
            co_firstlineno=src.__code__.co_firstlineno,
            co_filename=src.__code__.co_filename,
        )
        dst.__code__ = code
        dst.__module__ = src.__module__
        return dst
    
    @classmethod
    def _init_and_copy_pytestmark_attr(mcls, src: Any, dst: Callable) -> Callable:
        setattr(dst, "pytestmark", getattr(src, "pytestmark").copy())
        return dst


class Spec(metaclass = _SpecMeta):
    """
    Base class for generated spec tests.

    Subclass this to customize how individual tests are invoked.
    Override `dispatch()` or `dispatch_async()` to change
    call signatures or invocation behavior of generated tests.
    """
    __slots__ = ()

    @classmethod
    def get_decorators(cls) -> tuple[Case, Ex]:
        return Case(), Ex()

    async def dispatch_async(self, name: str, actor: Callable, *args, **kwargs):
        await actor(*args, **kwargs)
    
    def dispatch(self, name: str, actor: Callable, *args, **kwargs):
        actor(*args, **kwargs)
