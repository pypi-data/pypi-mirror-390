module potential

  implicit none

  integer, private, parameter :: dp = selected_real_kind(12)
  real(dp), allocatable :: epsilon_(:,:)
  real(dp), allocatable :: sigma_(:,:)

contains

  subroutine init(epsilon, sigma)
    double precision, intent(in) :: epsilon(:,:), sigma(:,:)
    if (allocated(epsilon_).and.allocated(sigma_)) return
    allocate(epsilon_(size(epsilon,1),size(epsilon,2)), source=epsilon)
    allocate(sigma_(size(sigma,1),size(sigma,2)), source=sigma)
  end subroutine init
  
  subroutine compute(isp,jsp,rsq,u,w,h)
    integer,          intent(in)    :: isp, jsp
    double precision, intent(in)    :: rsq
    double precision, intent(inout) :: u, w, h
    double precision                :: sigsq
    sigsq = sigma_(isp,jsp)**2
    u = 4 * epsilon_(isp,jsp) * ((sigsq/rsq)**6 - (sigsq/rsq)**3)
    w = 24 * epsilon_(isp,jsp) * (2*(sigsq/rsq)**6 - (sigsq/rsq)**3) / rsq
    h = 96 * epsilon_(isp,jsp) * (7*(sigsq/rsq)**6 - 2*(sigsq/rsq)**3) / rsq**2
  end subroutine compute

end module potential
