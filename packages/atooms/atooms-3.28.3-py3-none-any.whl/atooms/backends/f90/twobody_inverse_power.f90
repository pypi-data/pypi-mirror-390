module potential

  implicit none

  double precision, allocatable :: epsilon_(:,:)
  double precision, allocatable :: sigma_(:,:)
  integer :: exponent_

contains

  subroutine init(exponent, epsilon, sigma)
    integer, intent(in) :: exponent
    double precision, intent(in) :: epsilon(:,:), sigma(:,:)
    if (allocated(epsilon_).and.allocated(sigma_)) return
    exponent_ = exponent
    allocate(epsilon_(size(epsilon,1),size(epsilon,2)), source=epsilon)
    allocate(sigma_(size(sigma,1),size(sigma,2)), source=sigma)
  end subroutine init
  
  subroutine compute(isp,jsp,rsq,u,w,h)
    integer,          intent(in)    :: isp, jsp
    double precision, intent(in)    :: rsq
    double precision, intent(inout) :: u, w, h
    u = epsilon_(isp,jsp) * (sigma_(isp,jsp)**2 / rsq)**(exponent_/2)
    w = exponent_ * u / rsq
    h = exponent_ * (exponent_+2) * u / (rsq**2)
  end subroutine compute

  ! subroutine compute_vector(isp,jsp,rsq,u,w,h)
  !   integer,          intent(in)    :: isp, jsp(:)
  !   double precision, intent(in)    :: rsq(:)
  !   double precision, intent(inout) :: u(:), w(:), h(:)
  !   double precision                :: eps(size(rsq)), sig2(size(rsq))
  !   integer                         :: i
  !   eps = [(epsilon_(isp, jsp(i)), i=1,size(rsq))]
  !   sig2 = [(sigma_(isp, jsp(i))**2, i=1,size(rsq))]
  !   u = eps * (sig2 / rsq)**(exponent_/2)
  !   w = exponent_ * u / rsq
  !   h = exponent_ * (exponent_+2) * u / (rsq**2)
  ! end subroutine compute_vector
  
end module potential
