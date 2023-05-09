
# Active Contraction

FEBio and opendihu use different simulation models for fiber contraction.
This document briefly describes the differences between the two programs
and the adaptations necessary to make the results comparable.

## opendihu

To simulate active fiber contraction we use the
`TransverselyIsotropicMooneyRivlinIncompressibleActive3D` material.

The strain energy function depends on the four parameters $c_1$,
$c_2$, $b$ and $d$ and is given by:

$$
\Psi_o = c_1 (\tilde{I}_1 - 3) + c_2 (\tilde{I}_2 - 3)
    + \frac{b}{d} (\tilde{\lambda}^d - 1) - b \ln(\tilde{\lambda})
$$

where $\tilde{\lambda} = \sqrt{\tilde{I}_4}$.

## FEBio

In FEBio we use the `Transversely Isotropic Mooney-Rivlin` material
to simulate active fiber contraction.

There the strain energy function depends on eight parameters
$c_1, \ldots, c_6, \lambda_m, K$ and is given by:

$$
\Psi_f = c_1(\tilde{I}_1 - 3) + c_2 (\tilde{I}_2 - 3)
    + \frac{K}{2} \ln(J)^2 + F_2(\tilde{\lambda})
$$

where $F_2(\tilde{\lambda})$ describes the contribution
from the fibers given by:

$$
F_2(\tilde{\lambda}) = \begin{cases}
    0 & \tilde{\lambda} \le 1 \\
    c_3 (e^{-c_4} (\text{Ei}(c_4 \tilde{\lambda}) %
        - \text{Ei}(c_4)) - \ln(\tilde{\lambda})) %
        & 1 \lt \tilde{\lambda} \lt \lambda_m \\
    c_5 (\tilde{\lambda} - 1) + c_6 \ln(\tilde{\lambda}) %
        & \tilde{\lambda} \ge \lambda_m %
    \end{cases}
$$

and $\text{Ei}(\cdot)$ is the exponential integral function.

The parameter $c_6$ is not specified by the user but determined
by the fact, that $\Psi$ is continuous at $\lambda_m$.

## Adaptations

For better comparison of the results from opendihu and FEBio
we want

$$
\Psi_o \overset{!}{=} \Psi_f
$$

which is achieved by setting

$$
\begin{align}
b &= c_5 = c_6 \\
\lambda_m &= 1 \\
d &= 1 \\
K &= 0
\end{align}
$$

and therefore

$$
\Psi_o = \Psi_f = c_1(\tilde{I}_1 - 3) + c_2 (\tilde{I}_2 - 3)
    + b (\tilde{\lambda} - 1) + b \ln(\tilde{\lambda})
$$
