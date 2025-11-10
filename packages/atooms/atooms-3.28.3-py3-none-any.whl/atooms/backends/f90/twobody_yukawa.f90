module potential

  implicit none

  integer, private, parameter :: dp = selected_real_kind(12)
  real(dp), allocatable :: epsilon_(:,:)
  real(dp), allocatable :: kappa_(:,:)
  real(dp), allocatable :: sigma_(:,:)

contains

  subroutine init(epsilon, kappa, sigma)
    double precision, intent(in) :: epsilon(:,:), kappa(:,:), sigma(:,:)
    if (allocated(epsilon_).and.allocated(sigma_).and.allocated(kappa_)) return
    allocate(epsilon_(size(epsilon,1),size(epsilon,2)), source=epsilon)
    allocate(kappa_(size(kappa,1),size(kappa,2)), source=kappa)
    allocate(sigma_(size(sigma,1),size(sigma,2)), source=sigma)
  end subroutine init
  
  subroutine compute(isp,jsp,rsq,u,w,h)
    integer,          intent(in)    :: isp, jsp
    double precision, intent(in)    :: rsq
    double precision, intent(inout) :: u, w, h
    double precision                :: sigsq, r
    r = SQRT(rsq)
    u = epsilon_(isp,jsp) / (kappa_(isp,jsp) * r) * EXP(kappa_(isp,jsp) * (sigma_(isp,jsp) - r))
    w = (1 / r) * (1 / r + kappa_(isp,jsp)) * u
    h = u / r**4 + (2 / r**2 + kappa_(isp,jsp) / r) * w
  end subroutine compute

end module potential
