module bond_potential

  implicit none

  double precision, allocatable :: epsilon_(:,:)
  double precision, allocatable :: sigma_(:,:)
  double precision, allocatable :: R0_(:,:)
  double precision, allocatable :: K_(:,:)

contains

  subroutine init(exponent, epsilon, sigma)
    integer, intent(in) :: exponent
    double precision, intent(in) :: epsilon(:,:), sigma(:,:)
    if (allocated(epsilon_).and.allocated(sigma_)) return
    exponent_ = exponent
    allocate(epsilon_(size(epsilon,1),size(epsilon,2)), source=epsilon)
    allocate(sigma_(size(sigma,1),size(sigma,2)), source=sigma)
  end subroutine init
  
  subroutine compute_bond(isp,jsp,rsq,u,w,h)
    integer,          intent(in)    :: isp, jsp
    double precision, intent(in)    :: rsq
    double precision, intent(inout) :: u, w, h
    u = - K_(isp,jsp) * R0_(isp,jsp)**2 * log(1 - (rsq / sigma_(isp,jsp)**2))
    w = - K_(isp,jsp) * R0_(isp,jsp)**2 / sigma_(isp,jsp)**2 / (1 - (rsq / sigma_(isp,jsp)**2)
    h = 0.0
    if (rsq < 2**(1./6)) then
       sigsq = sigma_(isp,jsp)**2
       u = u + 4 * epsilon_(isp,jsp) * ((sigsq/rsq)**6 - (sigsq/rsq)**3) + epsilon_(isp,jsp)
       w = w + 24 * epsilon_(isp,jsp) * (2*(sigsq/rsq)**6 - (sigsq/rsq)**3) / rsq
       h = h + 96 * epsilon_(isp,jsp) * (7*(sigsq/rsq)**6 - 2*(sigsq/rsq)**3) / rsq**2
    end if
  end subroutine compute_bond
  
end module bond_potential
