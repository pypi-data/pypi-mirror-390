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
    double precision                :: sigsq, r
    r = SQRT(rsq)
    u = 0.5d0 * epsilon_(isp,jsp) * (1.d0 - r/sigma_(isp,jsp))**2
    w = epsilon_(isp,jsp) * (1.d0 - r/sigma_(isp,jsp)) / (sigma_(isp,jsp) * r)
    h = epsilon_(isp,jsp) / (sigma_(isp,jsp) * rsq * r)
  end subroutine compute

end module potential
