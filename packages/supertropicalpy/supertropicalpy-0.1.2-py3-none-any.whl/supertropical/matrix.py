# src/supertropical/matrix.py
import numpy as np
import itertools
from.element import SupertropicalElement

class SupertropicalMatrix:
    """
    Represents a matrix over the supertropical algebra.
    """

    def __init__(self, data):
        """
        Initializes from a list of lists or a numpy array.
        """
        if not isinstance(data, np.ndarray):
            # Convert list of (float, int, or SupertropicalElement)
            # to a numpy array of SupertropicalElement objects
            if isinstance(data, list):
                # Get shape from nested list
                rows = len(data)
                cols = len(data[0]) if rows > 0 else 0
                object_array = np.empty((rows, cols), dtype=object)
                
                for i in range(rows):
                    for j in range(cols):
                        val = data[i][j]
                        if not isinstance(val, SupertropicalElement):
                            val = SupertropicalElement(val)
                        object_array[i, j] = val
                self.data = object_array
            else:
                # If it's already a numpy array
                self.data = np.array(data, dtype=object)
        else:
            self.data = data
            
        self.shape = self.data.shape

    def __repr__(self):
        """String representation showing matrix in readable 2D array format."""
        rows = []
        for i in range(self.shape[0]):
            row = []
            for j in range(self.shape[1]):
                elem = self.data[i, j]
                # Format: number with 'v' for ghost, plain number for tangible
                if elem.is_ghost:
                    row.append(f"{elem.value}v")
                else:
                    row.append(f"{elem.value}")
            rows.append(row)
        
        # Calculate column widths for alignment
        col_widths = []
        for j in range(self.shape[1]):
            max_width = max(len(rows[i][j]) for i in range(self.shape[0]))
            col_widths.append(max_width)
        
        # Build the string with proper alignment
        lines = []
        for row in rows:
            formatted_row = [val.rjust(col_widths[j]) for j, val in enumerate(row)]
            lines.append("  [" + "  ".join(formatted_row) + "]")
        
        return "[\n" + "\n".join(lines) + "\n]"

    def __getitem__(self, key):
        return self.data[key]

    def __mul__(self, other):
        """
        Matrix multiplication or scalar multiplication.
        
        - If other is SupertropicalMatrix: performs supertropical matrix multiplication
          C_ij = ⊕_k (A_ik ⊙ B_kj)
        - If other is scalar (SupertropicalElement, int, float): multiplies each element
        """
        if isinstance(other, SupertropicalMatrix):
            # Matrix multiplication
            if self.shape[1] != other.shape[0]:
                raise ValueError(f"Matrix dimensions do not match: {self.shape} * {other.shape}.")

            new_shape = (self.shape[0], other.shape[1])
            result_matrix = np.empty(new_shape, dtype=object)

            for i in range(new_shape[0]):
                for j in range(new_shape[1]):
                    # Initialize C_ij with the zero element (-inf)
                    sum_val = SupertropicalElement(-np.inf)
                    
                    for k in range(self.shape[1]):
                        # Calculate A_ik ⊙ B_kj (using element multiplication)
                        prod = self[i, k] * other[k, j]
                        # Perform C_ij = C_ij ⊕ (A_ik ⊙ B_kj) (using element addition)
                        sum_val = sum_val + prod
                    
                    result_matrix[i, j] = sum_val

            return SupertropicalMatrix(result_matrix)
            
        elif isinstance(other, SupertropicalElement):
            # Scalar multiplication
            result = np.empty(self.shape, dtype=object)
            for i in range(self.shape[0]):
                for j in range(self.shape[1]):
                    result[i, j] = self[i, j] * other
            return SupertropicalMatrix(result)
            
        elif isinstance(other, (int, float)):
            return self * SupertropicalElement(other)
            
        else:
            raise TypeError("Can only multiply by SupertropicalMatrix, SupertropicalElement or scalar.")

    def __rmul__(self, other):
        if isinstance(other, (int, float, SupertropicalElement)):
            return self.__mul__(other)
        else:
            raise TypeError("Left multiplication only supported for scalars.")
    
    # --- Linear Algebra Methods ---

    def get_minor(self, i: int, j: int):
        """
        Returns the minor matrix by removing row i and column j.
        
        Args:
            i (int): Row index to remove.
            j (int): Column index to remove.

        Returns:
            SupertropicalMatrix: The (n-1)x(n-1) minor matrix.
        """
        data_without_row = np.delete(self.data, i, axis=0)
        data_without_col = np.delete(data_without_row, j, axis=1)
        return SupertropicalMatrix(data_without_col)

    def permanent(self):
        """
        Calculates the supertropical permanent of the matrix.
        
        The permanent is defined as:
        per(A) = $\oplus_{\pi \in S_n} \odot_{i=1}^n a_{i, \pi(i)}$
        
        This is used as the supertropical equivalent of the determinant. [5, 19]

        Returns:
            SupertropicalElement: The permanent of the matrix.
        """
        if self.shape[0] != self.shape[1]:
            raise ValueError("Permanent is only defined for square matrices.")
            
        n = self.shape[0]
        if n == 0:
            return SupertropicalElement(0.0) # Multiplicative identity

        # Use itertools.permutations to sum over all permutations
        perms = itertools.permutations(range(n))
        
        # Start with the additive identity (-inf)
        total_sum = SupertropicalElement(-np.inf)

        for perm in perms:
            # Start with the multiplicative identity (0.0)
            term_prod = SupertropicalElement(0.0)
            for i in range(n):
                term_prod = term_prod * self[i, perm[i]]
            
            # Add the product of this permutation to the total sum
            total_sum = total_sum + term_prod
            
        return total_sum

    def adjoint(self):
        """
        Calculates the supertropical adjoint matrix.
        
        The adjoint is the transpose of the cofactor matrix.
        The (i, j)-th entry of the adjoint is the (j, i)-th cofactor.
        The (j, i)-th cofactor is the permanent of the minor M_ji. [5, 11]

        Returns:
            SupertropicalMatrix: The adjoint matrix of self.
        """
        if self.shape[0] != self.shape[1]:
            raise ValueError("Adjoint is only defined for square matrices.")

        n = self.shape[0]
        adj_matrix_data = np.empty(self.shape, dtype=object)
        
        for i in range(n):
            for j in range(n):
                # Adjoint(i, j) = Cofactor(j, i) = permanent(Minor(j, i))
                minor = self.get_minor(j, i) 
                adj_matrix_data[i, j] = minor.permanent()
                
        return SupertropicalMatrix(adj_matrix_data)

    def solve(self, b: 'SupertropicalMatrix'):
        """
        Solves the supertropical linear system A * x = b using
        a version of Cramer's Rule. 

        The solution is calculated using the adjoint matrix:
        x = adj(A) * b * (per(A))^{-1}
        
        This provides the unique maximal tangible solution to the
        system $Ax \mid_{gs}= b$. 

        Args:
            b (SupertropicalMatrix): The (n, 1) vector on the 
                                     right-hand side.

        Returns:
            SupertropicalMatrix: The (n, 1) solution vector x.
            
        Raises:
            ValueError: If the matrix is singular (permanent is ghost)
                        or dimensions are incorrect.
        """
        if self.shape[0] != self.shape[1]:
            raise ValueError("System must be square (n x n) to solve.")
        # b must be a column vector with same number of rows as A, allow (n,1) or (n,)
        if b.shape != (self.shape[0], 1) and b.shape != (self.shape[0],):
            raise ValueError(f"Dimension mismatch. A is {self.shape} but b is {b.shape}.")

        # 1. Calculate the permanent (supertropical determinant)
        per_A = self.permanent()
        
        # A matrix is nonsingular if its permanent is tangible [7, 19]
        if per_A.is_ghost:
            raise ValueError("Matrix is singular (permanent is ghost). Cannot solve.")

        # 2. Calculate the inverse of the permanent
        # (1/a) in supertropical algebra is -a (classical)
        per_A_inv = SupertropicalElement(-per_A.value, is_ghost=per_A.is_ghost)

        # 3. Calculate the tangible adjoint matrix 
        adj_A = self.adjoint()
        
        # 4. Calculate solution x = adj(A) * b * per(A)^-1
        # Reshape b if needed to ensure column vector
        if len(b.shape) == 1:
            b_reshaped = SupertropicalMatrix(b.data.reshape(-1, 1))
        else:
            b_reshaped = b
            
        x = (adj_A * b_reshaped) * per_A_inv
        
        return x
    
    def transpose(self):
        """
        Returns the transpose of the matrix A^T.
        
        For matrix A, transpose A^T is defined as [A^T]_ij = A_ji.
        
        Returns:
            SupertropicalMatrix: The transposed matrix
        """
        transposed_data = np.empty((self.shape[1], self.shape[0]), dtype=object)
        
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                transposed_data[j, i] = self.data[i, j]
        
        return SupertropicalMatrix(transposed_data)
    
    def __pow__(self, k):
        """
        Matrix power: A^k = A * A * ... * A (k times).
        
        Uses supertropical matrix multiplication.
        
        Args:
            k (int): Non-negative integer exponent
            
        Returns:
            SupertropicalMatrix: The result of A^k
        """
        if not isinstance(k, int) or k < 0:
            raise ValueError("Exponent must be a non-negative integer")
        
        if self.shape[0] != self.shape[1]:
            raise ValueError("Matrix must be square for exponentiation")
        
        if k == 0:
            # A^0 = I (identity matrix)
            return SupertropicalMatrix.identity(self.shape[0])
        
        result = self
        for _ in range(k - 1):
            result = result * self
        
        return result
    
    @staticmethod
    def identity(n):
        """
        Creates an n×n identity matrix I.
        
        Identity matrix is defined as:
        [I]_ij = { 0   if i = j
                  { ε   if i ≠ j
        
        where ε = -∞ (represented as ghost element with value -inf).
        
        Args:
            n (int): Size of the square identity matrix
            
        Returns:
            SupertropicalMatrix: n×n identity matrix
        """
        import math
        identity_data = np.empty((n, n), dtype=object)
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    identity_data[i, j] = SupertropicalElement(0, is_ghost=False)
                else:
                    identity_data[i, j] = SupertropicalElement(-math.inf, is_ghost=True)
        
        return SupertropicalMatrix(identity_data)
    
    @staticmethod
    def pseudo_zero(n):
        """
        Creates an n×n pseudo-zero matrix Z_G.
        
        Pseudo-zero matrix is defined as:
        [Z_G]_ij = { ε        if i = j
                   { ε or aν  if i ≠ j
        
        where ε = -∞ and aν ∈ G_0 (any ghost element).
        
        For simplicity, we use ε = -∞ as ghost for all entries.
        
        Args:
            n (int): Size of the square pseudo-zero matrix
            
        Returns:
            SupertropicalMatrix: n×n pseudo-zero matrix
        """
        import math
        pseudo_zero_data = np.empty((n, n), dtype=object)
        
        for i in range(n):
            for j in range(n):
                # All entries are ε (ghost -infinity)
                pseudo_zero_data[i, j] = SupertropicalElement(-math.inf, is_ghost=True)
        
        return SupertropicalMatrix(pseudo_zero_data)
    
    def pseudo_inverse(self):
        """
        Calculates the pseudo-inverse A^♯ of the matrix.
        
        Pseudo-inverse is defined as:
        - If |A| ∈ T: A^♯ = (1_R / |A|) ⊗ adj(A)
        - If |A| ∈ G_0 with |A| ≠ ε: A^♯ = (1_R / |A|)^ν ⊗ adj(A)
        
        where 1_R is the multiplicative identity and |A| is the permanent.
        
        Returns:
            SupertropicalMatrix: The pseudo-inverse matrix
            
        Raises:
            ValueError: If matrix is not square or permanent is epsilon
        """
        if self.shape[0] != self.shape[1]:
            raise ValueError("Matrix must be square for pseudo-inverse")
        
        # Calculate permanent
        perm = self.permanent()
        
        # Check if permanent is epsilon (not invertible)
        if perm.value == -np.inf:
            raise ValueError("Matrix permanent is epsilon, pseudo-inverse undefined")
        
        # Calculate adjoint
        adj_A = self.adjoint()
        
        # Calculate (1/|A|) or (1/|A|)^ν
        # In supertropical: 1/a = -a (classical negation)
        inv_perm_value = -perm.value
        inv_perm = SupertropicalElement(inv_perm_value, is_ghost=perm.is_ghost)
        
        # Pseudo-inverse = inv_perm ⊗ adj(A)
        return adj_A * inv_perm