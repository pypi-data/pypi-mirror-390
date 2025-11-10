module potential

  implicit none

  double precision, allocatable :: epsilon_(:,:)
  double precision, allocatable :: sigma_(:,:)
  double precision, allocatable :: A_(:,:)
  double precision, allocatable :: B_(:,:)
  integer :: exponent_

contains

  subroutine init(exponent, epsilon, sigma, A, B)
    integer, intent(in) :: exponent
    double precision, intent(in) :: epsilon(:,:), sigma(:,:), A(:,:), B(:,:)
    if (allocated(epsilon_).and.allocated(sigma_).and.allocated(A_).and.allocated(B_)) return
    ! only works with recent compilers...
    !allocate(exponent_, source=exponent)
    !allocate(epsilon_, source=epsilon)
    !allocate(sigma_, source=sigma)
    exponent_ = exponent
    allocate(epsilon_(size(epsilon,1),size(epsilon,2)), source=epsilon)
    allocate(sigma_(size(sigma,1),size(sigma,2)), source=sigma)
    allocate(A_(size(A,1),size(A,2)), source=A)
    allocate(B_(size(B,1),size(B,2)), source=B)
  end subroutine init
  
  subroutine compute(isp,jsp,rsq,u,w,h)
    integer,          intent(in)    :: isp, jsp
    double precision, intent(in)    :: rsq
    double precision, intent(inout) :: u, w, h
    double precision :: exp_term, der_term, der2_term, r, u_0
    r = rsq**0.5
    exp_term = exp(A_(isp,jsp) / (r-B_(isp,jsp)))
    der_term = A_(isp,jsp) / (r-B_(isp,jsp))**2
    der2_term = A_(isp,jsp) / (r-B_(isp,jsp))**3
    u_0 = epsilon_(isp,jsp) * (sigma_(isp,jsp) / r)**exponent_
    u = u_0 * exp_term
    w = (exponent_ * u_0 / rsq + u_0 / r * der_term) * exp_term
    h = (+ exponent_ * (exponent_+2) / rsq**2 &
         + exponent_ / r**3 * der_term &
         + (exponent_+1) / r**3 * der_term &
         + 1.d0 / rsq * 2 * der2_term &
         + 1.d0 / rsq * der_term**2) * u_0 * exp_term

  end subroutine compute

end module potential
