try:
    import jax.numpy as jnp
    _HAVE_JAX = True
except ImportError:
    _HAVE_JAX = False
    import numpy as jnp

import numpy as np

import sympy

from sympy import (
    Matrix,
    lambdify,
    powsimp,
    init_printing,
    zeros
)

from typing import Union, Callable
from types import SimpleNamespace
from attrs import define, field



from library.model.boundary_conditions import BoundaryConditions
from library.model.initial_conditions import InitialConditions, Constant
from library.python.misc.misc import Zstruct

init_printing()


def vectorize_constant_sympy_expressions(expr, Q, Qaux):
    symbol_list = Q.get_list() + Qaux.get_list()
    q0 = Q[0]

    rows, cols = expr.shape

    new_data = []

    for i in range(rows):
        row = []
        for j in range(cols):
            entry = expr[i, j]
            if not any(symbol in entry.free_symbols for symbol in symbol_list):
                if entry == 0:
                    row.append(10 ** (-20) * q0)
                else:
                    row.append(entry + 10 ** (-20) * q0)
            else:
                row.append(entry)
        new_data.append(row)

    return Matrix(new_data)

def default_simplify(expr):
    return powsimp(expr, combine="all", force=False, deep=True)

def get_default_function_arguments():
    return Zstruct(
        time=sympy.symbols("t", real=True),
        position=register_sympy_attribute(3, "X"),
        distance=sympy.symbols("dX", real=True),
        p=register_sympy_attribute(0, "p_"),
        n=register_sympy_attribute(3, "n"),
    )

