from picos import RealVariable, SolutionFailure, Problem
import math


class BBTreeNode():
    """
    Creates and handles a BBTreeNode object that can branch and bound
    to determine the optimal result and corresponding best variable
    values.

    Constructor:
        vars (list of picos RealVariable objects): variables in the
            problem.
        constraints (list of constraints): list of problem constraints.
            ex: [z == x+y, -5*x+4*y <= 0, 6*x+2*y <= 17, x>=0, y>=0].
        objective (picos RealVariable object): variable that is being
            maximized.
        prob (picos Problem object): problem created by buildProblem
            using constraints, vars, and objective.
    """

    def __init__(self, vars = [], constraints = [], objective='', prob=None):
        """
        Initializes BBTreeNode.
        """
        self.vars = vars
        self.prob=Problem()
        self.prob.add_list_of_constraints(constraints)
        self.prob.set_objective('max', objective)
        self.best_res = -1e20
        self.best_vars = self.__copy_vars(vars)

    """
        Casts a list of picos RealVariables objects to a python list of floats.
    """
    @staticmethod
    def __copy_vars(vars):
        return list(map(lambda x: x.value, vars))

    def bbsolve(self):
        """
        Uses the branch and bound method to solve an integer program.

        Returns:
            best_res (float): value of the maximized objective function.
            bestnode_vars (list of floats): list of variables that
                create best_res.
        """
        try:
            # solves the current node
            solve = self.prob.solve(solver='cvxopt') 
            # determines if at least one real variable exists
            real_variable = next((v for v in self.vars if abs(round(v.value) - float(v.value)) > 1e-4), None)
            # update best solution
            if(not real_variable and solve.reportedValue > self.best_res + 1e-4):
                self.best_res = solve.reportedValue
                self.best_vars = self.__copy_vars(self.vars)
            # branch and bound recursively
            elif(solve.reportedValue > self.best_res + 1e-4):
                # add and backtrack less than discrete constraint
                less_than = (real_variable <= math.floor(real_variable.value))
                self.prob += less_than
                self.bbsolve()
                self.prob.remove_constraint(less_than)

                # add and backtrack greater than discrete constraint
                greater_than = (real_variable >= math.ceil(real_variable.value))
                self.prob += greater_than
                self.bbsolve()
                self.prob.remove_constraint(greater_than)

        # solution is infeasible, discard node
        except SolutionFailure:
                pass

        return self.best_res, self.best_vars