@define(frozen=True, slots=True, kw_only=True)
class Core:
    """
    Generic (virtual) model implementation.
    """
    
    boundary_conditions: BoundaryConditions 
    
    name: str = "Model"
    dimension: int = 1

    initial_conditions: InitialConditions = field(factory=Constant)
    aux_initial_conditions: InitialConditions = field(factory=Constant)
    
    parameters: Zstruct = field(factory=lambda: Zstruct())
    
    function_arguments: Zstruct = field(factory=lambda: get_default_function_arguments())
    variables: Zstruct = field(init=False, default=1)
    positive_variables: Union[dict, list, None] = field(default=None)
    aux_variables: Zstruct = field(default=0)



    _simplify: Callable = field(factory=lambda: default_simplify)

    # Derived fields initialized in __attrs_post_init__
    _default_parameters: dict = field(init=False, factory=dict)
    n_variables: int = field(init=False)
    n_aux_variables: int = field(init=False)
    n_parameters: int = field(init=False)
    parameter_symbols: Zstruct = field(init=False)
    


    def __attrs_post_init__(self):
        
        # Use object.__setattr__ because class is frozen
        object.__setattr__(self, "variables", register_sympy_attribute(self.variables, "q", self.positive_variables))
        object.__setattr__(self, "aux_variables", register_sympy_attribute(self.aux_variables, "qaux"))
        # object.__setattr__(self, "position", register_sympy_attribute(self.dimension, "X"))

        object.__setattr__(self, "parameters_symbols", register_sympy_attribute(self.parameters, "p"))
        object.__setattr__(self, "parameters", register_parameter_values(self.parameters))
        object.__setattr__(
            self, "normal",
            register_sympy_attribute(["n" + str(i) for i in range(self.dimension)], "n")
        )

        object.__setattr__(self, "n_variables", self.variables.length())
        object.__setattr__(self, "n_aux_variables", self.aux_variables.length())
        object.__setattr__(self, "n_parameters", self.parameters.length())
        
    def initialize_boundary_conditions(self, mesh):
        self.boundary_conditions.initialize(
            mesh,
            self.time,
            self.position,
            self.distance,
            self.variables,
            self.aux_variables,
            self.parameters,
            self.normal,
        )
        
    def print_boundary_conditions(self):
        inputs = self.get_boundary_conditions_matrix_inputs()
        return self.boundary_conditions.get_boundary_function_matrix(*inputs)
    
    def squeeze(self, printer='jax'):
        if printer == 'jax':
            return jnp.squeeze
        elif printer == 'numpy':
            return np.squeeze
        else:
            assert False
    
    def array(self, printer='jax'):
        if printer == 'jax':
            return jnp.array
        elif printer == 'numpy':
            return np.array
        else:
            assert False
    
        
    def get_boundary_conditions_matrix_inputs(self):
        """
        Returns the inputs for the boundary conditions matrix.
        """
        return (
            self.time,
            self.position,
            self.distance,
            self.variables,
            self.aux_variables,
            self.parameters,
            self.normal,
        )
        
    def get_boundary_conditions_matrix_inputs_as_list(self):
        """
        Returns the inputs for the boundary conditions matrix where the Zstructs are converted to lists.
        """
        return [
            self.time,
            self.position.get_list(),
            self.distance,
            self.variables.get_list(),
            self.aux_variables.get_list(),
            self.parameters.get_list(),
            self.normal.get_list(),
        ]


    def _get_boundary_conditions(self, printer="jax"):
        """Returns a runtime boundary_conditions for jax arrays from the symbolic model."""
        n_boundary_functions = len(self.boundary_conditions.boundary_functions)
        bcs = []
        for i in range(n_boundary_functions):
            func_bc = lambdify(
                [
                    self.time,
                    self.position.get_list(),
                    self.distance,
                    self.variables.get_list(),
                    self.aux_variables.get_list(),
                    self.parameters.get_list(),
                    self.normal.get_list(),
                ],
                vectorize_constant_sympy_expressions(self.boundary_conditions.boundary_functions[i], self.variables, self.aux_variables),
                printer,
            )
            # the func=func part is necessary, because of https://stackoverflow.com/questions/46535577/initialising-a-list-of-lambda-functions-in-python/46535637#46535637
            f = (
                lambda time,
                position,
                distance,
                q,
                qaux,
                p,
                n,
                func=func_bc: self.squeeze(printer=printer)(
                    self.array(printer=printer)(func(time, position, distance, q, qaux, p, n)), axis=1
                )
            )
            bcs.append(f)
        return bcs

    def _get_pde(self, printer="jax"):
        """Returns a runtime model for numpy arrays from the symbolic model."""
        l_flux = [
            lambdify(
                (
                    self.variables.get_list(),
                    self.aux_variables.get_list(),
                    self.parameters.get_list(),
                ),
                vectorize_constant_sympy_expressions(
                    self.flux()[d], self.variables, self.aux_variables
                ),
                printer,
            )
            for d in range(self.dimension)
        ]
        # the f=l_flux[d] part is necessary, because of https://stackoverflow.com/questions/46535577/initialising-a-list-of-lambda-functions-in-python/46535637#46535637
        flux = [
            lambda Q, Qaux, param, f=l_flux[d]: self.squeeze(printer=printer)(
                self.array(printer=printer)(f(Q, Qaux, param)), axis=1
            )
            for d in range(self.dimension)
        ]
        l_flux_jacobian = lambdify(
            [
                self.variables.get_list(),
                self.aux_variables.get_list(),
                self.parameters.get_list(),
            ],
            self.flux_jacobian(),
            printer,
        )
        flux_jacobian = l_flux_jacobian

        l_nonconservative_matrix = [
            lambdify(
                [
                    self.variables.get_list(),
                    self.aux_variables.get_list(),
                    self.parameters.get_list(),
                ],
                vectorize_constant_sympy_expressions(
                    self.nonconservative_matrix()[d],
                    self.variables,
                    self.aux_variables,
                ),
                printer,
            )
            for d in range(self.dimension)
        ]
        nonconservative_matrix = [
            lambda Q, Qaux, param, f=l_nonconservative_matrix[d]: f(Q, Qaux, param)
            for d in range(self.dimension)
        ]

        l_quasilinear_matrix = [
            lambdify(
                [
                    self.variables.get_list(),
                    self.aux_variables.get_list(),
                    self.parameters.get_list(),
                ],
                vectorize_constant_sympy_expressions(
                    self.quasilinear_matrix()[d], self.variables, self.aux_variables
                ),
                printer,
            )
            for d in range(self.dimension)
        ]
        quasilinear_matrix = l_quasilinear_matrix

        l_eigenvalues = lambdify(
            [
                self.variables.get_list(),
                self.aux_variables.get_list(),
                self.parameters.get_list(),
                self.normal.get_list(),
            ],
            vectorize_constant_sympy_expressions(
                self.eigenvalues(), self.variables, self.aux_variables
            ),
            printer,
        )

        def eigenvalues(Q, Qaux, param, normal):
            return jnp.squeeze(
                jnp.array(l_eigenvalues(Q, Qaux, param, normal)), axis=1
            )

        l_left_eigenvectors = lambdify(
            [
                self.variables.get_list(),
                self.aux_variables.get_list(),
                self.parameters.get_list(),
                self.normal.get_list(),
            ],
            vectorize_constant_sympy_expressions(
                self.left_eigenvectors(), self.variables, self.aux_variables
            ),
            printer,
        )

        def left_eigenvectors(Q, Qaux, param, normal):
            return self.squeeze(printer=printer)(
                self.array(printer=printer)(l_left_eigenvectors(Q, Qaux, param, normal)), axis=1
            )


        l_right_eigenvectors = lambdify(
            [
                self.variables.get_list(),
                self.aux_variables.get_list(),
                self.parameters.get_list(),
                self.normal.get_list(),
            ],
            vectorize_constant_sympy_expressions(
                self.right_eigenvectors(), self.variables, self.aux_variables
            ),
            printer,
        )

        def right_eigenvectors(Q, Qaux, param, normal):
            return self.squeeze(printer=printer)(
                self.array(printer=printer)(l_right_eigenvectors(Q, Qaux, param, normal)), axis=1
            )
            
        

        l_source = lambdify(
            [
                self.variables.get_list(),
                self.aux_variables.get_list(),
                self.parameters.get_list(),
            ],
            vectorize_constant_sympy_expressions(
                self.source(), self.variables, self.aux_variables
            ),
            printer,
        )

        def source(Q, Qaux, param):
            return self.squeeze(printer=printer)(self.array(printer=printer)(l_source(Q, Qaux, param)), axis=1)


        l_source_jacobian = lambdify(
            [
                self.variables.get_list(),
                self.aux_variables.get_list(),
                self.parameters.get_list(),
            ],
            vectorize_constant_sympy_expressions(
                self.source_jacobian(), self.variables, self.aux_variables
            ),
            printer,
        )
        source_jacobian = l_source_jacobian

        l_source_implicit = lambdify(
            [
                self.variables.get_list(),
                self.aux_variables.get_list(),
                self.parameters.get_list(),
            ],
            vectorize_constant_sympy_expressions(
                self.source_implicit(), self.variables, self.aux_variables
            ),
            printer,
        )
        def source_implicit(Q, Qaux, param):
            return self.squeeze(printer=printer)(self.array(printer=printer)(l_source_implicit(Q, Qaux, param)), axis=1)
        
        l_residual = lambdify(
            [
                self.variables.get_list(),
                self.aux_variables.get_list(),
                self.parameters.get_list(),
            ],
            vectorize_constant_sympy_expressions(
                self.residual(), self.variables, self.aux_variables
            ),
            printer,
        )
        def residual(Q, Qaux, param):
            return self.squeeze(printer=printer)(self.array(printer=printer)(l_residual(Q, Qaux, param)), axis=1)


        l_interpolate_3d = lambdify(
            [
                self.position.get_list(),
                self.variables.get_list(),
                self.aux_variables.get_list(),
                self.parameters.get_list(),
            ],
            vectorize_constant_sympy_expressions(
                self.interpolate_3d(), self.variables, self.aux_variables
            ),
            printer,
        )
        def interpolate_3d(X, Q, Qaux, param):
            return self.squeeze(printer=printer)(self.array(printer=printer)(l_interpolate_3d(X, Q, Qaux, param)), axis=1)



        left_eigenvectors = None
        right_eigenvectors = None
        d = {
            "flux": flux,
            "flux_jacobian": flux_jacobian,
            "nonconservative_matrix": nonconservative_matrix,
            "quasilinear_matrix": quasilinear_matrix,
            "eigenvalues": eigenvalues,
            "left_eigenvectors": left_eigenvectors,
            "right_eigenvectors": right_eigenvectors,
            "source": source,
            "source_jacobian": source_jacobian,
            "source_implicit": source_implicit,
            "residual": residual,
            "interpolate_3d": interpolate_3d,
        }
        return SimpleNamespace(**d)

    def flux(self):
        return [Matrix(self.variables[:]) for d in range(self.dimension)]

    def nonconservative_matrix(self):
        return [zeros(self.n_variables, self.n_variables) for d in range(self.dimension)]

    def source(self):
        return zeros(self.n_variables, 1)

    def flux_jacobian(self):
        """ generated automatically unless explicitly provided """
        return [ self._simplify(
                Matrix(self.flux()[d]).jacobian(self.variables),
            ) for d in range(self.dimension) ]

    def quasilinear_matrix(self):
        """ generated automatically unless explicitly provided """
        return [ self._simplify(
                Matrix(self.flux_jacobian()[d] + self.nonconservative_matrix()[d],
            )
        ) for d in range(self.dimension) ]

    def source_jacobian(self):
        """ generated automatically unless explicitly provided """
        return self._simplify(
                Matrix(self.source()).jacobian(self.variables),
            )

    def source_implicit(self):
        return zeros(self.n_variables, 1)

    def residual(self):
        return zeros(self.n_variables, 1)
    
    def interpolate_3d(self):
        return zeros(6, 1)


    def eigenvalues(self):
        A = self.normal[0] * self.quasilinear_matrix()[0]
        for d in range(1, self.dimension):
            A += self.normal[d] * self.quasilinear_matrix()[d]
        return self._simplify(eigenvalue_dict_to_matrix(A.eigenvals()))
    
    def left_eigenvectors(self):
        return zeros(self.n_variables, self.n_variables)
    
    def right_eigenvectors(self):
        return zeros(self.n_variables, self.n_variables)
    
    def substitute_precomputed_denominator(self, expr, sym, sym_inv):
        if isinstance(expr, sympy.MatrixBase):
            return expr.applyfunc(lambda e: self.substitute_precomputed_denominator(e, sym, sym_inv))

        num, den = sympy.fraction(expr)
        if den.has(sym):
            # split into (part involving sym, part not involving sym)
            den_sym, den_rest = den.as_independent(sym, as_Add=False)
            # careful: as_independent returns (independent, dependent)
            # so we need to swap naming
            den_rest, den_sym = den_sym, den_rest

            # replace sym by sym_inv in the sym-dependent part
            den_sym_repl = den_sym.xreplace({sym: sym_inv})

            return self.substitute_precomputed_denominator(num, sym, sym_inv) * den_sym_repl / den_rest
        elif expr.args:
            return expr.func(*[self.substitute_precomputed_denominator(arg, sym, sym_inv) for arg in expr.args])
        else:
            return expr

def transform_positive_variable_intput_to_list(argument, positive, n_variables):
    out = [False for _ in range(n_variables)]
    if positive is None:
        return out
    if type(positive) == type({}):
        assert type(argument) == type(positive)
        for i, a in enumerate(argument.keys()):
            if a in positive.keys():
                out[i] = positive[a]
    if type(positive) == list:
        for i in positive:
            out[i] = True
    return out

def register_sympy_attribute(argument, string_identifier="q_", positives=None):
    if type(argument) == int:
        positive = transform_positive_variable_intput_to_list(argument, positives, argument)
        attributes = {
            string_identifier + str(i): sympy.symbols(
                string_identifier + str(i), real=True, positive=positive[i]
            )
            for i in range(argument)
        }
    elif type(argument) == type({}):
        positive = transform_positive_variable_intput_to_list(argument, positives, len(argument))
        attributes = {
            name: sympy.symbols(str(name), real=True, positive=pos) for name, pos in zip(argument.keys(), positive)
        }
    elif type(argument) == list:
        positive = transform_positive_variable_intput_to_list(argument, positives, len(argument))
        attributes = {name: sympy.symbols(str(name), real=True, positive=pos) for name, pos in zip(argument, positive)}
    elif type(argument) == Zstruct:
        d = argument.as_dict()
        register_sympy_attribute(d, string_identifier, positives)
    else:
        assert False
    return Zstruct(**attributes)


def register_parameter_symbols(parameters):
    if type(parameters) == type({}):
        for k, v in parameters.items():
            parameters[k] = sympy.symbols(str(k), real=True)
    elif type(parameters) == Zstruct:
        d = parameters.as_dict()
        register_parameter_symbols(d)
    else:
        assert False
    return register_sympy_attribute(parameters, "p_")


def eigenvalue_dict_to_matrix(eigenvalues, simplify=default_simplify):
    evs = []
    for ev, mult in eigenvalues.items():
        for i in range(mult):
            evs.append(simplify(ev))
    return Matrix(evs)
